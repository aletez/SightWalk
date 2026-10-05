"""A twin for a pane whose range touches the file's first or last line: such a pane cannot scroll
that way, so the wheel over it does nothing. The pane's cell is then split into a narrow left strip
showing the real view (its gutter, with the true line numbers) and a wide right strip showing the
twin: the same lines with room above and below. The room is made with phantoms, not blank lines,
so the caret cannot travel into it and give the trick away; the one blank line the top phantom
needs is the only line the caret can reach there."""

import sublime

from .config import HEADER_PAD
from .views import CODE_SETTINGS, match_font

ROOM_HTML = '<div style="height: %dpx"></div>'
PHANTOMS = {}


def needed(view, seg):
    return seg.begin == 1 or seg.end >= view.rowcol(view.size())[0] + 1


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
    html = ROOM_HTML % (HEADER_PAD * lh)
    phantoms = sublime.PhantomSet(twin, "sight_walk_room")
    phantoms.update([sublime.Phantom(sublime.Region(twin.line(0).b), html, sublime.LAYOUT_BLOCK),
                     sublime.Phantom(sublime.Region(twin.size()), html, sublime.LAYOUT_BLOCK)])
    PHANTOMS[twin.id()] = phantoms


def content_top(twin):
    """Layout y of the range's first line, below the blank line and the room phantom."""
    return twin.text_to_layout(twin.text_point(1, 0))[1]
