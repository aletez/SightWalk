import queue
import time

import sublime

from . import chat, marks, plan, state, twin, vetting
from .config import (COLS, DEFAULT_CONVERSATION_HEIGHT, INSET, MIN_LINES_IN_CELL, POLL_MS,
                     SCROLLBAR,
                     HEADER_PAD, SETTINGS_FILE, SETTLE_MS, SETTLE_S, VETTING_LINES)
from .spec import display_path, header_text, parse_spec
from .editor import Editor
from .tint import apply_grey, apply_tint
from .views import (draw_edit_button, header_top, keep_caret_visible, write_header, draw_icons, draw_outlines, hide_chrome, make_header, make_side_view,
                    match_font, prepare_code_view, reader_layout, wait_until_loaded)


class Reader:
    def __init__(self, window):
        self.window = window
        self.segments, self.items, self.indicators = [], [], []
        self.offset = 0.0
        # window_height: the whole layout; height: the code column, VETTING_LINES shorter.
        self.window_height = self.height = self.overhead = self.lh = None
        self.ready = False
        self.expected = {}
        self.settle_until = 0.0
        self.resize_base = None
        self.inbox = queue.Queue()
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
        self.below = vetting.make(window, make_side_view, match_font, self.chat)

    # Loading

    def load(self, specs, root=None):
        self.ready = False
        self.close_panes()
        self.gutter = None  # measured on the first poll, when the panes are laid out
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
            for view in (seg.view, seg.header, seg.twin):
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
        self.items = []
        for seg in self.segments:
            top = seg.view.text_to_layout(seg.view.text_point(seg.begin - 1, 0))[1]
            content = (seg.end - seg.begin + 1) * self.lh
            twin_item = plan.Item(seg.twin, 0.0, content) if seg.twin is not None else None
            seg.code_item = plan.Item(seg.view, top, content, twin_item)
            seg.header_item = plan.Item(seg.header, header_top(seg.header), self.lh)
            self.items += [seg.header_item, seg.code_item]

    def make_twins(self):
        """Once the panes are laid out, the gutter can be measured and the twins built: a twin
        narrows its pane, so a later measurement would be wrong."""
        pane = self.segments[0].view
        column = (self.cols[2] - self.cols[1]) * self.window_width()
        self.gutter = max(column - pane.viewport_extent()[0], 1)
        for seg in self.segments:
            if twin.needed(seg.view, seg):
                text = seg.view.substr(sublime.Region(
                    seg.view.text_point(seg.begin - 1, 0),
                    seg.view.line(seg.view.text_point(seg.end - 1, 0)).b))
                seg.twin = twin.make(self.window, seg, seg.view, text)
        self.make_items()
        plan.stack(self.items, self.overhead)
        self.render()

    def start(self):
        plan.stack(self.items, self.overhead)
        self.ready = True
        self.scroll_to(0)

    def calibrate(self, callback):
        view, other = self.segments[0].view, self.segments[0].header
        self.place([(view, None)], [1], 1)

        def measure_full():
            full = view.viewport_extent()[1]
            self.place([(view, None), (other, None)], [1, 1], 2)

            def measure_half():
                half = view.viewport_extent()[1]
                # full = H - o and half = H/2 - o, solved for H and o.
                self.window_height = 2 * (full - half)
                self.overhead = self.window_height - full
                self.height = self.window_height - self.lift()
                callback()

            sublime.set_timeout(measure_half, SETTLE_MS)

        sublime.set_timeout(measure_full, SETTLE_MS)

    # Scrolling and layout

    def lift(self):
        """How far the code column ends above the window's bottom: room for the vetting pane."""
        return VETTING_LINES * self.below.line_height()

    def scroll_to(self, offset, wheel=False):
        if not self.ready:
            return
        self.offset = min(max(offset, 0.0), plan.max_offset(self.items, self.height, self.overhead))
        self.render(settle=not wheel)

    def geometry(self, total):
        """The conversation header's height and the conversation's bottom; 0, 0 until calibrated."""
        if self.overhead is None:
            return 0, 0
        top = 2 * self.chat_header.line_height() + self.overhead  # its font may differ
        settings = sublime.load_settings(SETTINGS_FILE)
        share = settings.get("default_conversation_height", DEFAULT_CONVERSATION_HEIGHT)
        return top, max(total * share, top + 2 * self.lh)

    def window_width(self):
        # The conversation has no gutter, so its text width is about its column's width.
        return max(self.chat.viewport_extent()[0] / max(self.cols[1] - self.cols[0], 0.01), 1)

    def editor_geometry(self):
        if self.editor is None:
            return None
        """The editor sits to the lower right of the panes, its top left corner set back past their
        header and gutter, so no colour of the frame touches the same colour in the editor."""
        width = self.window_width()
        header = self.editor.header.line_height() + self.overhead
        left = self.gutter_share() + INSET / width
        return header, left, self.lh + self.overhead + INSET

    def gutter_share(self):
        """The panes' gutter as a share of the window: the width of a twin's left strip. The px
        value is measured once, at calibration, where a pane still fills the code column."""
        return (self.gutter or 1) / self.window_width()

    def place(self, pairs, heights, total, overlaps=()):
        top, split = self.geometry(total)
        current = self.window.get_layout().get("cols", [])
        if top and self.editor is None and len(current) == len(COLS):
            self.cols = current  # columns the user dragged keep their widths
        share = self.gutter_share() if any(t is not None for _, t in pairs) else 0
        wide = share + SCROLLBAR / self.window_width() if share else 0
        twins = [(share, wide) if t is not None else 0 for _, t in pairs]
        self.window.set_layout(reader_layout(heights, total, overlaps, top, split, self.cols,
                                             self.editor_geometry(), twins))
        # The twin's group comes before its pane's, as its rect does.
        views = [v for pane, t in pairs for v in ((t, pane) if t is not None else (pane,))]
        self.assign_groups(views, bool(top))
        for view in views:
            self.window.focus_view(view)
        hide_chrome(self.window)

    def assign_groups(self, views, full):
        # Until calibrated, the header and the pane below wait behind the conversation.
        first = [] if self.editor is None else [self.editor.header, self.editor.view]
        n = len(first) + len(views)
        for group, view in enumerate(first + views + [self.chat]):
            self.window.set_view_index(view, group, 0)
        for k, view in enumerate([self.chat_header, self.below]):
            self.window.set_view_index(view, n + 1 + k if full else n, 0 if full else k + 1)

    def render(self, settle=True):
        cells = plan.visible_cells(self.items, self.offset, self.height, self.overhead)
        min_cell = self.overhead + MIN_LINES_IN_CELL * self.lh
        cells = plan.fill_bottom(plan.merge_slivers(cells, min_cell), self.filler, self.height, min_cell)
        shown = [item for item, _, _ in cells]
        self.expected = {}  # until scroll_views sets them, no wheel movement is read
        if settle:  # renders of the wheel's own must not swallow the wheel that follows
            self.settle_until = time.time() + SETTLE_S
        for item, top, bottom in cells:
            keep_caret_visible(item.view, plan.viewport_y(item, self.offset, top), bottom - top)
            if item.twin is not None:
                item.twin.top_layout = twin.content_top(item.twin.view)
                item.twin.y = item.y  # the twin shows the same lines at the same place
        pairs = [(item.view, item.twin.view if item.twin else None) for item in shown]
        self.place(pairs, [b - t for _, t, b in cells], self.window_height,
                   [True] * len(shown))  # every cell overlaps the next: no borders, no dead lines
        self.park_hidden(shown, sum(1 for pair in pairs for v in pair if v is not None))
        self.window.focus_view(shown[-1].view)
        self.window.focus_view(self.chat if self.editor is None else self.editor.view)
        self.fill_vetting()
        chat.show_header(self.chat_header, self.status)
        self.draw_gutter()
        self.draw_outlines()
        self.draw_edit_buttons()
        sublime.set_timeout(lambda: self.scroll_views(cells), 0)

    def park_hidden(self, shown, groups):
        shown_ids = set(item.view.id() for item in shown)
        shown_ids |= set(i.twin.view.id() for i in shown if i.twin is not None)
        parking = groups - 1 + (0 if self.editor is None else 2)  # the last code group
        twins = [i.twin for i in self.items if i.twin is not None]
        for item in self.items + twins + [self.filler]:
            if item.view.id() not in shown_ids:
                size = len(self.window.views_in_group(parking))
                self.window.set_view_index(item.view, parking, size)

    def scroll_views(self, cells):
        for item, top, _ in cells:
            for shown in (item, item.twin):
                if shown is None:
                    continue
                x = shown.view.viewport_position()[0]
                y = plan.viewport_y(shown, self.offset, top)
                shown.view.set_viewport_position((x, y), False)
                self.expected[shown.view.id()] = (shown.view, y)
        if self.editor is not None:  # its header's text sits between blank lines too
            self.editor.header.set_viewport_position((0, header_top(self.editor.header)), False)

    def read_wheel(self):
        """The wheel over a code pane, a header or the filler scrolls that view; the reader takes
        the movement over and puts the view back."""
        settling = time.time() < self.settle_until
        for view, y in self.expected.values():
            moved = view.viewport_position()[1] - y
            if not view.is_valid() or abs(moved) <= 0.5:
                continue
            if settling:
                # Right after a render Sublime moves views by itself (focus, caret): not the wheel.
                view.set_viewport_position((view.viewport_position()[0], y), False)
            else:
                self.scroll_to(self.offset + moved, wheel=True)
                return

    def fill_vetting(self):
        top, split = self.geometry(self.window_height)
        lh = self.below.line_height()
        behind = max(int((self.height - split) / lh + 0.5), 0)
        width = self.window_width()
        left = int(width * self.cols[1] / max(self.below.em_width(), 1)) - 1
        cover = int(width * (self.cols[2] - self.cols[1])) - 3 * int(self.below.em_width())
        vetting.fill(self.below, behind, left, cover, ["Vetting", "", "(the route comes here)"])

    # Gutter icons

    def draw_gutter(self):
        first, last = marks.visible_lines(self.segments, self.offset, self.height, self.lh)
        icons = marks.gutter_icons(self.indicators, first, last)
        for index, seg in enumerate(self.segments):
            mine = {line: icon for (i, line), icon in icons.items() if i == index and line}
            draw_icons(seg.view, seg.icons, mine)
            seg.icons = mine
            # The header is a one-line view, so its line 0 is drawn on line 1.
            header = {HEADER_PAD + 1: icons[(index, 0)]} if (index, 0) in icons else {}
            draw_icons(seg.header, seg.header_icons, header)
            seg.header_icons = header

    def draw_outlines(self):
        for index, seg in enumerate(self.segments):
            lines = set(m["line"] for m in self.indicators if m["seg"] == index)
            if lines != seg.outlines:
                draw_outlines(seg.view, lines)
                if seg.twin is not None:  # its first content line is line 2
                    draw_outlines(seg.twin, set(line - seg.begin + 2 for line in lines))
                seg.outlines = lines

    def poll(self):
        if state.READERS.get(self.window.id()) is not self or not self.chat.is_valid():
            return
        chat.keep_at_bottom(self.chat)
        chat.show_header(self.chat_header, self.status)  # rewraps when the column is resized
        if self.ready:
            if self.gutter is None:
                self.make_twins()
                return sublime.set_timeout(self.poll, POLL_MS)
            self.follow_resize()
            self.read_wheel()
        sublime.set_timeout(self.poll, POLL_MS)

    def follow_resize(self):
        """A panel or a window resize changes the room. The conversation and the vetting pane
        together span the column under the fixed header, so their heights change one to one."""
        size = self.chat.viewport_extent()[1] + self.below.viewport_extent()[1]
        if self.resize_base is None:
            self.resize_base = (size, self.window_height)
        elif abs(size - self.resize_base[0] - (self.window_height - self.resize_base[1])) > 0.5:
            self.window_height = self.resize_base[1] + size - self.resize_base[0]
            self.height = self.window_height - self.lift()
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
        write_header(seg.header, header_text(seg))

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
