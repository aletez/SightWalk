import sublime
import sublime_plugin

from . import chat, state


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
            reader.inbox.put(dict(context, text=draft))


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


class SightWalkWindowListener(sublime_plugin.EventListener):
    def on_pre_close_window(self, window):
        state.forget(window)
