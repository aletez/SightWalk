import sublime
import sublime_plugin

from . import chat, scrollbars, state


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
    def run(self, edit):
        reader = state.reader_for(self.view.window())
        if reader is None:
            return
        context = reader.context()
        draft = chat.take_draft(self.view, edit)
        if draft:
            reader.inbox.put(dict(context, text=draft, **reader.take_edits()))


class SightWalkAskCommand(sublime_plugin.TextCommand):
    """Sends a fixed message, such as "Explain next.", without touching the draft."""

    def run(self, edit, text):
        reader = state.reader_for(self.view.window())
        if reader is None:
            return
        reader.say(text, prefix="U: ")
        reader.inbox.put(dict(reader.context(), text=text, **reader.take_edits()))


class SightWalkEditCommand(sublime_plugin.TextCommand):
    """Enter in a code pane: opens the editor at the caret's line."""

    def run(self, edit):
        reader = state.reader_for(self.view.window())
        index = next((i for i, s in enumerate(reader.segments) if s.view == self.view), None)
        if index is None:
            return
        seg = reader.segments[index]
        line = self.view.rowcol(self.view.sel()[0].b)[0] + 1 if self.view.sel() else seg.begin
        reader.open_editor(index, min(max(line, seg.begin), seg.end))


class SightWalkCloseEditorCommand(sublime_plugin.TextCommand):
    """Esc in the editor: closes it the usual way, Sublime asking about unsaved changes."""

    def run(self, edit):
        reader = state.reader_for(self.view.window())
        if reader is not None and reader.editor is not None:
            reader.close_editor()


class SightWalkBlockCommand(sublime_plugin.TextCommand):
    """Does nothing: primary+w, held or pressed twice, would close the reader's own views."""

    def run(self, edit):
        pass


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
        reader.scroll_to(reader.offset + lines * reader.lh + pages * reader.height)

    def is_enabled(self):
        return state.reader_for(self.window) is not None


class SightWalkChatListener(sublime_plugin.ViewEventListener):
    @classmethod
    def is_applicable(cls, settings):
        return settings.get("sight_walk_chat", False)

    def on_modified(self):
        # Typing and inserted replies keep the prompt line at the bottom of the pane.
        self.view.show(self.view.size())
        chat.underline_symbols(self.view)


class SightWalkWindowListener(sublime_plugin.EventListener):
    def on_activated(self, view):
        scrollbars.reader_focused(state.reader_for(view.window()) is not None)

    def on_pre_close_window(self, window):
        state.forget(window)
