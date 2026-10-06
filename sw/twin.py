"""A twin for a pane starting at its file's line 1: such a view cannot move up, so the wheel over
it would not scroll the reader that way. Its cell is split: a narrow left strip shows the real
view, that is its gutter with the true line numbers, and the rest shows the twin, the range's text
with room above and below. The room is made with phantoms, not blank lines, so the caret cannot
travel into it; the one blank line the top phantom needs is the only line it can reach there."""

import sublime

from .config import ROOM_LINES
from .views import CODE_SETTINGS, match_font

ROOM_HTML = '<div style="height: %dpx"></div>'
PHANTOMS = {}


def make(window, seg, code_view, text):
    """A scratch view with one blank line, the range's text, and a phantom of room at each end."""
    twin = window.new_file()
    twin.set_scratch(True)
    twin.set_name(seg.spec)
    settings = twin.settings()
    # No margin: Sublime paints a margin in the gutter's colour, so the real view's cell beside
    # the twin shows it, and the twin's text starts right at its cell's edge.
    for key, value in CODE_SETTINGS + (("gutter", False), ("line_numbers", False), ("margin", 0),
                                       ("scroll_past_end", False), ("sight_walk_twin", True)):
        settings.set(key, value)
    settings.set("color_scheme", code_view.settings().get("color_scheme"))
    twin.assign_syntax(code_view.syntax())
    match_font(twin, code_view)
    twin.set_read_only(True)
    fill(twin, text, code_view.line_height())
    return twin


def fill(twin, text, lh):
    """The range's text after one blank line, with the room phantoms; again after an edit."""
    twin.run_command("sight_walk_replace", {"text": "\n" + text})
    room(twin, lh)


def room(twin, lh):
    """Phantoms below the blank first line and below the last line: room for the wheel either way."""
    html = ROOM_HTML % (ROOM_LINES * lh)
    phantoms = sublime.PhantomSet(twin, "sight_walk_room")
    phantoms.update([sublime.Phantom(sublime.Region(twin.line(0).b), html, sublime.LAYOUT_BLOCK),
                     sublime.Phantom(sublime.Region(twin.size()), html, sublime.LAYOUT_BLOCK)])
    PHANTOMS[twin.id()] = phantoms


def content_top(twin):
    """Layout y of the range's first line, below the blank line and the room phantom."""
    return twin.text_to_layout(twin.text_point(1, 0))[1]
