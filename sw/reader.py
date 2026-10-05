import queue
import time

import sublime

from . import chat, marks, plan, state, vetting
from .config import (COLS, DEFAULT_CONVERSATION_HEIGHT, INSET, MIN_LINES_IN_CELL, OVERLAP,
                     POLL_MS, SETTINGS_FILE, SETTLE_MS, SETTLE_S, STRIP_DEFAULT, STRIP_LINES, STRIP_PX,
                     WHEEL_MS)
from .spec import display_path, header_text, parse_spec
from .editor import Editor
from .tint import apply_grey, apply_tint
from .views import (draw_edit_button, draw_icons, draw_outlines, hide_chrome, make_header,
                    make_side_view, match_font, prepare_code_view, reader_layout, wait_until_loaded,
                    write_header)


class Reader:
    def __init__(self, window):
        self.window = window
        self.segments, self.items, self.indicators = [], [], []
        self.offset = 0.0
        # window_height: the whole layout; height: the code column, VETTING_LINES shorter.
        self.window_height = self.height = self.overhead = self.lh = None
        self.ready = False
        self.resize_base = None
        self.inbox = queue.Queue()
        self.filler = plan.Item(make_side_view(window, "", {}), 0.0, 0.0)
        self.filler.view.set_read_only(True)
        # Between the conversation and the code, an empty strip the width of a gutter: the only
        # place the wheel moves the column. Its blank lines give the wheel room either way.
        self.strip = make_side_view(window, "Scroll", {"word_wrap": False})
        self.strip.run_command("sight_walk_replace", {"text": "\n" * (2 * STRIP_LINES)})
        self.strip.sel().clear()
        self.strip.sel().add(sublime.Region(self.strip.text_point(STRIP_LINES, 0)))
        self.strip.set_read_only(True)
        self.grouped = set()
        self.settle_until = 0.0
        self.last_ids = []
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
        self.items = []
        for seg in self.segments:
            top = seg.view.text_to_layout(seg.view.text_point(seg.begin - 1, 0))[1]
            seg.code_item = plan.Item(seg.view, top, (seg.end - seg.begin + 1) * self.lh)
            seg.header_item = plan.Item(seg.header, 0.0, self.lh)
            self.items += [seg.header_item, seg.code_item]

    def measure_gutter(self):
        """Once the panes are laid out, a pane's gutter can be measured: the strip's width."""
        pane = self.segments[0].view
        column = (self.cols[2] - self.code_left()) * self.window_width()
        self.gutter = max(column - pane.viewport_extent()[0], 1)
        self.render()

    def start(self):
        plan.stack(self.items, self.overhead)
        self.ready = True
        self.scroll_to(0)

    def calibrate(self, callback):
        view, other = self.segments[0].view, self.segments[0].header
        self.place([(self.code_left(), 0.0, self.cols[2], 1)], [view], 1)

        def measure_full():
            full = view.viewport_extent()[1]
            self.place([(self.code_left(), 0.0, self.cols[2], 1),
                        (self.code_left(), 1, self.cols[2], 2)], [view, other], 2)

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
        """The editor sits to the lower right of the panes, its top left corner set back past their
        header and gutter, so no colour of the frame touches the same colour in the editor."""
        if self.editor is None:
            return None
        width = self.window_width()
        header = self.editor.header.line_height() + self.overhead
        left = self.code_left() + self.gutter_share() + INSET / width
        return header, left, self.lh + self.overhead + INSET

    def gutter_share(self):
        """The panes' gutter as a share of the window. The px value is measured once, after the
        first layout."""
        return (self.gutter or STRIP_DEFAULT) / self.window_width()

    def strip_share(self):
        # Twice the gutter's former width (52 px), a fixed width that needs no measuring.
        return STRIP_PX / self.window_width()

    def code_left(self):
        return self.cols[1] + self.strip_share()

    def column_rects(self):
        """The strip, from top to bottom of the window, then every pane and header at its place in
        the virtual document, above and below the screen too (a layout's rows may lie outside 0..1,
        Jakub found). Scrolling only shifts the rows: no view changes group, size or position."""
        left, right = self.code_left(), self.cols[2]
        rects, views = [(self.cols[1], 0.0, left, self.window_height)], [self.strip]
        for item in self.items:
            top = item.y - self.offset
            rects.append((left, top, right, top + item.content + self.overhead))
            views.append(item.view)
        # The filler covers the room below the last pane.
        end = rects[-1][3]
        rects.append((left, end, right, max(end, 0.0) + self.window_height))
        views.append(self.filler.view)
        return rects, views

    def layout(self, rects, total):
        top, split = self.geometry(total)
        current = self.window.get_layout().get("cols", [])
        if top and self.editor is None and len(current) == 4:
            self.cols = [0.0, current[1], 1.0]  # a conversation the user widened keeps its width
        self.window.set_layout(reader_layout(rects, total, top, split, self.cols,
                                             self.editor_geometry()))
        return top

    def place(self, rects, views, total):
        top = self.layout(rects, total)
        self.assign_groups(views, bool(top))
        hide_chrome(self.window)

    def assign_groups(self, views, full):
        # Until calibrated, the header and the vetting pane wait behind the conversation.
        first = [] if self.editor is None else [self.editor.header, self.editor.view]
        ordered = first + views + [self.chat]
        for group, view in enumerate(ordered):
            # Moving and focusing views is what makes a layout slow: only views not already
            # shown in their group are moved, and focused so their group shows them.
            if self.window.active_view_in_group(group) != view:
                self.window.set_view_index(view, group, 0)
                self.window.focus_view(view)
        n = len(ordered)
        for k, view in enumerate([self.chat_header, self.below]):
            self.window.set_view_index(view, n + k if full else n - 1, 0 if full else k + 1)

    def render(self, settle=True):
        """The wheel only shifts the layout's rows (see column_rects); anything else lays every
        view out again."""
        rects, views = self.column_rects()
        if settle or [v.id() for v in views] != self.last_ids:
            self.arrange(rects, views)
            self.last_ids = [v.id() for v in views]
            self.settle_until = time.time() + SETTLE_S  # the strip may be off its anchor a moment
            self.draw_outlines()
            self.fill_vetting()
            chat.show_header(self.chat_header, self.status)
            self.draw_edit_buttons()
            self.scroll_views()
            sublime.set_timeout(self.scroll_views, 0)  # again, once Sublime has laid them out
        else:
            self.layout(rects, self.window_height)
        self.draw_gutter()  # the eyes depend on what is on screen

    def arrange(self, rects, views):
        """Every view into its own group, focused if it was not shown there yet."""
        self.place(rects, views, self.window_height)
        self.window.focus_view(self.chat if self.editor is None else self.editor.view)

    def scroll_views(self):
        """Each pane shows its range from the top of its cell; the cell itself moves, not the view."""
        for item in self.items:
            x = item.view.viewport_position()[0]
            item.view.set_viewport_position((x, item.top_layout), False)
        self.strip.set_viewport_position((0, self.anchor()), False)

    def anchor(self):
        return STRIP_LINES * self.strip.line_height()

    def read_wheel(self):
        """The wheel over the strip moves it off its anchor: the reader takes the movement over and
        puts the strip back."""
        y = self.strip.viewport_position()[1]
        if abs(y - self.anchor()) > 0.5:
            self.strip.set_viewport_position((0, self.anchor()), False)
            if time.time() < self.settle_until:
                return
            self.scroll_to(self.offset + y - self.anchor(), wheel=True)

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
                seg.outlines = lines

    def poll(self):
        if state.READERS.get(self.window.id()) is not self or not self.chat.is_valid():
            return
        chat.keep_at_bottom(self.chat)
        chat.show_header(self.chat_header, self.status)  # rewraps when the column is resized
        if self.ready:
            if self.gutter is None:
                self.measure_gutter()
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
        path = self.editor.path
        pane = next(s.view for s in self.segments if s.path == path)
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
