"""The conversation pane: the transcript, which a guard keeps read-only, the draft after the
prompt, kept at the bottom of the pane, and the two-line header in place of a tab."""

import math

import sublime
import sublime_plugin

from .config import PROMPT
from .header import MARK_ROOM, title_lines
from .views import FADED, button_html, kept, make_side_view, match_font, phantoms
from .words import word

SYNTAX = "Packages/%s/SightWalkChat.sublime-syntax" % __package__.split(".")[0]

# Per chat buffer: the text before the draft (blank line, transcript, prompt). Only the plugin
# changes it, and it records the new text before each of its own edits.
PROTECTED = {}
GUARDS = {}
# The one conversation, carried from trip to trip (Jakub).
TRANSCRIPT = ""
MAC = sublime.platform() == "osx"
KEYS = (("Enter (⇧+Enter: %s)", "⌃⌘↓", "⌃⌘↑") if MAC
        else ("Enter (Shift+Enter: %s)", "Ctrl+Shift+↓", "Ctrl+Shift+↑"))
# The help mark: faded and outlined at all times, so it reads as read-only.
MARK_HTML = ('<a href="help" style="color: %s; text-decoration: none; border: 1px solid %s; '
             'border-radius: 3px; padding: 0 4px">?</a>' % (FADED, FADED))
def help_html():
    """The bench's keys, in the user's language."""
    send, nxt, previous = KEYS
    return "<div><b>%s</b> %s<br><b>%s</b> %s<br><b>%s</b> %s</div>" % (
        send % word("new_line"), word("send"), nxt, word("next"), previous, word("previous"))


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
    PROTECTED[buffer_id] = TRANSCRIPT + PROMPT
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
    kept(view)["mark"] = [phantoms(view, "sight_walk_mark"), None]
    return view


def show_header(view, title, status, help_mark=True, button=None):
    """button: (label, on_click), drawn at the right end of the first line instead of the help
    mark, like a sight's Edit button."""
    columns = int(view.viewport_extent()[0] / max(view.em_width(), 1))
    room = len(button[0]) + 4 - MARK_ROOM if button is not None else 0
    text = title_lines(title, status, columns - room)  # the first line ends where the mark goes
    mark = kept(view)["mark"]
    if text == mark[1]:
        return
    mark[1] = text
    view.run_command("sight_walk_replace", {"text": text})
    point = view.line(0).b
    if button is not None:
        html = button_html(button[0], "b")
        mark[0].update([sublime.Phantom(sublime.Region(point), html, sublime.LAYOUT_INLINE,
                                        lambda _: button[1]())])
        return
    phantom = sublime.Phantom(sublime.Region(point), MARK_HTML, sublime.LAYOUT_INLINE,
                              lambda _: view.show_popup(help_html(), location=point))
    mark[0].update([phantom] if help_mark else [])


STATUS_HTML = '<span style="color: %s">%%s</span>' % FADED


def make_status(window, conversation):
    """The status line between the bench's floor and the Tools pane's ceiling: what the
    conversation is about (the agent's status) and whether an answer is on its way (Jakub). It is
    shown nowhere else, neither in a header nor in the status bar."""
    view = make_side_view(window, "Status", {"word_wrap": False, "scroll_past_end": False,
                                             "sight_walk_blank": True})
    view.assign_syntax(SYNTAX)
    view.run_command("sight_walk_replace", {"text": " "})
    view.set_read_only(True)
    return view


def show_status(view, text, on_stop=None):
    """on_stop: while an answer is on its way, a [Stop] button after the text calls it."""
    if kept(view).get("status") == (text, bool(on_stop), word("stop")):
        return
    kept(view)["status"] = (text, bool(on_stop), word("stop"))
    html = STATUS_HTML % text.replace("&", "&amp;").replace("<", "&lt;")
    if on_stop:
        html += "&nbsp;&nbsp;" + button_html(word("stop"), "stop")
    phantoms(view, "sight_walk_status").update([sublime.Phantom(
        sublime.Region(0), html, sublime.LAYOUT_INLINE, lambda _: on_stop and on_stop())])


def show_help(view, point):
    """On hovering the right end of the first line, where the mark sits."""
    end = view.line(0).b
    if end - MARK_ROOM <= point <= end:
        view.show_popup(help_html(), sublime.HIDE_ON_MOUSE_MOVE_AWAY, end)


def say(view, text, prefix="A: "):
    global TRANSCRIPT
    protected = PROTECTED[view.buffer_id()]
    point = len(protected) - len(PROMPT)
    message = prefix + text.strip() + "\n\n"
    TRANSCRIPT += message
    PROTECTED[view.buffer_id()] = protected[:point] + message + PROMPT
    view.run_command("sight_walk_insert", {"point": point, "text": message})


def take_draft(view, edit):
    """Turns the draft into a sent message and opens a new prompt."""
    global TRANSCRIPT
    protected = PROTECTED[view.buffer_id()]
    start_of_draft = len(protected)
    draft = view.substr(sublime.Region(start_of_draft, view.size()))
    if not draft.strip():
        return None
    TRANSCRIPT += "U: " + draft + "\n\n"
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


def set_transcript(text):
    """Another conversation on the bench (a trip's kept one); catch_up shows it."""
    global TRANSCRIPT
    TRANSCRIPT = text


def catch_up(view):
    """Shows what was said on another bench meanwhile, keeping the draft."""
    protected = PROTECTED[view.buffer_id()]
    blanks = len(protected) - len(protected.lstrip("\n"))
    if protected[blanks:] == TRANSCRIPT + PROMPT:
        return
    PROTECTED[view.buffer_id()] = "\n" * blanks + TRANSCRIPT + PROMPT
    view.run_command("sight_walk_replace", {"text": PROTECTED[view.buffer_id()],
                                            "end": len(protected)})
