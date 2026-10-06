"""The Vetting strip: the guide outside a trip. On a selection in any window, the window's layout
glides a quarter of its width aside, partly out of the window, and a strip with the
conversation glides in on the side of the selection, so the selection stays in view (Jakub).
Esc or primary+w glides it out again; opening a trip closes it. The conversation goes on from
bench to bench (chat.TRANSCRIPT)."""

import os
import time

import sublime

from . import chat, scrollbars, state
from .config import (DEFAULT_CONVERSATION_HEIGHT, GLIDE_MS, SETTINGS_FILE, STRIP_SIDE,
                     STRIP_WIDTH)
from .tint import apply_grey
from .header import BENCH as GUIDE
from .spec import repo_root
from .views import bench_font, make_side_view, match_font, to_layout

FRAME_MS = 12


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
        self.code = selection_spec(view)
        self.side = strip_side(view)
        self.saved = self.window.get_layout()
        self.status = self.note = ""
        self.closing = False
        self.origin = view
        self.head = None
        self.make_views(view)
        self.glide(0.0, 1.0, self.opened)
        self.poll()

    def make_views(self, code_view):
        self.chat = make_side_view(self.window, GUIDE, {
            "word_wrap": True, "wrap_width": 0, "sight_walk_chat": True,
            "sight_walk_strip": True, "scroll_past_end": False})
        match_font(self.chat, code_view)
        chat.start(self.chat)
        self.below = make_side_view(self.window, "", {})
        self.below.set_read_only(True)
        self.header = chat.make_header(self.window, self.chat, GUIDE)
        self.header.settings().set("sight_walk_strip", True)
        apply_grey(self.header)
        bench_font(self.chat)  # after the header, which keeps the font of code
        self.show_header()

    def opened(self):
        self.window.focus_view(self.chat)
        scrollbars.reader_focused(True)  # a focus the plugin sets is not reported as activated

    def views(self):
        return [self.header, self.chat, self.below]

    def is_open(self):
        return not self.closing and self.chat.is_valid()

    def rects(self, shown):
        """The window's own cells shifted aside by shown quarters, then the strip's header,
        conversation and an empty view below, at the heights a trip's bench has, so a trip opening
        over the strip finds the conversation where it was (Jakub). shown: 0 (out) to 1 (in)."""
        width = STRIP_WIDTH * shown
        shift = width if self.side == "left" else -width
        left = width - STRIP_WIDTH if self.side == "left" else 1.0 - width
        own = [(x0 + shift, y0, x1 + shift, y1) for x0, y0, x1, y1 in cell_rects(self.saved)]
        head, right = self.header_share(), left + STRIP_WIDTH
        split = sublime.load_settings(SETTINGS_FILE).get("default_conversation_height",
                                                         DEFAULT_CONVERSATION_HEIGHT)
        split = max(split, head + 0.05)
        return own + [(left, 0.0, right, head), (left, head, right, split), (left, split, right, 1.0)]

    def header_share(self):
        """The header's two lines as a share of the window's height, measured on the code view
        the strip was asked from: its height in px over its cell's share."""
        if self.head is None:
            cells = cell_rects(self.saved)
            _, y0, _, y1 = cells[self.window.get_view_index(self.origin)[0]]
            height = self.origin.viewport_extent()[1] / max(y1 - y0, 0.01)
            self.head = min((2 * self.header.line_height() + 10) / max(height, 1), 0.2)
        return self.head

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
        self.window.set_layout(self.saved)
        if refocus and self.origin.is_valid():
            self.window.focus_view(self.origin)
        scrollbars.reader_focused(False)
        reader = state.current_reader()
        if reader is not None:
            chat.catch_up(reader.chat)

    def poll(self):
        if self.is_open():
            chat.keep_at_bottom(self.chat)
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
        chat.show_header(self.header, GUIDE, self.note or self.status, help_mark=False)

    def folder(self):
        """Where a guide started from the strip works: the selection's repository."""
        path = self.origin.file_name() if self.origin.is_valid() else None
        if not path:
            return os.path.expanduser("~")
        return repo_root(path) or os.path.dirname(path)

    def context(self):
        return {"from": "strip", "code": self.code}

    def take_edits(self):
        return {}
