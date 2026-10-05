import queue

import sublime

from . import chat, marks, plan, state
from .config import MIN_LINES_IN_CELL, PAD_ROWS, POLL_MS, SETTLE_MS
from .spec import header_text, parse_spec
from .tint import apply_tint
from .views import (draw_icons, draw_outlines, hide_chrome, make_header, make_side_view,
                    match_font, prepare_code_view, reader_layout, wait_until_loaded)


class Reader:
    def __init__(self, window):
        self.window = window
        self.segments, self.items, self.indicators = [], [], []
        self.offset = 0.0
        self.height = self.overhead = self.lh = None
        self.ready = False
        self.anchor = 0.0
        self.strip_cache = None
        self.strip_extent = None
        self.inbox = queue.Queue()
        self.strip = make_side_view(window, "Scroll", {"word_wrap": False})
        self.strip.set_read_only(True)
        self.filler = plan.Item(make_side_view(window, "", {}), 0.0, 0.0)
        self.filler.view.set_read_only(True)
        self.chat = make_side_view(window, "Conversation", {
            "word_wrap": True, "wrap_width": 0, "sight_walk_chat": True, "scroll_past_end": True})
        chat.start(self.chat)

    # Loading

    def load(self, specs, root=None):
        self.ready = False
        self.close_panes()
        self.segments = [plan.Segment(spec, *parse_spec(spec, root)) for spec in specs]
        self.indicators = []
        paths = list(dict.fromkeys(seg.path for seg in self.segments))
        originals = {path: self.window.open_file(path) for path in paths}
        wait_until_loaded(list(originals.values()), lambda: self.build(originals))

    def close_panes(self):
        for seg in self.segments:
            for view in (seg.view, seg.header):
                if view is not None and view.is_valid():
                    view.close()

    def build(self, originals):
        used = set()
        for seg in self.segments:
            seg.view = prepare_code_view(self.window, originals[seg.path], seg.path in used)
            seg.header = make_header(self.window, header_text(seg), seg.view)
            used.add(seg.path)
        for path in originals:
            mine = [s for s in self.segments if s.path == path]
            apply_tint([s.view for s in mine], [s.header for s in mine], path)
        self.make_items()
        if self.height is None:
            self.calibrate(self.start)
        else:
            self.start()

    def make_items(self):
        first = self.segments[0].view
        self.lh = first.line_height()
        match_font(self.strip, first)
        self.items = []
        for seg in self.segments:
            top = seg.view.text_to_layout(seg.view.text_point(seg.begin - 1, 0))[1]
            seg.code_item = plan.Item(seg.view, top, (seg.end - seg.begin + 1) * self.lh)
            seg.header_item = plan.Item(seg.header, 0.0, self.lh)
            self.items += [seg.header_item, seg.code_item]

    def start(self):
        plan.stack(self.items, self.overhead)
        self.ready = True
        self.scroll_to(0)

    def calibrate(self, callback):
        view, other = self.segments[0].view, self.segments[0].header
        self.place([1], 1, [view])

        def measure_full():
            full = view.viewport_extent()[1]
            self.place([1, 1], 2, [view, other])

            def measure_half():
                half = view.viewport_extent()[1]
                # full = H - o and half = H/2 - o, solved for H and o.
                self.height = 2 * (full - half)
                self.overhead = self.height - full
                self.strip_extent = self.strip.viewport_extent()[1]
                callback()

            sublime.set_timeout(measure_half, SETTLE_MS)

        sublime.set_timeout(measure_full, SETTLE_MS)

    # Scrolling and layout

    def scroll_to(self, offset):
        if not self.ready:
            return
        self.offset = min(max(offset, 0.0), plan.max_offset(self.items, self.height, self.overhead))
        self.render()

    def place(self, heights, total, views, overlaps=()):
        self.window.set_layout(reader_layout(heights, total, overlaps))
        n = len(views)
        for group, view in enumerate(views):
            self.window.set_view_index(view, group, 0)
        self.window.set_view_index(self.strip, n, 0)
        self.window.set_view_index(self.chat, n + 1, 0)
        for view in views:
            self.window.focus_view(view)
        hide_chrome(self.window)

    def render(self):
        cells = plan.visible_cells(self.items, self.offset, self.height, self.overhead)
        min_cell = self.overhead + MIN_LINES_IN_CELL * self.lh
        cells = plan.fill_bottom(plan.merge_slivers(cells, min_cell), self.filler, self.height, min_cell)
        shown = [item for item, _, _ in cells]
        headers = [seg.header_item for seg in self.segments]
        self.place([b - t for _, t, b in cells], self.height, [item.view for item in shown],
                   [item in headers for item in shown])
        self.park_hidden(shown)
        self.window.focus_view(shown[-1].view)
        self.window.focus_view(self.chat)
        self.draw_strip()
        self.draw_gutter()
        self.draw_outlines()
        sublime.set_timeout(lambda: self.scroll_views(cells), 0)

    def park_hidden(self, shown):
        shown_ids = set(item.view.id() for item in shown)
        parking = len(shown) - 1
        for item in self.items + [self.filler]:
            if item.view.id() not in shown_ids:
                size = len(self.window.views_in_group(parking))
                self.window.set_view_index(item.view, parking, size)

    def scroll_views(self, cells):
        for item, top, _ in cells:
            item.view.set_viewport_position((0, plan.viewport_y(item, self.offset, top)), False)
        self.strip.set_viewport_position((0, self.anchor), False)

    # Scroll strip, kept for the wheel

    def draw_strip(self):
        text = marks.strip_text(int(self.height // self.lh), PAD_ROWS)
        self.anchor = PAD_ROWS * self.strip.line_height()
        if text != self.strip_cache:
            self.strip_cache = text
            self.strip.run_command("sight_walk_replace", {"text": text})
        # Reset at once, so the poll never mistakes a redraw for a wheel movement.
        self.strip.set_viewport_position((0, self.anchor), False)

    # Gutter icons

    def draw_gutter(self):
        first, last = marks.visible_lines(self.segments, self.offset, self.height, self.lh)
        icons = marks.gutter_icons(self.indicators, first, last)
        for index, seg in enumerate(self.segments):
            mine = {line: icon for (i, line), icon in icons.items() if i == index and line}
            draw_icons(seg.view, seg.icons, mine)
            seg.icons = mine
            # The header is a one-line view, so its line 0 is drawn on line 1.
            header = {1: icons[(index, 0)]} if (index, 0) in icons else {}
            draw_icons(seg.header, seg.header_icons, header)
            seg.header_icons = header

    def draw_outlines(self):
        for index, seg in enumerate(self.segments):
            lines = set(m["line"] for m in self.indicators if m["seg"] == index)
            if lines != seg.outlines:
                draw_outlines(seg.view, lines)
                seg.outlines = lines

    def poll(self):
        if state.READERS.get(self.window.id()) is not self or not self.strip.is_valid():
            return
        chat.keep_at_middle(self.chat)
        if self.ready:
            self.follow_resize()
            y = self.strip.viewport_position()[1]
            if abs(y - self.anchor) > 0.5:
                self.strip.set_viewport_position((0, self.anchor), False)
                self.scroll_to(self.offset + (y - self.anchor))
        sublime.set_timeout(self.poll, POLL_MS)

    def follow_resize(self):
        # The strip spans the whole column, so its height changes one to one with the room for
        # the panes when a panel opens or closes or the window is resized.
        extent = self.strip.viewport_extent()[1]
        if abs(extent - self.strip_extent) > 0.5:
            self.height += extent - self.strip_extent
            self.strip_extent = extent
            self.render()

    def point(self, new_marks, reveal=True, clear=True):
        resolved = marks.resolve_marks(self.segments, new_marks)
        self.indicators = resolved if clear else self.indicators + resolved
        ys = [marks.line_y(self.segments[m["seg"]], m["line"], self.lh) for m in resolved]
        bottom = self.offset + self.height - 2 * self.lh
        if reveal and ys and not all(self.offset <= y <= bottom for y in ys):
            self.scroll_to((min(ys) + max(ys)) / 2 - self.height / 2)
        else:
            self.render()

    # Conversation

    def say(self, text):
        chat.say(self.chat, text)

    def context(self):
        if not self.ready:
            return {"focus": None, "visible": []}
        focus = plan.focus_segment(self.segments, self.offset, self.height, self.overhead)
        return {"focus": focus.spec if focus else None,
                "visible": plan.visible_specs(self.segments, self.offset, self.height)}
