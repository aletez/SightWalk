"""Marks as gutter icons. Pure functions, no Sublime API."""

import math

from .config import DEFAULT_MARK
from .spec import matches


BAD_LINE = 'Write a line as "file:line" or {"pane": index, "line": line}, not %r.'


def line_y(segment, line, lh):
    return segment.code_item.y + (line - segment.begin) * lh


def resolve_target(segments, target):
    """target: "file:line" or {"pane": index, "line": line}. Returns (pane, line)."""
    try:
        if isinstance(target, dict):
            index, line = int(target["pane"]), int(target["line"])
        else:
            name, _, line = str(target).rpartition(":")
            line = int(line)
    except (KeyError, TypeError, ValueError):
        raise ValueError(BAD_LINE % (target,)) from None
    if isinstance(target, dict):
        return pane_target(segments, index, line)
    inside = [i for i, seg in enumerate(segments)
              if matches(seg, name) and seg.begin <= line <= seg.end]
    if not inside:
        raise ValueError("No pane shows %s; a mark must be inside a pane's range." % target)
    if len(inside) > 1:
        raise ValueError('%s is in panes %s; give {"pane": index, "line": %d} instead'
                         % (target, ", ".join(map(str, inside)), line))
    return inside[0], line


def pane_target(segments, index, line):
    if not 0 <= index < len(segments):
        raise ValueError("No pane %d; the panes are 0 to %d." % (index, len(segments) - 1))
    seg = segments[index]
    if not seg.begin <= line <= seg.end:
        raise ValueError("Line %d is outside pane %d (%s)." % (line, index, seg.spec))
    return index, line


def icon_for(mark):
    mark = str(mark)
    if len(mark) == 1 and mark in "123456789":
        return "digit_" + mark
    if len(mark) == 1 and mark.isascii() and mark.isalpha():
        return "letter_" + mark.lower()
    raise ValueError("A mark is a digit 1-9 or a letter A-Z, not %r" % mark)


def jump(segments, mark):
    """A jump of control: both arrows bend towards the other end, in reader order."""
    sender = resolve_target(segments, mark["from"])
    receiver = resolve_target(segments, mark["to"])
    down = sender <= receiver
    return [{"seg": sender[0], "line": sender[1], "icon": "pass_down" if down else "pass_up"},
            {"seg": receiver[0], "line": receiver[1],
             "icon": "take_above" if down else "take_below"}]


def resolve_marks(segments, marks):
    """marks: {"from": target, "to": target} for a jump, or {"at": target, "mark": "1"}."""
    resolved = []
    for mark in marks:
        if "from" in mark or "to" in mark:
            if not ("from" in mark and "to" in mark):
                raise ValueError('A jump needs both ends: {"from": line, "to": line}.')
            resolved += jump(segments, mark)
        else:
            if "at" not in mark:
                raise ValueError('A mark is {"at": line, "mark": "1"} or {"from": line, '
                                 '"to": line}, not %r.' % (mark,))
            index, line = resolve_target(segments, mark["at"])
            icon = icon_for(mark.get("mark", DEFAULT_MARK))
            resolved.append({"seg": index, "line": line, "icon": icon})
    return resolved


def visible_lines(segments, offset, height, lh):
    """(pane, line) of the first and the last line wholly on screen, or None, None.
    Line 0 is the pane's header, which sorts before its code."""
    seen = []
    for index, seg in enumerate(segments):
        if offset - 0.5 <= seg.header_item.y <= offset + height - lh + 0.5:
            seen.append((index, 0))
        y0 = seg.code_item.y
        lo = max(seg.begin, seg.begin + math.ceil((offset - y0) / lh - 0.01))
        hi = min(seg.end, seg.begin + math.floor((offset + height - lh - y0) / lh + 0.01))
        if lo <= hi:
            seen += [(index, lo), (index, hi)]
    return (seen[0], seen[-1]) if seen else (None, None)


def gutter_icons(indicators, first, last):
    """{(pane, line): icon} for the screen. An eye on the first or last line, looking up or down,
    stands for marks off screen in that direction and replaces that line's own icon."""
    if first is None:
        return {}
    keys = [((m["seg"], m["line"]), m["icon"]) for m in indicators]
    icons = {key: icon for key, icon in keys if first <= key <= last}
    if any(key < first for key, _ in keys):
        icons[first] = "eye_up"
    if any(key > last for key, _ in keys):
        icons[last] = "eye_down"
    return icons
