"""Marks as gutter icons. Pure functions, no Sublime API."""

import math
import re

from .config import DEFAULT_MARK
from .spec import matches, sight_index, sight_name


BAD_LINE = ('Write a line as "file:line" or {"sight": index or name, "line": line}, such as '
            '{"sight": "(c)", "line": 12}, not %r.')


def line_y(sight, line, lh):
    return sight.code_item.y + sight.code_item.lead + (line - sight.begin) * lh


def resolve_target(sights, target):
    """target: "file:line" or {"sight": index, "line": line}. Returns (sight, line)."""
    try:
        if isinstance(target, dict):
            index, line = sight_number(target["sight"]), int(target["line"])
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


def sight_number(sight):
    """A sight given by its index or its name ("(c)", "c")."""
    index = sight_index(sight) if isinstance(sight, str) and not sight.isdigit() else None
    return int(sight) if index is None else index


def sight_target(sights, index, line):
    if not 0 <= index < len(sights):
        raise ValueError("No sight %d; the sights are 0 to %d (%s to %s)." % (
            index, len(sights) - 1, sight_name(0), sight_name(len(sights) - 1)))
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
# The icons' own colours (tools/draw_icons.py): a marked line's outline takes its icon's (Jakub).
ICON_COLOURS = {"digit": "#C77A0E", "letter": "#2C6ED5", "green": "#23894E", "red": "#C8372D",
                "yellow": "#E3B505", "purple": "#7B3FB5", "brown": "#8A5A2B"}


def icon_colour(icon):
    """The ICON_COLOURS key of an icon: digit_3 → digit, pass_up_red → red, pass_up → green."""
    kind = icon.split("_")[0]
    if kind in ("digit", "letter"):
        return kind
    last = icon.split("_")[-1]
    return last if last in ICON_COLOURS else "green"


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
        y0 = sight.code_item.y + sight.code_item.lead
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


CODE_TALK = re.compile(r"[\u2061-\u2064]|`[^`\n]+`|\w+\.\w+:\d+|\b(?:lines?|lini[aei]|linii)\s+\d+", re.I)


def speaks_of_code(text):
    """The message names code: a `marked name`, file:line, or a line number (line 12, linia 12)."""
    return bool(CODE_TALK.search(text))


REF_SCOPES = {"digit": "region.orangish", "letter": "region.bluish"}
# The jumps' frames, as their arrows: green, red, yellow, purple, brown (no scheme names a brown
# region, so it takes the text's colour).
JUMP_SCOPES = ("region.greenish", "region.redish", "region.yellowish", "region.purplish",
               "sight_walk.brown")


SIGHT_REF = re.compile(r"\([a-z]\d*\)")


def sight_refs(text, count):
    """[(start, end)]: the sights' names in text, "(c)", of the count sights in the trip."""
    return [m.span() for m in SIGHT_REF.finditer(text)
            if (sight_index(m.group(0)) or 0) < count and sight_index(m.group(0)) is not None]


# The guide's names: tags it writes, invisible operators the bench shows (Jakub, 2026-10-15).
TAGS = {"func": "\u2061", "class": "\u2062", "var": "\u2063", "str": "\u2064"}
MARK_TAGS = ("icon", "jump")  # the marks, placed by the answer itself (Jakub, 2026-10-17)
INVISIBLE = re.compile("[\u2061-\u2064]")
TAG = re.compile(r"<(/?)([a-z]+)(?:\s[^<>\n]*)?>")
OLD_MARKUP = re.compile(r"`|\*\*")


