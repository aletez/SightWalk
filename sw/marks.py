"""Indicators in the scroll strip. Pure functions, no Sublime API."""

from .config import DEFAULT_MARK
from .spec import matches

ABOVE, BELOW = "⬆️", "⬇️"


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


def resolve_marks(segments, marks):
    resolved = []
    for mark in marks:
        index, line = resolve_target(segments, mark)
        resolved.append({"seg": index, "line": line, "emoji": mark.get("emoji", DEFAULT_MARK)})
    return resolved


def strip_rows(placed, offset, lh, rows):
    """placed: (virtual y, emoji) pairs. Returns one string per visible row."""
    indexed = [(int(round((y - offset) / lh)), emoji) for y, emoji in placed]
    marks = {}
    for r, emoji in indexed:
        if 0 <= r < rows:
            marks[r] = marks.get(r, "") + emoji
    for r, _ in indexed:
        if r < 0:
            marks.setdefault(0, ABOVE)
        elif r >= rows:
            marks.setdefault(rows - 1, BELOW)
    return [marks.get(r, "") for r in range(rows)]


def strip_text(rows, pad):
    return "\n" * pad + "\n".join(rows) + "\n" * pad
