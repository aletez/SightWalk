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
        if "places" in mark:  # a frame without an icon: its places checked, nothing drawn
            for text in mark["places"].split():
                index, first, last = parse_place(text)
                for line in {first[0], last[0]}:
                    resolve_target(sights, {"sight": sight_name(index), "line": line})
            continue
        if mark.get("map"):  # a jump's arrow on the Map only: checked, nothing in the gutter
            for end in ("from", "to"):
                resolve_target(sights, mark[end])
            continue
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
HERE_SCOPE = "sight_walk.link"  # a place without an icon: framed in the text's colour
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
INVISIBLE = re.compile("[\u2061-\u2064]")
TAG = re.compile(r"<(/?)([a-z_]+)(?:\s[^<>\n]*)?>")
OLD_MARKUP = re.compile(r"`|\*\*")


def untag(text):
    """The guide's text with <func>name</func> and the like turned into invisible operators
    around the name; <here> and its sugar stay for read_marks. ValueError says what is wrong."""
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


# One markup for both sides of the bench (Jakub, 2026-10-20): <here at="places"> frames words
# about places; icon="1" (one sign, or one per place) gives each place's first line an icon;
# jump="calls" (two places, source then target) makes them a jump of that transition type.
# <calls at="A B">…</calls> is sugar for <here at="A B" jump="calls">…</here>, and so for every
# type; empty, it only draws the arrow on the Map.
from .ontology import TRIP_TYPES  # noqa: E402

MARK_TAGS = ("here",) + TRIP_TYPES
MARK_TAG = re.compile(r'<(%s)((?:\s+[a-z]+="[^"<>]*")*)\s*>([^<>\n]*)</\1>' % "|".join(MARK_TAGS))
ATTRIBUTE = re.compile(r'([a-z]+)="([^"<>]*)"')
MARK_FORM = ('<here at="(c):34" icon="1">this check</here> for a line with its icon (a sight\'s '
             'name and a file line; a digit 1-9 or a capital A-Z), <here at="(c):34:12-16">this '
             'name</here> for a place without an icon, <calls at="(a):33 (b):41">calls</calls> '
             'for a jump (or returns, leads_to, unblocks, passes_data, comparable)')


def mark_attributes(tag, attributes):
    """{at, icon, jump} of a mark tag; the sugar's name becomes its jump."""
    found = dict(ATTRIBUTE.findall(attributes))
    unknown = set(found) - {"at", "icon"} - ({"jump"} if tag == "here" else set())
    if unknown or "at" not in found:
        raise ValueError("A mark is %s; not <%s%s>." % (MARK_FORM, tag, attributes))
    if tag != "here":
        found["jump"] = tag
    return found


def tag_marks(found):
    """The marks one tag gives: a jump, icons on its places' first lines, or a frame alone."""
    places = found["at"].split()
    starts = [parse_place(p) for p in places]
    if any(index == BENCH for index, _, _ in starts):
        raise ValueError("%s is the user's draft; mark places in the sights." % BENCH)
    line = lambda i: {"sight": sight_name(starts[i][0]), "line": starts[i][1][0]}  # noqa: E731
    if "jump" in found:
        if len(places) != 2 or found["jump"] not in TRIP_TYPES or "icon" in found:
            raise ValueError("jump takes two places, source then target, a type of %s, and no "
                             "icon." % ", ".join(TRIP_TYPES))
        return [{"from": line(0), "to": line(1), "type": found["jump"]}]
    if "icon" not in found:
        return [{"places": found["at"]}]
    icons = found["icon"].split()
    if len(icons) not in (1, len(places)):
        raise ValueError("icon takes one sign for all places or one per place, %r." % found["at"])
    return [{"at": line(k), "mark": icons[k if len(icons) > 1 else 0]} for k in range(len(places))]


def read_marks(text):
    """(text without the mark tags, marks for resolve_marks, frames): frames are (start, end,
    kind, [mark indices]) in the text returned, kind "icon", "here", "map" (a jump with no
    words, its arrow only) or the jump's index among the jumps (Jakub: the answer places its
    own marks, so where they stand is kept with it). The same mark again makes no second one:
    it frames its words in the same colour, so the answer can come back to a jump or a line."""
    out, found, frames, jumps, last = [], [], [], {}, 0
    for match in MARK_TAG.finditer(text):
        out.append(text[last:match.start()])
        start, last = sum(len(part) for part in out), match.end()
        marks = tag_marks(mark_attributes(match.group(1), match.group(2)))
        words = match.group(3)
        if "from" in marks[0]:
            if not words:
                marks[0]["map"] = True
            kind = "map" if not words else jumps.setdefault(repr(marks[0]), len(jumps))
        else:
            kind = "icon" if "at" in marks[0] else "here"
        signs = " ".join(m["mark"] for m in marks if "mark" in m)
        if signs and words.strip() != signs:  # the bench shows the gutter's signs (Jakub)
            words = (words + " " + signs) if words else signs
        indices = []
        for mark in marks:
            if mark not in found:
                found.append(mark)
            indices.append(found.index(mark))
        out.append(words)
        frames.append((start, start + len(words), kind, indices))
    out = "".join(out) + text[last:]
    left = [m.group(0) for m in TAG.finditer(out) if m.group(2) in MARK_TAGS + ("icon", "jump")]
    if left:
        raise ValueError("Write marks as %s; not %s." % (MARK_FORM, left[0]))
    return out, found, frames


