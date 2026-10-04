"""Marks as gutter icons. Pure functions, no Sublime API."""

import math

from .config import DEFAULT_MARK
from .spec import matches

PASS, TAKE = "➡️", "⬅️"
NAMED = {"🅰️": "letter_a", "🅱️": "letter_b", "*️⃣": "letter_a"}
NAMED.update(("%d️⃣" % n, "digit_%d" % n) for n in range(1, 10))


def line_y(segment, line, lh):
    return segment.code_item.y + (line - segment.begin) * lh


def resolve_target(segments, mark):
    if "pane" in mark:
        index, line = int(mark["pane"]), int(mark["line"])
        if not 0 <= index < len(segments):
            raise ValueError("No pane %d" % index)
        return index, line
    name, _, line = mark["target"].rpartition(":")
    line = int(line)
    candidates = [i for i, seg in enumerate(segments) if matches(seg, name)]
    if not candidates:
        raise ValueError("No pane shows %s" % name)
    inside = [i for i in candidates if segments[i].begin <= line <= segments[i].end]
    return (inside or candidates)[0], line


def icon_for(emoji):
    if emoji in NAMED:
        return NAMED[emoji]
    if len(emoji) == 1 and emoji in "123456789":
        return "digit_" + emoji
    if len(emoji) == 1 and emoji.isascii() and emoji.isalpha():
        return "letter_" + emoji.lower()
    raise ValueError("Unknown mark %r" % emoji)


def resolve_marks(segments, marks):
    resolved = []
    for mark in marks:
        index, line = resolve_target(segments, mark)
        emoji = mark.get("emoji", DEFAULT_MARK)
        icon = None if emoji in (PASS, TAKE) else icon_for(emoji)
        resolved.append({"seg": index, "line": line, "emoji": emoji, "icon": icon})
    pair_jumps(resolved)
    return resolved


def pair_jumps(resolved):
    # The n-th sender goes with the n-th receiver. The arrows bend towards each other: down from
    # a sender above its receiver, up from one below. A mark without a partner points down.
    senders = [m for m in resolved if m["emoji"] == PASS]
    receivers = [m for m in resolved if m["emoji"] == TAKE]
    for i, mark in enumerate(senders):
        partner = receivers[i] if i < len(receivers) else None
        down = partner is None or (mark["seg"], mark["line"]) <= (partner["seg"], partner["line"])
        mark["icon"] = "pass_down" if down else "pass_up"
        if partner is not None:
            partner["icon"] = "take_above" if down else "take_below"
    for mark in receivers[len(senders):]:
        mark["icon"] = "take_above"


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


def strip_text(rows, pad):
    return "\n" * (rows + 2 * pad - 1)
