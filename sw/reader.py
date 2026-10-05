import queue

import sublime

from . import chat, marks, plan, state
from .config import (COLS, DEFAULT_CONVERSATION_HEIGHT, INSET, MIN_LINES_IN_CELL, PAD_ROWS, POLL_MS,
                     SETTINGS_FILE, SETTLE_MS)
from .spec import display_path, header_text, parse_spec
from .editor import Editor
from .tint import apply_grey, apply_tint
from .views import (draw_edit_button, draw_icons, draw_outlines, hide_chrome, make_header, make_side_view,
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
            "word_wrap": True, "wrap_width": 0, "sight_walk_chat": True, "scroll_past_end": False})
        chat.start(self.chat)
        # The conversation's header plays the role of a tab, since tabs are off.
        self.status = ""
        self.cols = list(COLS)
        self.editor = None
        self.edits = []
        self.chat_header = chat.make_header(window, self.chat)
        apply_grey(self.chat_header)
        # Below the conversation: room for what comes next (ledger, route map).
        self.below = make_side_view(window, "", {})
        self.below.set_read_only(True)

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
        if self.editor is not None:
            self.editor.header.close()
            self.editor.view.close()
            self.editor = None
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

    def geometry(self, total):
        """The conversation header's height and the conversation's bottom; 0, 0 until calibrated."""
        if self.overhead is None:
            return 0, 0
        top = 2 * self.chat_header.line_height() + self.overhead  # its font may differ
        settings = sublime.load_settings(SETTINGS_FILE)
        share = settings.get("default_conversation_height", DEFAULT_CONVERSATION_HEIGHT)
        return top, max(total * share, top + 2 * self.lh)

    def editor_geometry(self):
        if self.editor is None:
            return None
        """The editor sits to the lower right of the panes, its top left corner set back past their
        header and gutter, so no colour of the frame touches the same colour in the editor."""
        # The strip's text start is in window coordinates and gives the window's width; a pane's
        # comes back relative to the pane (measured: 66 px), which is its gutter.
        strip_x = self.strip.text_to_window(self.strip.visible_region().a)[0]
        width = max(strip_x / max(self.cols[2], 0.01), 1)
        pane = self.segments[0].view
        text_x = pane.text_to_window(pane.visible_region().a)[0]
        gutter = text_x if text_x < self.cols[1] * width else text_x - self.cols[1] * width
        header = self.editor.header.line_height() + self.overhead
        left = (gutter + INSET) / width
        return header, left, self.lh + self.overhead + INSET

    def place(self, heights, total, views, overlaps=()):
        top, split = self.geometry(total)
        current = self.window.get_layout().get("cols", [])
        if top and self.editor is None and len(current) == 4:
            self.cols = current  # columns the user dragged keep their widths
        self.window.set_layout(reader_layout(heights, total, overlaps, top, split, self.cols,
                                             self.editor_geometry()))
        self.assign_groups(views, bool(top))
        for view in views:
            self.window.focus_view(view)
        hide_chrome(self.window)

    def assign_groups(self, views, full):
        # Until calibrated, the header and the pane below wait behind the conversation.
        first = [] if self.editor is None else [self.editor.header, self.editor.view]
        n = len(first) + len(views)
        for group, view in enumerate(first + views + [self.strip, self.chat]):
            self.window.set_view_index(view, group, 0)
        for k, view in enumerate([self.chat_header, self.below]):
            self.window.set_view_index(view, n + 2 + k if full else n + 1, 0 if full else k + 1)

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
        self.window.focus_view(self.chat if self.editor is None else self.editor.view)
        self.draw_strip()
        chat.show_header(self.chat_header, self.status)
        self.draw_gutter()
        self.draw_outlines()
        self.draw_edit_buttons()
        sublime.set_timeout(lambda: self.scroll_views(cells), 0)

    def park_hidden(self, shown):
        shown_ids = set(item.view.id() for item in shown)
        parking = len(shown) - 1 + (0 if self.editor is None else 2)  # the last code group
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
        chat.keep_at_bottom(self.chat)
        chat.show_header(self.chat_header, self.status)  # rewraps when the column is resized
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

    # Editing

    def draw_edit_buttons(self):
        for index, seg in enumerate(self.segments):
            draw_edit_button(seg.header, header_text(seg),
                             lambda _, i=index: self.open_editor(i, self.segments[i].begin))

    def open_editor(self, index, line):
        if self.editor is None:
            if self.segments[index].view.is_dirty():
                # Don't Save could not tell those changes from the editor's and would revert them.
                sublime.message_dialog("%s has unsaved changes in another view. Save or discard "
                                       "them there first." % display_path(self.segments[index].path))
                return
            self.editor = Editor(self, index, line)
        self.render()

    def close_editor(self):
        self.editor.close(self.editor_closed)

    def editor_closed(self, ranges, lines):
        """After Esc. If the file is still dirty, the user chose Don't Save: the panes go back to
        the file on disk. Otherwise the reader takes the edits over and tells the agent."""
        pane = next(s.view for s in self.segments if s.path == self.editor.path)
        self.editor = None
        if pane.is_dirty():
            pane.run_command("revert")
            ranges, lines = {}, {}
        pane.set_read_only(True)  # read-only belongs to the buffer
        for k, line in lines.items():
            self.indicators[k]["line"] = line
        for i, (begin, end) in ranges.items():
            self.move_range(self.segments[i], begin, end)
        self.make_items()
        plan.stack(self.items, self.overhead)
        self.render()

    def move_range(self, seg, begin, end):
        if (begin, end) == (seg.begin, seg.end):
            return
        self.edits.append("%s, now %d-%d" % (seg.spec, begin, end))
        seg.spec = "%s:%d-%d" % (seg.spec.rpartition(":")[0], begin, end)
        seg.begin, seg.end = begin, end
        seg.header.run_command("sight_walk_replace", {"text": header_text(seg)})

    def take_edits(self):
        """Ranges the user changed in the editor, for the agent's next message."""
        edits, self.edits = self.edits, []
        return {"edited": edits} if edits else {}

    # Conversation

    def say(self, text, status=None, prefix="A: "):
        if status is not None:
            self.status = status
            chat.show_header(self.chat_header, self.status)
        chat.say(self.chat, text, prefix)

    def context(self):
        if not self.ready:
            return {"focus": None, "visible": []}
        focus = plan.focus_segment(self.segments, self.offset, self.height, self.overhead)
        return {"focus": focus.spec if focus else None,
                "visible": plan.visible_specs(self.segments, self.offset, self.height)}
