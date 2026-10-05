"""The vetting pane: an L under the conversation and the code. Its cell spans both columns; the
code panes lie over its top right part, and on each line there a phantom fills that part, so no
text or caret reaches it. The last VETTING_LINES lines, under the code, use the full width."""

import sublime

from .config import VETTING_LINES

COVER_HTML = '<span style="padding-left: %dpx"></span>'
FILLS = {}


def make(window, make_side_view, match_font, conversation):
    view = make_side_view(window, "Vetting", {"word_wrap": False, "scroll_past_end": False})
    match_font(view, conversation)
    view.set_read_only(True)
    FILLS[view.id()] = [sublime.PhantomSet(view, "sight_walk_cover"), None]
    return view


def fill(view, behind, left_columns, cover_px, lines=()):
    """behind: lines that lie behind the code; left_columns: their visible width in characters;
    cover_px: the width the phantom fills behind the code. lines: the content, top first."""
    key = (behind, left_columns, cover_px, tuple(lines))
    state = FILLS[view.id()]
    if state[1] == key:
        return
    state[1] = key
    rows = list(lines) + [""] * max(behind + VETTING_LINES - len(lines), 0)
    # Behind the code, every line is padded to the boundary, where the phantom starts.
    text = "\n".join(row[:left_columns].ljust(left_columns) if i < behind else row
                     for i, row in enumerate(rows))
    view.run_command("sight_walk_replace", {"text": text})
    state[0].update([sublime.Phantom(sublime.Region(view.line(view.text_point(i, 0)).b),
                                     COVER_HTML % cover_px, sublime.LAYOUT_INLINE)
                     for i in range(behind)])
