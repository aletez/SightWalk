import queue
import time

import sublime

from . import chat, marks, plan, state, twin, vetting
from .config import (COLS, DEFAULT_CONVERSATION_HEIGHT, INSET, MIN_LINES_IN_CELL,
                     OVERLAP, POLL_MS, SCROLLBAR, SETTINGS_FILE, SETTLE_MS, SETTLE_S, TAIL_LINES,
                     WHEEL_MS)
from .spec import display_path, header_text, parse_spec
from .editor import Editor
from .tint import apply_grey, apply_tint
from .views import (draw_edit_button, keep_caret_visible, write_header, draw_icons, draw_outlines, hide_chrome, make_header, make_side_view,
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
        self.strip_tops = {}
        self.inbox = queue.Queue()
        self.filler = plan.Item(make_side_view(window, "", {}), 0.0, 0.0)
        self.filler.view.set_read_only(True)
        # Below the last pane, an invisible strip that scrolls the column: the panes can leave
        # the screen upwards and the wheel still brings them back.
        self.tail = make_side_view(window, "", {})
        self.tail.run_command("sight_walk_replace", {"text": "\n" * (2 * TAIL_LINES)})
        self.tail.set_read_only(True)
        self.grouped = set()
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
            for view in (seg.view, seg.header, seg.twin, seg.corner):
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
            seg.header_item = plan.Item(seg.header, 0.0, self.lh)
            self.items += [seg.header_item, seg.code_item]

    def make_twins(self):
        """Once the panes are laid out, the gutter can be measured and the twins built: a twin
        narrows its pane, so a later measurement would be wrong."""
        pane = self.segments[0].view
        column = (self.cols[2] - self.cols[1]) * self.window_width()
        self.gutter = max(column - pane.viewport_extent()[0], 1)
        for seg in self.segments:
            text = seg.view.substr(sublime.Region(
                seg.view.text_point(seg.begin - 1, 0),
                seg.view.line(seg.view.text_point(seg.end - 1, 0)).b))
            seg.twin = twin.make(self.window, seg, seg.view, text)
            if seg.begin == 1:
                seg.corner = make_side_view(self.window, "", {})
                seg.corner.set_read_only(True)
        self.make_items()
        plan.stack(self.items, self.overhead)
        self.render()

    def start(self):
        plan.stack(self.items, self.overhead)
        self.ready = True
        self.scroll_to(0)

    def calibrate(self, callback):
        view, other = self.segments[0].view, self.segments[0].header
        self.place([(self.cols[1], 0.0, self.cols[2], 1)], [view], 1)

        def measure_full():
            full = view.viewport_extent()[1]
            self.place([(self.cols[1], 0.0, self.cols[2], 1),
                        (self.cols[1], 1, self.cols[2], 2)], [view, other], 2)

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
        """The code column reaches the window's bottom (the vetting pane is no L any more)."""
        return 0

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

    def column_rects(self, cells):
        """The code column, in drawing order (earlier is on top): every header lies over the code
        only, and the gutter strip reaches up beside it, so the gutters make one band and only
        they take the wheel. Every cell overlaps the next: no border lines, no dead strip."""
        visible = self.gutter_share()
        wide = visible + SCROLLBAR / self.window_width()
        left, right = self.cols[1], self.cols[2]
        above = {id(seg.code_item): seg for seg in self.segments}
        headers = set(id(seg.header_item) for seg in self.segments)
        rects, views = [], []
        for i, (item, top, bottom) in enumerate(cells):
            end = bottom + (OVERLAP if i + 1 < len(cells) else 0)
            if item is self.filler:  # below the last pane: an invisible strip, down to the bottom
                rects += [(left + visible, top, right, end), (left, top, left + wide, end)]
                views += [item.view, self.tail]
            elif item.twin is None:  # a header
                rects.append((left + visible if id(item) in headers else left, top, right, end))
                views.append(item.view)
            else:
                self.pane_rects(cells, i, above[id(item)], (left, visible, wide, right, end),
                                rects, views)
        return rects, views

    def pane_rects(self, cells, i, seg, edges, rects, views):
        """The twin, then the strip, which reaches under it (hiding its scroll bar) and up beside
        the header. A strip at line 1 cannot scroll above it: there an empty view in the band's
        colour covers the corner instead."""
        left, visible, wide, right, end = edges
        item, top = cells[i][0], cells[i][1]
        rects.append((left + visible, top, right, end))
        views.append(item.twin.view)
        header_top = cells[i - 1][1] if i and cells[i - 1][0] is seg.header_item else None
        start = header_top if header_top is not None and seg.begin > 1 else top
        if header_top is not None and seg.begin == 1:
            rects.append((left, header_top, left + visible, top + OVERLAP))
            views.append(seg.corner)
        rects.append((left, start, left + wide, end))
        views.append(item.view)
        # Its cell may begin beside the header: it scrolls from there, so the numbers keep lining
        # up with the twin's lines.
        self.strip_tops[item.view.id()] = start

    def place(self, rects, views, total):
        top, split = self.geometry(total)
        current = self.window.get_layout().get("cols", [])
        if top and self.editor is None and len(current) == len(COLS):
            self.cols = current  # columns the user dragged keep their widths
        self.window.set_layout(reader_layout(rects, total, top, split, self.cols,
                                             self.editor_geometry()))
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
        self.settle_until = time.time() + SETTLE_S
        for item, top, bottom in cells:
            keep_caret_visible(item.view, plan.viewport_y(item, self.offset, top), bottom - top)
            if item.twin is not None:
                item.twin.top_layout = twin.content_top(item.twin.view)
                item.twin.y = item.y  # the twin shows the same lines at the same place
        self.strip_tops = {}
        for seg in self.segments:  # the corner takes the header's band colour, once it is known
            if seg.corner is not None:
                band = seg.header.settings().get("color_scheme")
                if seg.corner.settings().get("color_scheme") != band:
                    seg.corner.settings().set("color_scheme", band)
        rects, views = self.column_rects(cells)
        self.grouped = set(v.id() for v in views)
        self.place(rects, views, self.window_height)
        self.park_hidden(shown, len(views))
        # Parked views join the last code group; its own view must stay the one shown there.
        self.window.focus_view(views[-1])
        self.window.focus_view(shown[-1].view)
        self.window.focus_view(self.chat if self.editor is None else self.editor.view)
        self.draw_gutter()
        self.draw_outlines()
        if settle:  # unchanged by scrolling, and each one writes text or phantoms
            self.fill_vetting()
            chat.show_header(self.chat_header, self.status)
            self.draw_edit_buttons()
        # Placing the views focuses them, which can scroll one to its caret: put them back at
        # once, and again on the next tick, when Sublime has finished laying them out.
        self.scroll_views(cells)
        sublime.set_timeout(lambda: self.scroll_views(cells), 0)

    def park_hidden(self, shown, groups):
        shown_ids = set(item.view.id() for item in shown)
        shown_ids |= set(i.twin.view.id() for i in shown if i.twin is not None)
        parking = groups - 1 + (0 if self.editor is None else 2)  # the last code group
        twins = [i.twin.view for i in self.items if i.twin is not None]
        extras = [self.tail] + [s.corner for s in self.segments if s.corner is not None]
        placed = set(v.id() for v in self.window.views_in_group(parking))
        for view in [i.view for i in self.items] + twins + [self.filler.view] + extras:
            # A view shown in some group is in the groups list; the rest wait behind the last.
            if view.id() not in shown_ids and view.id() not in self.grouped:
                size = len(self.window.views_in_group(parking))
                self.window.set_view_index(view, parking, size)

    def scroll_views(self, cells):
        for item, top, _ in cells:
            for shown in (item, item.twin):
                if shown is None:
                    continue
                x = shown.view.viewport_position()[0]
                y = plan.viewport_y(shown, self.offset, top)
                if shown is item:
                    y = plan.viewport_y(shown, self.offset, self.strip_tops.get(shown.view.id(), top))
                shown.view.set_viewport_position((x, y), False)
                if shown is item.twin:
                    continue  # the code's own scrolling is free until the next render
                if item.twin is None:
                    continue  # a header or the filler: only the gutter strips take the wheel
                # Read back: a view that has just changed group is still the old size, so Sublime
                # clamps the position. Expecting the intended y would read the clamp as the wheel.
                self.expected[shown.view.id()] = (shown.view, shown.view.viewport_position()[1])
            if item is self.filler:
                self.place_tail()

    def place_tail(self):
        """The strip below the last pane sits in the middle of its blank lines, room either way."""
        y = TAIL_LINES * self.tail.line_height()
        self.tail.set_viewport_position((0, y), False)
        self.expected[self.tail.id()] = (self.tail, self.tail.viewport_position()[1])

    def read_wheel(self):
        """The wheel over a code pane, a header or the filler scrolls that view; the reader takes
        the movement over. The view goes back first and the reader is redrawn after, or the view
        would show its own position for as long as the redraw takes, which looks like trembling."""
        settling = time.time() < self.settle_until
        moved = 0.0
        for view, y in self.expected.values():
            if not view.is_valid():
                continue
            x, at = view.viewport_position()
            if abs(at - y) > 0.5:
                view.set_viewport_position((x, y), False)
                # Right after a render Sublime moves views by itself (focus, caret): not the wheel.
                # A jump of more than a screen is never the wheel either, but a view being laid out.
                if not settling and abs(at - y) < self.window_height:
                    moved = moved or at - y
        if moved:
            self.scroll_to(self.offset + moved, wheel=True)

    def fill_vetting(self):
        top, split = self.geometry(self.window_height)
        lh = self.below.line_height()
        behind = 0  # nothing lies behind the code any more
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
            header = {1: icons[(index, 0)]} if (index, 0) in icons else {}
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
        sublime.set_timeout(self.poll, POLL_MS)

    def poll_wheel(self):
        """Its own loop, far shorter than poll: how long a view scrolls before the reader takes
        the movement over is the give the user feels. Reading a few viewport positions is cheap."""
        if state.READERS.get(self.window.id()) is not self or not self.chat.is_valid():
            return
        if self.ready and self.gutter is not None:
            self.read_wheel()
        sublime.set_timeout(self.poll_wheel, WHEEL_MS)

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
