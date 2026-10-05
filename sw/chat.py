import sublime
import sublime_plugin

from .config import PROMPT

SYNTAX = "Packages/%s/SightWalkChat.sublime-syntax" % __package__.split(".")[0]
# The blank first line carries the filler phantom, which can only sit below a line.
START = "\n" + PROMPT

# Per chat buffer: the text before the draft (blank line, transcript, prompt). Only the plugin
# changes it, and it records the new text before each of its own edits.
PROTECTED = {}
GUARDS = {}
FILLERS = {}
HINTS = {}
HINT = ("⌘+Enter" if sublime.platform() == "osx" else "Ctrl+Enter") + " to send"
HINT_HTML = '<span style="color: color(var(--foreground) alpha(0.35))">%s</span>' % HINT


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
    FILLERS[buffer_id] = [sublime.PhantomSet(view, "sight_walk_fill"), 0]
    HINTS[buffer_id] = [sublime.PhantomSet(view, "sight_walk_hint"), False]
    update_hint(view)


SYMBOL_FLAGS = sublime.DRAW_NO_FILL | sublime.DRAW_NO_OUTLINE | sublime.DRAW_STIPPLED_UNDERLINE


def underline_symbols(view):
    """A stippled underline under every name of code, in the text colour: schemes that leave
    variables plain (like Mariana) still show them as code. Waits for the syntax to catch up."""
    def draw():
        if view.is_valid():
            regions = view.find_by_selector("meta.symbol.sight-walk")
            view.add_regions("sight_walk_symbols", regions, "sight_walk.symbol", "", SYMBOL_FLAGS)
    sublime.set_timeout(draw, 50)


def update_hint(view):
    """A faint hint after the prompt while the draft is empty. A phantom is not text, so it can't
    be selected, copied or sent."""
    hint = HINTS.get(view.buffer_id())
    protected = PROTECTED.get(view.buffer_id())
    if hint is None or protected is None:
        return
    empty = view.size() == len(protected)
    if empty != hint[1]:
        hint[1] = empty
        phantom = sublime.Phantom(sublime.Region(view.size()), HINT_HTML, sublime.LAYOUT_INLINE)
        hint[0].update([phantom] if empty else [])


def say(view, text):
    protected = PROTECTED[view.buffer_id()]
    point = len(protected) - len(PROMPT)
    message = "A: " + text.strip() + "\n\n"
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


def keep_at_middle(view, scroll=False):
    """Keeps the prompt line at the middle of the pane: a filler above a short transcript, a
    scroll past the end for a long one. Only changes scroll, so the user can read back."""
    phantoms, fill = FILLERS[view.buffer_id()]
    half = view.viewport_extent()[1] / 2
    end = view.text_to_layout(view.size())[1] + view.line_height()
    # Corrected from the measured result, so the phantom's exact rendering doesn't matter.
    new = int(min(max(fill + half - end, 0), half))
    if abs(new - fill) >= 2:
        FILLERS[view.buffer_id()][1] = new
        html = '<div style="height: %dpx"></div>' % new
        phantoms.update([sublime.Phantom(sublime.Region(0), html, sublime.LAYOUT_BLOCK)] if new else [])
    elif scroll:
        view.set_viewport_position((0, max(end - half, 0)), False)
