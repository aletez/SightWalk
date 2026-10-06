"""The Vetting strip: the guide outside a trip. On a selection in any window, the window's layout
glides a quarter of its width aside, partly out of the window, and a strip with the
conversation glides in on the side of the selection, so the selection stays in view (Jakub).
Esc or primary+w glides it out again; opening a trip closes it. The conversation goes on from
bench to bench (chat.TRANSCRIPT)."""

import os
import time
from html import escape as html_escape

import sublime

from . import chat, scrollbars, state
from .config import (DEFAULT_CONVERSATION_HEIGHT, GLIDE_MS, SETTINGS_FILE, STRIP_SIDE,
                     STRIP_WIDTH)
from .header import BENCH as GUIDE
from .spec import repo_root
from .views import bench_font, make_side_view, match_font, selected_text, to_layout

FRAME_MS = 12
# The filler's top is a line, the floor under the prompt, so the prompt does not seem to hang in
# the air (Jakub); its height comes from default_conversation_height.
FLOOR = 'border-top: 1px solid color(var(--foreground) alpha(0.25))'
FILLER_HTML = '<div style="height: %dpx; ' + FLOOR + '"></div>'
STATUS_HTML = ('<div style="height: %dpx; ' + FLOOR + '"></div><div style="color: '
               'color(var(--foreground) alpha(0.6)); font-style: italic">%s</div>')


def ease(t):
    """Fast at first, slowing down at the end."""
    return 1 - (1 - t) ** 3


def cell_rects(layout):
    """A layout's cells as (x0, y0, x1, y1) shares of the window."""
    cols, rows = layout["cols"], layout["rows"]
    return [(cols[a], rows[b], cols[c], rows[d]) for a, b, c, d in layout["cells"]]


def strip_side(view):
    """The side of the selection, or the one the settings name."""
    side = sublime.load_settings(SETTINGS_FILE).get("strip_side", STRIP_SIDE)
    if side in ("left", "right"):
        return side
    return "right" if selection_x(view) > 0.5 else "left"


def selection_x(view):
    """Where the selection starts, as a share of the window's width."""
    window = view.window()
    layout = window.get_layout()
    a, _, c, _ = layout["cells"][window.get_view_index(view)[0]]
    x0, x1 = layout["cols"][a], layout["cols"][c]
    sel = view.sel()[0] if view.sel() else sublime.Region(0)
    x = view.text_to_layout(sel.begin())[0] - view.viewport_position()[0]
    return x0 + (x1 - x0) * x / max(view.viewport_extent()[0], 1)


def selection_spec(view):
    """The selection as "file:begin-end", or None for a buffer that is no file."""
    if not view.file_name() or not view.sel():
        return None
    sel = view.sel()[0]
    begin, end = view.rowcol(sel.begin())[0] + 1, view.rowcol(sel.end())[0] + 1
    if sel.end() > sel.begin() and view.rowcol(sel.end())[1] == 0:
        end -= 1  # a selection ending at a line's start does not take that line
    return "%s:%d-%d" % (view.file_name(), begin, max(begin, end))


