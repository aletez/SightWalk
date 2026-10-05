"""Text of the conversation's header. Pure functions, no Sublime API."""

import textwrap

TITLE = "Conversation"
MARK_ROOM = 6  # columns kept free at the right of the first line for the help mark


def header_text(status, columns):
    """Two lines: the title and the agent's status, wrapped to the pane, the first line padded to
    the right edge so the help mark can sit there. A status too long for two lines is cut."""
    width = max(columns - MARK_ROOM, 10)
    text = TITLE + (" · " + status.strip() if status and status.strip() else "")
    lines = textwrap.wrap(text, width) or [TITLE]
    if len(lines) > 2:
        lines = [lines[0], lines[1][:width - 1].rstrip() + "…"]
    first = lines[0].ljust(width)
    return first + "\n" + (lines[1] if len(lines) > 1 else "")
