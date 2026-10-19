"""Sublime commands and listeners. sight_walk.py imports them, which is how Sublime finds them."""

import glob
import json
import os

import sublime
import sublime_plugin

from . import subl_asked, subl_executor, subl_chat, subl_guide, marks, subl_scrollbars, state, subl_tint, subl_vetting
from .config import SETTINGS_FILE
from .spec import repo_root
from .words import trips_count, word


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


def send(owner, text, here=None):
    """A message from the trip to the agent, with what the user sees and any edited ranges, and
    here: the places selected when it was sent, if the user linked no words (see subl_links)."""
    context = owner.context()
    if here:  # the selection is what "this" means: the sight in focus would only blur it
        context = {"here": here, "visible": context.get("visible", [])}
    state.INBOX.put(dict(context, text=text, **owner.take_edits()))
    owner.keep_transcript()
    subl_guide.await_answer(owner)


class SightWalkSendCommand(sublime_plugin.TextCommand):
    """primary+enter on a trip's bench: the draft goes to the agent."""

    def run(self, edit):
        owner = state.reader_for(self.view.window())
        if owner is None:
            return
        tagged = owner.links.tagged(self.view)  # the guide gets the links as <here> tags
        label = len(subl_chat.TRANSCRIPT)  # where the message's "U:" will stand
        if subl_chat.take_draft(self.view, edit):
            send(owner, tagged, owner.links.ask(label))


class SightWalkSelectColourSchemeCommand(sublime_plugin.WindowCommand):
    """One colour scheme for every view of every trip (Jakub): general, light or dark, the
    list for light or dark holding only such schemes, previewed live in all trips; Enter
    saves it to the SightWalk settings, Esc gives the old one back."""

    def run(self):
        kinds = [word("scheme_general"), word("scheme_light"), word("scheme_dark")]
        self.window.show_quick_panel(kinds, self.pick_kind)

    def pick_kind(self, kind):
        if kind < 0:
            return
        self.key = subl_tint.SCHEME_KEYS[kind]
        wanted = {1: False, 2: True}.get(kind)
        self.schemes = [p for p in all_schemes()
                        if wanted is None or subl_tint.is_dark(p) in (wanted, None)]
        current = sublime.load_settings(SETTINGS_FILE).get(self.key)
        selected = next((i for i, p in enumerate(self.schemes) if p == current), -1)
        sublime.set_timeout(lambda: self.window.show_quick_panel(
            [scheme_item(p) for p in self.schemes], self.done, selected_index=selected,
            on_highlight=self.preview), 0)

    def preview(self, index):
        subl_tint.PREVIEW = self.schemes[index]
        subl_tint.refresh_all()

    def done(self, index):
        subl_tint.PREVIEW = None
        if index >= 0:
            settings = sublime.load_settings(SETTINGS_FILE)
            settings.set(self.key, self.schemes[index])
            sublime.save_settings(SETTINGS_FILE)
        subl_tint.refresh_all()


def all_schemes():
    found = sublime.find_resources("*.sublime-color-scheme") + sublime.find_resources("*.tmTheme")
    return sorted({p for p in found if "/User/SightWalk/" not in p},  # not the tinted ones
                  key=lambda path: os.path.basename(path).lower())


def scheme_item(path):
    name = os.path.splitext(os.path.basename(path))[0]
    return [name, path.split("/")[1] if path.count("/") > 1 else ""]


class SightWalkCycleSightsCommand(sublime_plugin.WindowCommand):
    """ctrl+tab and ctrl+shift+tab in a trip: the focus round the sights on screen (Jakub)."""

    def run(self, step=1):
        reader = state.reader_for(self.window)
        if reader is not None and reader.ready:
            reader.cycle(step)


