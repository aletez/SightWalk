"""Sublime commands and listeners. sight_walk.py imports them, which is how Sublime finds them."""

import sublime
import sublime_plugin

from . import asked, chat, guide, scrollbars, state
from .strip import GuideStrip


class SightWalkReplaceCommand(sublime_plugin.TextCommand):
    def run(self, edit, text, end=None):
        read_only = self.view.is_read_only()
        self.view.set_read_only(False)
        self.view.replace(edit, sublime.Region(0, self.view.size() if end is None else end), text)
        # Replacing text under the caret selects the new text, so put a bare caret at the end.
        self.view.sel().clear()
        self.view.sel().add(sublime.Region(self.view.size()))
        self.view.set_read_only(read_only)


class SightWalkInsertCommand(sublime_plugin.TextCommand):
    def run(self, edit, point, text):
        self.view.insert(edit, point, text)


class SightWalkSendCommand(sublime_plugin.TextCommand):
    """primary+enter on a bench, a trip's or the small one: the draft goes to the agent."""

    def run(self, edit):
        owner = state.owner(self.view)
        if owner is None:
            return
        context = owner.context()
        draft = chat.take_draft(self.view, edit)
        if draft:
            state.INBOX.put(dict(context, text=draft, **owner.take_edits()))
            guide.await_answer(owner)


class SightWalkAskCommand(sublime_plugin.TextCommand):
    """Sends a fixed message, such as "Explain next.", without touching the draft."""

    def run(self, edit, text):
        owner = state.owner(self.view)
        if owner is None:
            return
        owner.say(text, prefix="U: ")
        state.INBOX.put(dict(owner.context(), text=text, **owner.take_edits()))
        guide.await_answer(owner)


class SightWalkEditCommand(sublime_plugin.TextCommand):
    """Enter in a sight: opens the editor at the caret's line."""

    def run(self, edit):
        reader = state.reader_for(self.view.window())
        index = None if reader is None else reader.sight_of(self.view)
        if index is None:
            return
        sight = reader.sights[index]
        line = self.view.rowcol(self.view.sel()[0].b)[0] + 1 if self.view.sel() else sight.begin
        reader.open_editor(index, min(max(line, sight.begin), sight.end))


class SightWalkCloseEditorCommand(sublime_plugin.TextCommand):
    """Esc in the editor: closes it the usual way, Sublime asking about unsaved changes."""

    def run(self, edit):
        reader = state.reader_for(self.view.window())
        if reader is not None and reader.editor is not None:
            reader.close_editor()


class SightWalkHeaderListener(sublime_plugin.ViewEventListener):
    @classmethod
    def is_applicable(cls, settings):
        return settings.get("sight_walk_header", False)

    def on_hover(self, point, hover_zone):
        if hover_zone == sublime.HOVER_TEXT:
            chat.show_help(self.view, point)


class SightWalkScrollCommand(sublime_plugin.WindowCommand):
    def run(self, lines=0, pages=0.0):
        reader = state.reader_for(self.window)
        if reader is None or not reader.ready:
            return
        reader.scroll_to(reader.offset + lines * reader.lh + pages * reader.room())

    def is_enabled(self):
        return state.reader_for(self.window) is not None


class SightWalkChatListener(sublime_plugin.ViewEventListener):
    @classmethod
    def is_applicable(cls, settings):
        return settings.get("sight_walk_chat", False)

    def on_modified(self):
        # Typing and inserted replies keep the prompt line at the bottom of the pane.
        self.view.show(self.view.size())


class SightWalkWindowListener(sublime_plugin.EventListener):
    def on_activated(self, view):
        scrollbars.reader_focused(state.owner(view) is not None)

    def on_pre_close_window(self, window):
        state.forget(window)


class SightWalkAskGuideCommand(sublime_plugin.TextCommand):
    """On a selection in any window: the Vetting strip glides in, to ask the guide about it."""

    def run(self, edit):
        bench = state.current_bench()
        if bench is not None:
            bench.close()
        strip = state.STRIPS.get(self.view.window().id())
        if strip is not None and strip.chat.is_valid():
            strip.open(self.view)
        else:
            strip = state.STRIPS[self.view.window().id()] = GuideStrip(self.view)
        state.BENCH[0] = strip
        if guide.ensure(state.BENCH[0].folder()):
            state.BENCH[0].note_waiting(guide.COMING)

    def is_enabled(self):
        return not self.view.settings().get("sight_walk", False) and self.view.window() is not None


class SightWalkCloseStripCommand(sublime_plugin.TextCommand):
    """Esc or primary+w on the Vetting strip: it glides out."""

    def run(self, edit):
        bench = state.current_bench()
        if bench is not None:
            bench.close()


class SightWalkStopGuideCommand(sublime_plugin.WindowCommand):
    """Ends the Vetting guide that SightWalk started in the background."""

    def run(self):
        guide.stop()

    def is_enabled(self):
        return guide.running()


class SightWalkToggleGuideCommand(sublime_plugin.TextCommand):
    """primary+g: the Vetting strip glides in on the selection, or out if it is open; in a trip,
    the focus goes to the bench, and from the bench back to the sight in focus (Jakub)."""

    def run(self, edit):
        bench = state.current_bench()
        reader = state.reader_for(self.view.window())
        if bench is not None and bench.window == self.view.window():
            bench.close()
        elif reader is not None:
            reader.toggle_focus(self.view)
        elif self.view.settings().get("sight_walk_strip", False):
            self.reopen_strip()  # its view, pulled into a cell of the user's by a layout change
        elif not self.view.settings().get("sight_walk", False):
            self.view.run_command("sight_walk_ask_guide")

    def reopen_strip(self):
        strip = state.STRIPS.get(self.view.window().id())
        if strip is None:
            return
        others = [v for v in self.view.window().views() if v != strip.chat]
        origin = strip.origin if strip.origin.is_valid() else (others[0] if others else None)
        if origin is not None:
            strip.open(origin)
            state.BENCH[0] = strip


class SightWalkSightListener(sublime_plugin.ViewEventListener):
    """Hovering a use the code's own questions point at (see asked)."""

    @classmethod
    def is_applicable(cls, settings):
        return settings.get("sight_walk_code", False)

    def on_hover(self, point, hover_zone):
        if hover_zone == sublime.HOVER_TEXT:
            asked.show_popup(self.view, point)


class SightWalkToggleSentinelsCommand(sublime_plugin.TextCommand):
    """References without sentinel: their underlines on or off (see asked)."""

    def run(self, edit):
        asked.toggle()