def span_relation(one, other):
    """How two phrases (start, end) stand, as constituents do (Jakub): "same", "inside" (one
    within other), "around" (other within one), "apart", or "crossing", which no constituents
    are."""
    (a, b), (c, d) = one, other
    if (a, b) == (c, d):
        return "same"
    if b <= c or d <= a:
        return "apart"
    if c <= a and b <= d:
        return "inside"
    if a <= c and d <= b:
        return "around"
    return "crossing"


def place_text(name, first, last):
    """A place the user pointed at, in the guide's notation (Jakub): first and last are (line,
    column), 1-based and inclusive, the column None for whole lines. "(c):34", "(c):34-36",
    "(c):34:12" (a caret), "(c):34:12-16" (characters of a line), "(c):34:12-36:5"."""
    (l1, c1), (l2, c2) = first, last
    if c1 is None:
        return "%s:%s" % (name, l1 if l1 == l2 else "%d-%d" % (l1, l2))
    if l1 != l2:
        return "%s:%d:%d-%d:%d" % (name, l1, c1, l2, c2)
    return "%s:%d:%s" % (name, l1, c1 if c1 == c2 else "%d-%d" % (c1, c2))


BENCH = "(>)"  # the bench's draft as a place (Jakub: its prompt is >>>), its lines from 1
PLACE = re.compile(r"^(\(\w+\)|\(>\)):(\d+)(?::(\d+))?(?:-(\d+)(?::(\d+))?)?$")
HERE = re.compile(r'<here at="([^"]*)"(?: code="[^"]*")?>|</here>')


def parse_place(text):
    """The inverse of place_text: (sight index, or BENCH, (line, column), (line, column)), the
    columns None for whole lines; "(c):34-36", "(c):34:12-16", "(c):34:12-36:5", "(>):1:10-11".
    ValueError if it is none."""
    found = PLACE.match(text.strip())
    index = (BENCH if found.group(1) == BENCH else sight_index(found.group(1))) if found else None
    if index is None:
        raise ValueError("%r is no place: write \"(c):34\" or \"(c):34:12-16\"." % text)
    line, column, to, to_column = (int(g) if g else None for g in found.group(2, 3, 4, 5))
    if column is None:
        return index, (line, None), (to or line, None)
    if to_column is not None:
        return index, (line, column), (to, to_column)
    return index, (line, column), (line, to or column)


def read_here(text):
    """The inverse of here_tags: (the text without tags, [(start, end, at)]), nested tags
    included, code attributes dropped. ValueError for a tag left open or closed twice."""
    plain, spans, open_ = [], [], []
    last = length = 0
    for match in HERE.finditer(text):
        plain.append(text[last:match.start()])
        length += match.start() - last
        last = match.end()
        if match.group(1) is not None:
            open_.append((length, match.group(1)))
        elif open_:
            start, at = open_.pop()
            spans.append((start, length, at))
        else:
            raise ValueError("</here> without <here>")
    if open_:
        raise ValueError("<here> left open")
    return "".join(plain) + text[last:], sorted(spans)


def here_tags(text, spans):
    """text with each span (start, end, at) or (start, end, at, code) wrapped as
    <here at="..." code="...">…</here>, code being the code pointed at when it is part of one
    line (Jakub: the guide checks the place by it); nested where phrases nest: at one position
    closings come first, inner before outer, then openings, outer before inner."""
    inserts = []
    for start, end, at, *code in spans:
        quoted = ' code="%s"' % code[0].replace('"', "&quot;") if code and code[0] else ""
        inserts.append((start, 1, start - end, '<here at="%s"%s>' % (at, quoted)))
        inserts.append((end, 0, end - start, "</here>"))
    out, last = [], 0
    for pos, _, _, tag in sorted(inserts):
        out += [text[last:pos], tag]
        last = pos
    return "".join(out) + text[last:]


def trip_place(value):
    """A transition's place in a trip, as the guide writes it everywhere (Jakub): "(c):34" or
    "(c)" becomes (2, 34) or (2,); a list [2, 34] (a trip file's form) passes as it is."""
    if isinstance(value, list):
        return tuple(value)
    if not isinstance(value, str):
        raise ValueError("%r is no place: write \"(c):34\" or \"(c)\"." % (value,))
    sight, _, line = value.partition(":")
    index = sight_index(sight)
    if index is None or (line and not line.strip().isdigit()):
        raise ValueError("%r is no place: write a sight's name and a file line, \"(c):34\", or "
                         "the sight alone, \"(c)\"." % value)
    return (index, int(line)) if line else (index,)


def frame_scopes(frames, text):
    """The scope each frame is drawn in: an icon's by its kind, digits orange, letters blue; a
    jump's by its colour, as its arrows (see JUMP_COLOURS)."""
    scopes = []
    for start, end, kind, *_ in frames:
        if kind in ("here", "map"):
            scopes.append(HERE_SCOPE)
        elif kind == "icon":  # by its sign, the frame's last character
            scopes.append(REF_SCOPES["digit" if text[start:end].strip()[-1:].isdigit() else "letter"])
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