class SightWalkLinkCommand(sublime_plugin.TextCommand):
    """primary+p (Jakub): links words on the bench to places in the code, from either side (see
    subl_links)."""

    def run(self, edit):
        reader = state.reader_for(self.view.window())
        if reader is None:
            return
        if self.view == reader.chat:
            reader.links.link_from_bench(self.view)
        elif reader.sight_of(self.view) is not None:
            reader.links.link_from_code()


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
        line = min(max(line, sight.begin), sight.end)
        # After this text command: the window's layout changed inside it leaves the editor's
        # cell empty (Jakub saw an empty frame; the header's button worked).
        sublime.set_timeout(lambda: reader.open_editor(index, line), 0)


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
            subl_chat.show_help(self.view, point)


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
        sublime.set_timeout(lambda: subl_chat.shade_variables(self.view), 50)  # after highlighting
        reader = state.reader_for(self.view.window())
        if reader is not None:
            reader.bench_edited()  # a move it causes is no wheel step
            reader.links.prune(self.view)  # linked words deleted

    def on_selection_modified(self):
        """Words selected in the draft wait for code to link to (see subl_links)."""
        reader = state.reader_for(self.view.window())
        if reader is not None:
            reader.links.note_bench(self.view)

    def on_post_text_command(self, command_name, args):
        """What leaves the bench by copying leaves without the invisible operators around names
        (see marks.untag). A click into linked words shows their places (see subl_links)."""
        if command_name in ("copy", "cut"):
            sublime.set_clipboard(marks.clean(sublime.get_clipboard()))
        reader = state.reader_for(self.view.window())
        if command_name == "drag_select" and reader is not None:
            shown = (reader.links.follow(self.view) or reader.links.follow_question(self.view)
                     or reader.follow_frame(self.view) or reader.follow_label(self.view))
            if not shown:
                reader.links.forget_shown()


class SightWalkWindowListener(sublime_plugin.EventListener):
    def on_activated(self, view):
        subl_scrollbars.reader_focused(state.reader_for(view.window()) is not None)
        self.offer_to_browser(view)

    def on_load(self, view):
        self.offer_to_browser(view)

    def on_window_command(self, window, command_name, args):
        """primary+w (close) in a trip closes no single view: it asks to close the window
        (Jakub). The editor keeps its own primary+w, bound in the keymap. next_view and
        prev_view go round the sights on screen."""
        reader = state.reader_for(window)
        if command_name in ("close", "close_file") and reader is not None:
            return ("sight_walk_close_trip", None)
        # ctrl+tab goes round the sights on screen, whatever keymap binds it to next_view (a
        # user's keymap wins over the plugin's, Jakub's binds ctrl+tab so).
        steps = {"next_view": 1, "prev_view": -1}
        if command_name in steps and reader is not None and reader.editor is None:
            return ("sight_walk_cycle_sights", {"step": steps[command_name]})
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

    def on_post_text_command(self, view, command_name, args):
        """A click into a linked place in a sight selects the words that refer to it (see
        subl_links)."""
        reader = state.reader_for(view.window())
        index = None if reader is None else reader.sight_of(view)
        if command_name == "drag_select" and index is not None:
            reader.links.follow_code(view, index)
        elif command_name == "drag_select" and reader is not None:
            reader.editor_header_clicked(view)

    def offer_to_browser(self, view):
        """A file opened from a trip's file browser becomes its sight (see Reader.take_file)."""
        reader = state.reader_for(view.window())
        if reader is not None:
            reader.take_file(view)

    def on_pre_close_window(self, window):
        state.forget(window)
        sublime.set_timeout(clear_schemes_if_unused, 2000)  # once the window's views are gone


def clear_schemes_if_unused():
    """The written colour schemes no trip uses go (Jakub); a trip writes them anew."""
    subl_tint.clear_schemes()


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
        if sublime.ok_cancel_dialog(word("close_trip"), word("close")):
            self.window.run_command("close_window")


class SightWalkOpenTourCommand(sublime_plugin.WindowCommand):
    """Chooses a tour (turnus) and opens it in a trip, the Tour tab listing its trips
    (Jakub): every informator's trips in reading order, and the tours written by hand
    (tours/*.json) found in the open folders and repositories."""

    def run(self):
        found = tour_choices()
        if not found:
            sublime.error_message(word("no_informators"))
            return
        self.window.show_quick_panel([[label, trips_count(n)] for label, n, _, _ in found],
                                     lambda i: i >= 0 and self.open(*found[i][2:]))

    def open(self, informator, tour):
        reader = state.current_reader() or subl_executor.new_reader()
        reader.open_tour(informator, tour)
        reader.window.bring_to_front()
        subl_scrollbars.reader_focused(True)


