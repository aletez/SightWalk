"""The conversation pane: the transcript, which a guard keeps read-only, the draft after the
prompt, kept at the bottom of the pane, and the two-line header in place of a tab."""

import math

import sublime
import sublime_plugin

from .config import PROMPT
from .header import MARK_ROOM, title_lines
from .views import FADED, make_side_view, match_font

SYNTAX = "Packages/%s/SightWalkChat.sublime-syntax" % __package__.split(".")[0]

# Per chat buffer: the text before the draft (blank line, transcript, prompt). Only the plugin
# changes it, and it records the new text before each of its own edits.
PROTECTED = {}
GUARDS = {}
# The one conversation, carried from bench to bench: a trip's, the Vetting strip's (Jakub).
TRANSCRIPT = [""]
MAC = sublime.platform() == "osx"
KEYS = (("Enter (⇧+Enter: new line)", "⌃⌘↓", "⌃⌘↑") if MAC
        else ("Enter (Shift+Enter: new line)", "Ctrl+Shift+↓", "Ctrl+Shift+↑"))
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
        # Typing into the transcript goes on in the draft: the letters are not lost (Jakub).
        typed = "".join(c.str for c in changes if c.a.pt < len(protected) and c.a.pt == c.b.pt)
        if typed.strip():
            self.view.run_command("sight_walk_insert", {"point": self.view.size(), "text": typed})
            self.view.sel().clear()
            self.view.sel().add(sublime.Region(self.view.size()))


def start(view):
    buffer_id = view.buffer_id()
    view.assign_syntax(SYNTAX)
    PROTECTED[buffer_id] = TRANSCRIPT[0] + PROMPT
    view.run_command("sight_walk_replace", {"text": PROTECTED[buffer_id]})
    GUARDS[buffer_id] = Guard(view)
    GUARDS[buffer_id].attach(view.buffer())


def make_header(window, conversation, name):
    """A two-line read-only header in place of a tab, over the Vetting Bench (with the help mark
    on the right of the first line) or over the Sights. Both use the conversation's font."""
    view = make_side_view(window, name, {
        "word_wrap": False, "gutter": True, "line_numbers": False, "scroll_past_end": False,
        "sight_walk_header": True})
    match_font(view, conversation)  # Plain Text has its own font
    view.set_read_only(True)
    MARKS[view.id()] = [sublime.PhantomSet(view, "sight_walk_mark"), None]
    return view


def show_header(view, title, status, help_mark=True):
    columns = int(view.viewport_extent()[0] / max(view.em_width(), 1))
    text = title_lines(title, status, columns)
    mark = MARKS[view.id()]
    if text == mark[1]:
        return
    mark[1] = text
    view.run_command("sight_walk_replace", {"text": text})
    point = view.line(0).b
    phantom = sublime.Phantom(sublime.Region(point), MARK_HTML, sublime.LAYOUT_INLINE,
                              lambda _: view.show_popup(HELP_HTML, location=point))
    mark[0].update([phantom] if help_mark else [])


def show_help(view, point):
    """On hovering the right end of the first line, where the mark sits."""
    end = view.line(0).b
    if end - MARK_ROOM <= point <= end:
        view.show_popup(HELP_HTML, sublime.HIDE_ON_MOUSE_MOVE_AWAY, end)


def say(view, text, prefix="A: "):
    protected = PROTECTED[view.buffer_id()]
    point = len(protected) - len(PROMPT)
    message = prefix + text.strip() + "\n\n"
    TRANSCRIPT[0] += message
    PROTECTED[view.buffer_id()] = protected[:point] + message + PROMPT
    view.run_command("sight_walk_insert", {"point": point, "text": message})


def take_draft(view, edit):
    """Turns the draft into a sent message and opens a new prompt."""
    protected = PROTECTED[view.buffer_id()]
    start_of_draft = len(protected)
    draft = view.substr(sublime.Region(start_of_draft, view.size()))
    if not draft.strip():
        return None
    TRANSCRIPT[0] += "U: " + draft + "\n\n"
    PROTECTED[view.buffer_id()] = protected[:-len(PROMPT)] + "U: " + draft + "\n\n" + PROMPT
    view.replace(edit, sublime.Region(start_of_draft - len(PROMPT), start_of_draft), "U: ")
    view.insert(edit, view.size(), "\n\n" + PROMPT)
    view.sel().clear()
    view.sel().add(sublime.Region(view.size()))
    return draft.strip()


def keep_at_bottom(view, room=0):
    """Adds or removes blank lines above the transcript until the prompt line touches the bottom,
    or stands room lines above it. Real lines, not a phantom, so a click anywhere in the pane
    lands in the conversation."""
    lh = view.line_height()
    bottom = view.text_to_layout(view.size())[1] + (1 + room) * lh - view.viewport_position()[1]
    protected = PROTECTED[view.buffer_id()]
    blanks = len(protected) - len(protected.lstrip("\n"))
    # Rounded down, so a line fits or not and the count never flips back and forth.
    lines = max(math.floor((view.viewport_extent()[1] - bottom) / lh + 0.01), -blanks)
    if lines == 0:
        return
    # Only the leading blank lines change; the protected text is recorded before the edit.
    PROTECTED[view.buffer_id()] = "\n" * (blanks + lines) + protected[blanks:]
    view.run_command("sight_walk_replace", {"text": "\n" * (blanks + lines), "end": blanks})


def catch_up(view):
    """Shows what was said on another bench meanwhile, keeping the draft."""
    protected = PROTECTED[view.buffer_id()]
    blanks = len(protected) - len(protected.lstrip("\n"))
    if protected[blanks:] == TRANSCRIPT[0] + PROMPT:
        return
    PROTECTED[view.buffer_id()] = "\n" * blanks + TRANSCRIPT[0] + PROMPT
    view.run_command("sight_walk_replace", {"text": PROTECTED[view.buffer_id()],
                                            "end": len(protected)})