def untag(text):
    """The guide's text with <func>name</func> and the like turned into invisible operators
    around the name; <icon> and <jump> stay for read_marks. ValueError says what is wrong."""
    if OLD_MARKUP.search(text):
        raise ValueError("Mark names with tags, not backticks or asterisks: <func>run</func>, "
                         "<class>Reader</class>, <var>token</var>, <str>sight_walk_setup</str>.")
    unknown = sorted(set(m.group(2) for m in TAG.finditer(text)) - set(TAGS) - set(MARK_TAGS))
    if unknown:
        raise ValueError("Unknown tags: %s; the tags are %s." % (
            ", ".join(unknown), ", ".join(tuple(TAGS) + MARK_TAGS)))
    out = re.sub(r"<(func|class|var|str)>([^<>\n]+)</\1>",
                 lambda m: TAGS[m.group(1)] + m.group(2) + TAGS[m.group(1)], text)
    left = [m.group(0) for m in TAG.finditer(out) if m.group(2) not in MARK_TAGS]
    if left:
        raise ValueError("A tag is not closed on its line, or holds another: %s" % left[0])
    return out


ICON_TAG = r'<icon at="([^"<>]+)">([^<>\n]+)</icon>'
JUMP_TAG = r'<jump from="([^"<>]+)" to="([^"<>]+)">([^<>\n]+)</jump>'
MARK_TAG = re.compile(ICON_TAG + "|" + JUMP_TAG)
MARK_FORM = ('<icon at="(c):34">1</icon> for a line (a sight\'s name and a file line; a digit '
             '1-9 or a capital A-Z), <jump from="(a):33" to="(b):41">the call</jump> for a jump '
             'of control (the words framed in its colour)')


def place(text):
    """{"sight": "(c)", "line": 34} from "(c):34"."""
    sight, _, line = text.rpartition(":")
    if not sight or not line.strip().isdigit():
        raise ValueError("%r is no place: write a sight's name and a file line, \"(c):34\"."
                         % text)
    return {"sight": sight.strip(), "line": int(line)}


def read_marks(text):
    """(text without <icon> and <jump>, marks for resolve_marks, frames): frames are
    (start, end, kind) in the text returned, kind "icon" or the jump's index among the jumps
    (Jakub: the answer places its own marks, so where they stand is kept with it)."""
    out, found, frames, jumps, last = [], [], [], 0, 0
    for match in MARK_TAG.finditer(text):
        out.append(text[last:match.start()])
        start = sum(len(part) for part in out)
        if match.group(1) is not None:
            found.append({"at": place(match.group(1)), "mark": match.group(2).strip()})
            words, kind = match.group(2), "icon"
        else:
            found.append({"from": place(match.group(3)), "to": place(match.group(4))})
            words, kind, jumps = match.group(5), jumps, jumps + 1
        out.append(words)
        frames.append((start, start + len(words), kind))
        last = match.end()
    out = "".join(out) + text[last:]
    left = [m.group(0) for m in TAG.finditer(out) if m.group(2) in MARK_TAGS]
    if left:
        raise ValueError("Write marks as %s; not %s." % (MARK_FORM, left[0]))
    return out, found, frames


def frame_scopes(frames, text):
    """The scope each frame is drawn in: an icon's by its kind, digits orange, letters blue; a
    jump's by its colour, as its arrows (see JUMP_COLOURS)."""
    scopes = []
    for start, end, kind in frames:
        if kind == "icon":
            scopes.append(REF_SCOPES["digit" if text[start:end].strip().isdigit() else "letter"])
        else:
            scopes.append(JUMP_SCOPES[kind % len(JUMP_SCOPES)])
    return scopes


def clean(text):
    """Text without the invisible operators: what leaves the bench by copying."""
    return INVISIBLE.sub("", text)


# Line numbers the guide may not write: the user reads lines by their icons (Jakub, 2026-10-15).
LINE_REF = re.compile(
    r"\b(?:lines?|lini[aeię]|linii|liniach|linijk[aię]|l\.)\s*\d+(?:\s*[-–]\s*\d+)?"
    r"|[\w/]+\.\w+:\d+(?:-\d+)?|(?<![\w)⁡-⁤])\(\s*\d{2,}(?:\s*[-–]\s*\d+)?\s*\)", re.I)


def line_refs(text):
    """The line numbers in text: "linia 33", "(l. 42)", "line 12", "setup.py:32-38", "(35)"."""
    return [m.group(0) for m in LINE_REF.finditer(text)]
