import math

import sublime
import sublime_plugin

from .config import PROMPT
from .header import MARK_ROOM, header_text
from .views import FADED, make_side_view, match_font

SYNTAX = "Packages/%s/SightWalkChat.sublime-syntax" % __package__.split(".")[0]
START = PROMPT

# Per chat buffer: the text before the draft (blank line, transcript, prompt). Only the plugin
# changes it, and it records the new text before each of its own edits.
PROTECTED = {}
GUARDS = {}
MAC = sublime.platform() == "osx"
KEYS = (("⌘+Enter", "⌃⌘↓", "⌃⌘↑") if MAC else ("Ctrl+Enter", "Ctrl+Shift+↓", "Ctrl+Shift+↑"))
# The help mark: faded and outlined at all times, so it reads as read-only.
MARK_HTML = ('<a href="help" style="color: %s; text-decoration: none; border: 1px solid %s; '
             'border-radius: 3px; padding: 0 4px">?</a>' % (FADED, FADED))
HELP_HTML = ("<div><b>%s</b> send<br><b>%s</b> explain next<br><b>%s</b> explain previous</div>"
             % KEYS)
MARKS = {}


def protected_end(end, changes):
    """Where the protected text ends after the changes. changes: (begin, end, inserted length)
    in order, each in the coordinates left by the one before. Text typed over the boundary
    counts as draft."""
    for a, b, inserted in changes:
        if a >= end:
            continue
        end = end - (b - a) + inserted if b <= end else a
    return end


class Guard(sublime_plugin.TextChangeListener):
    """Sees every edit, whatever command made it, and puts back any change to the protected text."""

    def __init__(self, view):
        super().__init__()
        self.view = view

    def on_text_changed(self, changes):
        protected = PROTECTED.get(self.view.buffer_id())
        if protected is None:
            return
        spans = [(c.a.pt, c.b.pt, len(c.str)) for c in changes]
        # Typing in the draft never reaches the protected text, so most keystrokes stop here.
        if all(a >= len(protected) for a, _, _ in spans):
            return
        if self.view.substr(sublime.Region(0, len(protected))) == protected:
            return
        end = protected_end(len(protected), spans)
        self.view.run_command("sight_walk_replace", {"text": protected, "end": end})


def start(view):
    buffer_id = view.buffer_id()
    view.assign_syntax(SYNTAX)
    PROTECTED[buffer_id] = START
    view.run_command("sight_walk_replace", {"text": START})
    GUARDS[buffer_id] = Guard(view)
    GUARDS[buffer_id].attach(view.buffer())


SYMBOL_FLAGS = sublime.DRAW_NO_FILL | sublime.DRAW_NO_OUTLINE | sublime.DRAW_STIPPLED_UNDERLINE


def underline_symbols(view):
    """A stippled underline under every name of code, in the text colour: schemes that leave
    variables plain (like Mariana) still show them as code. Waits for the syntax to catch up."""
    def draw():
        if view.is_valid():
            regions = view.find_by_selector("meta.symbol.sight-walk")
            view.add_regions("sight_walk_symbols", regions, "sight_walk.symbol", "", SYMBOL_FLAGS)
    sublime.set_timeout(draw, 50)


def make_header(window, conversation):
    """The conversation's header, in place of a tab: two read-only lines, the help mark on the
    right of the first."""
    view = make_side_view(window, "Conversation", {
        "word_wrap": False, "gutter": True, "line_numbers": False, "scroll_past_end": False,
        "sight_walk_header": True})
    match_font(view, conversation)  # Plain Text has its own font
    view.set_read_only(True)
    MARKS[view.id()] = [sublime.PhantomSet(view, "sight_walk_mark"), None]
    return view


def show_header(view, status):
    columns = int(view.viewport_extent()[0] / max(view.em_width(), 1))
    text = header_text(status, columns)
    mark = MARKS[view.id()]
    if text == mark[1]:
        return
    mark[1] = text
    view.run_command("sight_walk_replace", {"text": text})
    point = view.line(0).b
    phantom = sublime.Phantom(sublime.Region(point), MARK_HTML, sublime.LAYOUT_INLINE,
                              lambda _: view.show_popup(HELP_HTML, location=point))
    mark[0].update([phantom])


def show_help(view, point):
    """On hovering the right end of the first line, where the mark sits."""
    end = view.line(0).b
    if end - MARK_ROOM <= point <= end:
        view.show_popup(HELP_HTML, sublime.HIDE_ON_MOUSE_MOVE_AWAY, end)


def say(view, text, prefix="A: "):
    protected = PROTECTED[view.buffer_id()]
    point = len(protected) - len(PROMPT)
    message = prefix + text.strip() + "\n\n"
    PROTECTED[view.buffer_id()] = protected[:point] + message + PROMPT
    view.run_command("sight_walk_insert", {"point": point, "text": message})


def take_draft(view, edit):
    """Turns the draft into a sent message and opens a new prompt."""
    protected = PROTECTED[view.buffer_id()]
    start_of_draft = len(protected)
    draft = view.substr(sublime.Region(start_of_draft, view.size()))
    if not draft.strip():
        return None
    PROTECTED[view.buffer_id()] = protected[:-len(PROMPT)] + "U: " + draft + "\n\n" + PROMPT
    view.replace(edit, sublime.Region(start_of_draft - len(PROMPT), start_of_draft), "U: ")
    view.insert(edit, view.size(), "\n\n" + PROMPT)
    view.sel().clear()
    view.sel().add(sublime.Region(view.size()))
    return draft.strip()


def keep_at_bottom(view):
    """Adds or removes blank lines above the transcript until the prompt line touches the bottom.
    Real lines, not a phantom, so a click anywhere in the pane lands in the conversation."""
    lh = view.line_height()
    bottom = view.text_to_layout(view.size())[1] + lh - view.viewport_position()[1]
    protected = PROTECTED[view.buffer_id()]
    blanks = len(protected) - len(protected.lstrip("\n"))
    # Rounded down, so a line fits or not and the count never flips back and forth.
    lines = max(math.floor((view.viewport_extent()[1] - bottom) / lh + 0.01), -blanks)
    if lines == 0:
        return
    # Only the leading blank lines change; the protected text is recorded before the edit.
    PROTECTED[view.buffer_id()] = "\n" * (blanks + lines) + protected[blanks:]
    view.run_command("sight_walk_replace", {"text": "\n" * (blanks + lines), "end": blanks})
