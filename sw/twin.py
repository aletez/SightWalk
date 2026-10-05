"""Every pane's cell is split in two: a narrow left strip showing the real view, that is its gutter
with the true line numbers, and a wide right strip showing the twin, that is the range's text with
room above and below. The gutter is the reader's scroll strip: the wheel over it is taken over and
moves the whole column. The wheel over the code only scrolls the twin, which the next render puts
back, so reading a long line or a wide pane stays possible.

The room is made with phantoms, not blank lines, so the caret cannot travel into it and give the
trick away; the one blank line the top phantom needs is the only line it can reach there."""

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
    for key, value in CODE_SETTINGS + (("gutter", False), ("line_numbers", False),
                                       ("scroll_past_end", False), ("sight_walk_twin", True)):
        settings.set(key, value)
    settings.set("color_scheme", code_view.settings().get("color_scheme"))
    twin.assign_syntax(code_view.syntax())
    match_font(twin, code_view)
    twin.run_command("sight_walk_replace", {"text": "\n" + text})
    twin.set_read_only(True)
    room(twin, code_view.line_height())
    return twin


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
