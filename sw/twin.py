"""A twin: a scratch view showing a copy of some text with room above and below it, for the wheel.
A sight at line 1 shows its line 1's code in a twin (see line_one). The room is made with phantoms,
not blank lines, so the caret cannot travel into it; the one blank line the top phantom needs is
the only line it can reach there."""

import sublime

from .config import ROOM_LINES
from .views import CODE_SETTINGS, match_font, phantoms

ROOM_HTML = '<div style="height: %dpx"></div>'
# No gutter and no margin: the cell beside the twin shows the real view's gutter and margin.
TWIN_SETTINGS = (("gutter", False), ("line_numbers", False), ("margin", 0),
                 ("scroll_past_end", False))


def make(window, name, code_view, text):
    twin = window.new_file()
    twin.set_scratch(True)
    twin.set_name(name)
    for key, value in CODE_SETTINGS + TWIN_SETTINGS:
        twin.settings().set(key, value)
    twin.settings().set("color_scheme", code_view.settings().get("color_scheme"))
    twin.assign_syntax(code_view.syntax())
    match_font(twin, code_view)
    twin.set_read_only(True)
    fill(twin, text, code_view.line_height())
    return twin


def fill(twin, text, lh):
    """The text after one blank line, with the room phantoms; again after an edit."""
    twin.run_command("sight_walk_replace", {"text": "\n" + text})
    html = ROOM_HTML % (ROOM_LINES * lh)
    phantoms(twin, "sight_walk_room").update([sublime.Phantom(sublime.Region(twin.line(0).b), html, sublime.LAYOUT_BLOCK),
                     sublime.Phantom(sublime.Region(twin.size()), html, sublime.LAYOUT_BLOCK)])


def content_top(twin):
    """Layout y of the text's first line, below the blank line and the room phantom."""
    return twin.text_to_layout(twin.text_point(1, 0))[1]