class GuideStrip:
    def __init__(self, view):
        self.window = view.window()
        self.side = strip_side(view)
        self.saved = self.window.get_layout()
        self.status = self.note = ""
        self.info_at = None  # where the filler phantom stands: (end of text, height, status bar)
        self.text = GUIDE
        self.closing = False
        self.origin = view
        self.make_views(view)
        self.glide(0.0, 1.0, self.opened)
        self.poll()

    def make_views(self, code_view):
        self.chat = make_side_view(self.window, GUIDE, {
            "word_wrap": True, "wrap_width": 0, "sight_walk_chat": True,
            "sight_walk_strip": True, "scroll_past_end": False})
        match_font(self.chat, code_view)
        chat.start(self.chat)
        bench_font(self.chat)
        self.info = sublime.PhantomSet(self.chat, "sight_walk_info")
        self.show_header()

    def opened(self):
        self.window.focus_view(self.chat)
        scrollbars.reader_focused(True)  # a focus the plugin sets is not reported as activated

    def views(self):
        return [self.chat]

    def is_open(self):
        return not self.closing and self.chat.is_valid()

    def rects(self, shown):
        """The window's own cells shifted aside by shown quarters, then the strip's conversation,
        the whole height: no header and no view below, as the user may show tabs (see
        place_info). shown: 0 (out) to 1 (in)."""
        width = STRIP_WIDTH * shown
        shift = width if self.side == "left" else -width
        left = width - STRIP_WIDTH if self.side == "left" else 1.0 - width
        own = [(x0 + shift, y0, x1 + shift, y1) for x0, y0, x1, y1 in cell_rects(self.saved)]
        return own + [(left, 0.0, left + STRIP_WIDTH, 1.0)]

    def glide(self, start, end, then=None):
        """Moves the strip from start to end (0 out, 1 in) within GLIDE_MS, eased."""
        began = time.time()

        def frame():
            t = min((time.time() - began) * 1000 / GLIDE_MS, 1.0)
            self.place(start + (end - start) * ease(t))
            if t < 1.0:
                sublime.set_timeout(frame, FRAME_MS)
            elif then is not None:
                then()

        frame()

    def place(self, shown):
        n = len(self.saved["cells"])
        self.window.set_layout(to_layout(self.rects(shown), 1.0))
        for k, view in enumerate(self.views()):
            if self.window.get_view_index(view)[0] != n + k:
                self.window.set_view_index(view, n + k, 0)

    def close(self):
        """Glides out, then gives the window its layout back. The trip's bench, if one is open,
        catches up with the conversation."""
        if self.closing:
            return
        self.closing = True
        self.glide(1.0, 0.0, self.closed)

    def vanish_later(self, ms, front):
        """Without gliding, once a trip window lies over the strip (Jakub). Closing views raises
        their window, so the trip's window (front) is brought back to the front."""
        self.closing = True

        def vanish():
            self.closed(refocus=False)
            front.bring_to_front()

        sublime.set_timeout(vanish, ms)

    def closed(self, refocus=True):
        for view in self.views():
            if view.is_valid():
                view.close()
        for view in self.window.views():
            view.erase_status("sight_walk")
        self.window.set_layout(self.saved)
        if refocus and self.origin.is_valid():
            self.window.focus_view(self.origin)
        scrollbars.reader_focused(False)
        reader = state.current_reader()
        if reader is not None:
            chat.catch_up(reader.chat)

    def poll(self):
        if self.is_open():
            filler = self.filler_px()
            chat.keep_at_bottom(self.chat, room=filler / self.chat.line_height())
            if (self.chat.size(), filler, self.window.is_status_bar_visible()) != self.info_at:
                self.place_info()
            sublime.set_timeout(self.poll, 16)

    # As a listener, like a trip

    def say(self, text, status=None, prefix="A: "):
        if prefix == "A: ":
            self.note = ""  # the answer has come
        if status is not None:
            self.status = status
        self.show_header()
        chat.say(self.chat, text, prefix)

    def note_waiting(self, note):
        self.note = note
        self.show_header()

    def show_header(self):
        """What goes on, in the status bar, or at the strip's bottom if the status bar is hidden
        (see place_info). Never in the tab: it would not fit, and a cut text worries (Jakub)."""
        state_text = self.note or self.status
        self.text = GUIDE + (" · " + state_text if state_text else "")
        for view in self.window.views():  # the status bar shows the focused view's status
            view.set_status("sight_walk", self.text)
        self.info_at = None  # placed again on the next poll

    def filler_px(self):
        """Room under the prompt, so it stands where a trip's bench has it (Jakub)."""
        split = sublime.load_settings(SETTINGS_FILE).get("default_conversation_height",
                                                         DEFAULT_CONVERSATION_HEIGHT)
        return int(self.chat.viewport_extent()[1] * (1.0 - split))

    def place_info(self):
        """Under the prompt, a phantom as the filler: a view there would get a tab of its own
        (Jakub). With the status bar hidden, its last line says what goes on. Moved as the draft
        grows."""
        end, filler, bar = self.chat.size(), self.filler_px(), self.window.is_status_bar_visible()
        html = FILLER_HTML % filler if bar else STATUS_HTML % (
            filler - self.chat.line_height(), html_escape(self.text))
        self.info.update([sublime.Phantom(sublime.Region(end), html, sublime.LAYOUT_BLOCK)])
        self.info_at = (end, filler, bar)

    def folder(self):
        """Where a guide started from the strip works: the selection's repository."""
        path = self.origin.file_name() if self.origin.is_valid() else None
        if not path:
            return os.path.expanduser("~")
        return repo_root(path) or os.path.dirname(path)

    def context(self):
        """The selection at the moment of asking, in the view it was asked from or, if the user
        selected elsewhere since, in another view the window shows (Jakub)."""
        view = self.selecting_view()
        context = {"from": "strip", "code": selection_spec(view) if view else None}
        if view is not None and selected_text(view):
            context["selected"] = selected_text(view)
        return context

    def selecting_view(self):
        shown = [self.window.active_view_in_group(g) for g in range(len(self.saved["cells"]))]
        views = [self.origin] + [v for v in shown if v is not None and v != self.origin]
        views = [v for v in views if v.is_valid()]
        chosen = next((v for v in views if selected_text(v)), None)
        return chosen or (views[0] if views else None)

    def take_edits(self):
        return {}
