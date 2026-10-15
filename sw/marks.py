"""Marks as gutter icons. Pure functions, no Sublime API."""

import math
import re

from .config import DEFAULT_MARK
from .spec import matches


BAD_LINE = 'Write a line as "file:line" or {"sight": index, "line": line}, not %r.'


def line_y(sight, line, lh):
    return sight.code_item.y + (line - sight.begin) * lh


def resolve_target(sights, target):
    """target: "file:line" or {"sight": index, "line": line}. Returns (sight, line)."""
    try:
        if isinstance(target, dict):
            index, line = int(target["sight"]), int(target["line"])
        else:
            name, _, line = str(target).rpartition(":")
            line = int(line)
    except (KeyError, TypeError, ValueError):
        raise ValueError(BAD_LINE % (target,)) from None
    if isinstance(target, dict):
        return sight_target(sights, index, line)
    inside = [i for i, sight in enumerate(sights)
              if matches(sight, name) and sight.begin <= line <= sight.end]
    if not inside:
        raise ValueError("No sight shows %s; a mark must be inside a sight's range." % target)
    if len(inside) > 1:
        raise ValueError('%s is in sights %s; give {"sight": index, "line": %d} instead'
                         % (target, ", ".join(map(str, inside)), line))
    return inside[0], line


def sight_target(sights, index, line):
    if not 0 <= index < len(sights):
        raise ValueError("No sight %d; the sights are 0 to %d." % (index, len(sights) - 1))
    sight = sights[index]
    if not sight.begin <= line <= sight.end:
        raise ValueError("Line %d is outside sight %d (%s)." % (line, index, sight.spec))
    return index, line


def icon_for(mark):
    mark = str(mark)
    if len(mark) == 1 and mark in "123456789":
        return "digit_" + mark
    if len(mark) == 1 and mark.isascii() and mark.isalpha():
        return "letter_" + mark.lower()
    raise ValueError("A mark is a digit 1-9 or a letter A-Z, not %r" % mark)


JUMP_COLOURS = ("", "_red", "_yellow", "_purple", "_brown")  # see tools/draw_icons.py


def jump(sights, mark, colour=""):
    """A jump of control: both arrows bend towards the other end, in reader order, both in the
    jump's colour."""
    sender = resolve_target(sights, mark["from"])
    receiver = resolve_target(sights, mark["to"])
    down = sender <= receiver
    return [{"sight": sender[0], "line": sender[1], "icon": ("pass_down" if down else "pass_up") + colour},
            {"sight": receiver[0], "line": receiver[1],
             "icon": ("take_above" if down else "take_below") + colour}]


def resolve_marks(sights, marks):
    """marks: {"from": target, "to": target} for a jump, or {"at": target, "mark": "1"}."""
    resolved = []
    for mark in marks:
        if "from" in mark or "to" in mark:
            if not ("from" in mark and "to" in mark):
                raise ValueError('A jump needs both ends: {"from": line, "to": line}.')
            jumps = sum(1 for m in resolved if m["icon"].startswith("pass_"))
            resolved += jump(sights, mark, JUMP_COLOURS[jumps % len(JUMP_COLOURS)])
        else:
            if "at" not in mark:
                raise ValueError('A mark is {"at": line, "mark": "1"} or {"from": line, '
                                 '"to": line}, not %r.' % (mark,))
            index, line = resolve_target(sights, mark["at"])
            icon = icon_for(mark.get("mark", DEFAULT_MARK))
            resolved.append({"sight": index, "line": line, "icon": icon})
    return resolved


def visible_lines(sights, offset, height, lh):
    """(sight, line) of the first and the last line wholly on screen, or None, None.
    Line 0 is the sight's header, which sorts before its code."""
    seen = []
    for index, sight in enumerate(sights):
        if offset - 0.5 <= sight.header_item.y <= offset + height - lh + 0.5:
            seen.append((index, 0))
        y0 = sight.code_item.y
        lo = max(sight.begin, sight.begin + math.ceil((offset - y0) / lh - 0.01))
        hi = min(sight.end, sight.begin + math.floor((offset + height - lh - y0) / lh + 0.01))
        if lo <= hi:
            seen += [(index, lo), (index, hi)]
    return (seen[0], seen[-1]) if seen else (None, None)


def gutter_icons(indicators, first, last):
    """{(sight, line): icon} for the screen: a line's first mark (its second stands on the strip,
    see strip_icons). An eye on the first or last line, looking up or down, stands for marks off
    screen in that direction and replaces that line's own icon."""
    if first is None:
        return {}
    keys = [((m["sight"], m["line"]), m["icon"]) for m in indicators]
    icons = {}
    for key, icon in keys:
        if first <= key <= last:
            icons.setdefault(key, icon)
    if any(key < first for key, _ in keys):
        icons[first] = "eye_up"
    if any(key > last for key, _ in keys):
        icons[last] = "eye_down"
    return icons


def strip_icons(sights, indicators, lh):
    """{strip line: [icon]}: the second mark of a line, whose first stands in the gutter; never
    more than two on a line (Jakub). A strip line counts lines from the first sight's code start,
    which every sight's code start is a whole number of lines from (see plan.stack)."""
    first, seen, lines = sights[0].code_item.y, set(), {}
    for m in indicators:
        key = (m["sight"], m["line"])
        if key in seen:
            y = line_y(sights[m["sight"]], m["line"], lh) - first
            lines.setdefault(int(round(y / lh)), []).append(m["icon"])
        seen.add(key)
    return lines


CODE_TALK = re.compile(r"`[^`\n]+`|\w+\.\w+:\d+|\b(?:lines?|lini[aei]|linii)\s+\d+", re.I)


def speaks_of_code(text):
    """The message names code: a `marked name`, file:line, or a line number (line 12, linia 12)."""
    return bool(CODE_TALK.search(text))