def tour_choices():
    """(label, number of trips, informator's file, tour's file or None) for every tour to choose
    from, each labelled "informator: tour", its number of trips under it (Jakub)."""
    found = []
    for path in found_files("informators"):
        found.append((read_name(path) + ": " + word("all_trips"), len(read_field(path, "trips")),
                      path, None))
    for path in found_files("tours"):
        informator = os.path.normpath(os.path.join(os.path.dirname(path),
                                                   read_field(path, "informator")))
        # Named after its informator too, like the whole one (Jakub).
        found.append((read_name(informator) + ": " + read_name(path),
                      len(read_field(path, "trips")), informator, path))
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


class SightWalkSwitchLanguageCommand(sublime_plugin.ApplicationCommand):
    """The plugin's words in English or Polish (Jakub): the setting language, switched."""

    def run(self):
        settings = sublime.load_settings(SETTINGS_FILE)
        settings.set("language", "en" if settings.get("language", "en") == "pl" else "pl")
        sublime.save_settings(SETTINGS_FILE)


class SightWalkZoomMapCommand(sublime_plugin.TextCommand):
    """primary+= / primary+minus / primary+0 on the Map: larger, smaller, as wide as the pane."""

    def run(self, edit, how):
        subl_vetting.zoom(self.view, how)


class SightWalkTogglePanningCommand(sublime_plugin.WindowCommand):
    """primary+s in a trip: the wheel over the bench, Map and Tour moves the whole trip, or them."""

    def run(self):
        reader = state.reader_for(self.window)
        if reader is not None:
            reader.toggle_panning()


class SightWalkStopGuideCommand(sublime_plugin.WindowCommand):
    """Ends the Vetting guide that SightWalk started in the background."""

    def run(self):
        subl_guide.stop()

    def is_enabled(self):
        return subl_guide.running()


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
        subl_executor.new_reader().open_empty(self.folder())
        subl_scrollbars.reader_focused(True)  # a new window is not reported as activated

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
            subl_asked.show_popup(self.view, point)


class SightWalkToggleSentinelsCommand(sublime_plugin.TextCommand):
    """References without sentinel: their underlines on or off (see asked)."""

    def run(self, edit):
        subl_asked.toggle()


COMPARED_FONTS = ("Helvetica Neue", "Avenir Next", "Charter", "Iowan Old Style", "Georgia",
                  "Palatino")


class SightWalkCompareFontsCommand(sublime_plugin.ApplicationCommand):
    """A window of six panes with the bench's conversation, each in another font (Jakub), to
    choose bench_font_face."""

    def run(self):
        sample = (subl_chat.TRANSCRIPT or kept_conversation())[-2500:]
        sublime.run_command("new_window")
        window = sublime.active_window()
        window.set_layout({"cols": [0, 1 / 3, 2 / 3, 1], "rows": [0, 0.5, 1],
                           "cells": [[c, r, c + 1, r + 1] for r in range(2) for c in range(3)]})
        for group, face in enumerate(COMPARED_FONTS):
            window.focus_group(group)
            view = window.new_file(syntax=subl_chat.SYNTAX)
            view.set_scratch(True)
            view.set_name(face)
            view.settings().update({"font_face": face, "word_wrap": True, "gutter": False})
            view.run_command("append", {"characters": face + "\n\n" + sample})


def kept_conversation():
    """The longest conversation kept beside an informator in the open folders, for samples."""
    texts = [""]
    for window in sublime.windows():
        for folder in window.folders():
            for path in glob.glob(os.path.join(folder, "**", "*.transcripts.json"), recursive=True):
                with open(path, encoding="utf-8") as f:
                    texts += list(json.load(f).values())
    return max(texts, key=len)
