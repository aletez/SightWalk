"""Text of the one-line headers over the Vetting Bench and over the Sights. Pure functions, no
Sublime API."""

import textwrap

BENCH = "Bench"  # the bench's header names whom you talk to, as in chat clients (Jakub)
SIGHTS = "Sights"
STRIP = "Scroll strip"
MARK_ROOM = 4  # columns kept at the right for the help mark, close to the edge (Jakub)


def title_lines(title, status, columns):
    """One line (Jakub, 2026-10-19: the status line took the second's job): the title and a
    status (the trip's name, say), cut to the view with "…", padded to the right edge so the
    help mark can sit there."""
    width = max(columns - MARK_ROOM, 10)
    text = title + (" · " + status.strip() if status and status.strip() else "")
    if len(text) > width:
        text = text[:width - 1].rstrip() + "…"
    return text.ljust(width)
