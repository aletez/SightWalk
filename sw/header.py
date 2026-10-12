"""Text of the two-line headers over the Vetting Bench and over the Sights. Pure functions, no
Sublime API."""

import textwrap

BENCH = "Bench"  # the bench's header names whom you talk to, as in chat clients (Jakub)
SIGHTS = "Sights"
STRIP = "Scroll strip"
MARK_ROOM = 6  # columns kept free at the right of the first line for the help mark


def title_lines(title, status, columns):
    """Two lines: the title and a status (the agent's, or the trip's name), wrapped to the view,
    the first line padded to the right edge so the help mark can sit there. A status too long for
    two lines is cut."""
    width = max(columns - MARK_ROOM, 10)
    text = title + (" · " + status.strip() if status and status.strip() else "")
    lines = textwrap.wrap(text, width) or [title]
    if len(lines) > 2:
        lines = [lines[0], lines[1][:width - 1].rstrip() + "…"]
    first = lines[0].ljust(width)
    return first + "\n" + (lines[1] if len(lines) > 1 else "")
