"""Sublime commands and listeners. sight_walk.py imports them, which is how Sublime finds them."""

import glob
import json
import os

import sublime
import sublime_plugin

from . import asked, bridge, chat, guide, scrollbars, state
from .spec import repo_root


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


def send(owner, text):
    """A message from the trip to the agent, with what the user sees and any edited ranges."""
    state.INBOX.put(dict(owner.context(), text=text, **owner.take_edits()))
    owner.keep_transcript()
    guide.await_answer(owner)


class SightWalkSendCommand(sublime_plugin.TextCommand):
    """primary+enter on a trip's bench: the draft goes to the agent."""

    def run(self, edit):
        owner = state.reader_for(self.view.window())
        draft = None if owner is None else chat.take_draft(self.view, edit)
        if draft:
            send(owner, draft)


class SightWalkAskCommand(sublime_plugin.TextCommand):
    """Sends a fixed message, such as "Explain next.", without touching the draft."""

    def run(self, edit, text):
        owner = state.reader_for(self.view.window())
        if owner is not None:
            owner.say(text, prefix="U: ")
            send(owner, text)


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
        scrollbars.reader_focused(state.reader_for(view.window()) is not None)
        self.offer_to_browser(view)

    def on_load(self, view):
        self.offer_to_browser(view)

    def on_window_command(self, window, command_name, args):
        """primary+w (close) in a trip closes no single view: it asks to close the window
        (Jakub). The editor keeps its own primary+w, bound in the keymap."""
        if command_name in ("close", "close_file") and state.reader_for(window) is not None:
            return ("sight_walk_close_trip", None)
        return None

    def on_selection_modified(self, view):
        """Any change of a sight's selection, the caret's included. Here and not in a view
        listener: a clone gets its settings after it is made, so no view listener applies to it.
        Blank views (the strip, the fillers) take no caret (Jakub)."""
        if view.settings().get("sight_walk_blank", False):
            if len(view.sel()):
                view.sel().clear()
            return
        reader = state.reader_for(view.window())
        if reader is not None:
            reader.note_selection(view)

    def offer_to_browser(self, view):
        """A file opened from a trip's file browser becomes its sight (see Reader.take_file)."""
        reader = state.reader_for(view.window())
        if reader is not None:
            reader.take_file(view)

    def on_pre_close_window(self, window):
        state.forget(window)


class SightWalkResetSightsCommand(sublime_plugin.WindowCommand):
    """Shows the trip's sights again as the agent gave them (alpha: after an edit went wrong)."""

    def run(self):
        reader = state.reader_for(self.window) or state.current_reader()
        if reader is not None:
            reader.reset_sights()

    def is_enabled(self):
        reader = state.reader_for(self.window) or state.current_reader()
        return reader is not None and bool(reader.sights)


class SightWalkStopAnswerCommand(sublime_plugin.TextCommand):
    """Esc on the bench while an answer is on its way: stops it (see Reader.stop_answer)."""

    def run(self, edit):
        reader = state.reader_for(self.view.window())
        if reader is not None:
            reader.stop_answer()


class SightWalkCloseTripCommand(sublime_plugin.WindowCommand):
    def run(self):
        if sublime.ok_cancel_dialog("Close the Vetting Trip window?", "Close"):
            self.window.run_command("close_window")


class SightWalkOpenHolidayCommand(sublime_plugin.WindowCommand):
    """Chooses a holiday (wczasy) and opens it in a trip, the Holiday tab listing its trips
    (Jakub): every informator's trips in reading order, and the holidays written by hand
    (holidays/*.json) found in the open folders and repositories."""

    def run(self):
        found = holiday_choices()
        if not found:
            sublime.error_message("SightWalk found no informators/*.json in the open folders.")
            return
        self.window.show_quick_panel([[label, path] for label, path, _ in found],
                                     lambda i: i >= 0 and self.open(*found[i][1:]))

    def open(self, informator, holiday):
        reader = state.current_reader() or bridge.new_reader()
        reader.open_holiday(informator, holiday)
        reader.window.bring_to_front()
        scrollbars.reader_focused(True)


def holiday_choices():
    """(label, informator's file, holiday's file or None) for every holiday to choose from."""
    found = []
    for path in found_files("informators"):
        found.append((read_name(path) + ": all trips", path, None))
    for path in found_files("holidays"):
        informator = os.path.join(os.path.dirname(path), read_field(path, "informator"))
        found.append((read_name(path), os.path.normpath(informator), path))
    return found


def found_files(folder):
    """The folder/*.json files in every window's folders and its files' repositories, the kept
    conversations (*.transcripts.json) left out."""
    places = set()
    for window in sublime.windows():
        places.update(window.folders())
        places.update(repo_root(v.file_name()) for v in window.views() if v.file_name())
    found = set()
    for place in places - {None}:
        found.update(glob.glob(os.path.join(place, "**", folder, "*.json"), recursive=True))
    return sorted(f for f in found if not f.endswith(".transcripts.json"))


def read_name(path):
    return read_field(path, "name") or os.path.basename(path)


def read_field(path, key):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f).get(key, "")
    except (OSError, ValueError):
        return ""


class SightWalkTogglePanningCommand(sublime_plugin.WindowCommand):
    """ctrl+s in a trip: the wheel over Map and Holiday moves the whole trip, or the tool."""

    def run(self):
        reader = state.reader_for(self.window)
        if reader is not None:
            reader.toggle_panning()


class SightWalkStopGuideCommand(sublime_plugin.WindowCommand):
    """Ends the Vetting guide that SightWalk started in the background."""

    def run(self):
        guide.stop()

    def is_enabled(self):
        return guide.running()


class SightWalkToggleGuideCommand(sublime_plugin.TextCommand):
    """primary+g in a trip: the focus goes to the bench, and from the bench back to the sight in
    focus. Elsewhere: to the open trip's bench, or, with none open, to a new trip with no sights,
    showing the files of this file's repository (Jakub)."""

    def run(self, edit):
        reader = state.reader_for(self.view.window())
        if reader is not None:
            reader.toggle_focus(self.view)
            return
        reader = state.current_reader()
        if reader is not None:
            reader.window.bring_to_front()
            reader.window.focus_view(reader.chat)
            return
        bridge.new_reader().open_empty(self.folder())
        scrollbars.reader_focused(True)  # a new window is not reported as activated

    def folder(self):
        path = self.view.file_name()
        if path:
            return repo_root(path) or os.path.dirname(path)
        folders = self.view.window().folders()
        return folders[0] if folders else os.path.expanduser("~")


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
