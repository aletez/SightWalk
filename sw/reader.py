"""The reader: one window with the sights of one program run (Sights), the conversation (Vetting
Bench) and the Itinerary and Map below it.

The code column is a virtual document, every sight's header and code stacked (plan). Each view
keeps a permanent cell at its place in that document, above and below the screen too: a layout's
rows may lie outside 0..1 (Jakub found). Scrolling only shifts the rows (column_rects), which is
one cheap set_layout. The wheel is read by polling: a view the wheel moved off its place is put
back and the movement taken over (read_wheel)."""

import os
import time

import sublime

from . import chat, marks, plan, state, vetting
from .config import (BENCH_WIDTH, DEFAULT_BENCH_SIDE, DEFAULT_CONVERSATION_HEIGHT, GUTTER_PX, INSET,
                     OVERLAP, POLL_MS, ROOM_LINES, SETTINGS_FILE, SETTLE_MS, SETTLE_S,
                     WHEEL_MS)
from .editor import Editor
from .header import BENCH, SIGHTS
from .line_one import LineOne, line_top
from .spec import display_path, parse_spec, repo_root, sight_title
from .tint import apply_grey, apply_tint
from .views import (anchor, bench_font, draw_edit_button, draw_gap, draw_icons, draw_outlines, header_top,
                    hide_chrome, make_blank_view, make_header, make_side_view, prepare_code_view,
                    reader_layout, wait_until_loaded, write_header)


class Reader:
    def __init__(self, window):
        self.window = window
        self.sights, self.items, self.indicators, self.edits = [], [], [], []
        self.offset = 0.0
        # px: the window's height, the height a cell adds to its content, a code line's height.
        self.height = self.overhead = self.lh = None
        self.ready = self.measured = False
        self.gutter, self.gutter_tries = GUTTER_PX, 0
        self.resize_base = None
        self.settle_until = 0.0
        self.last_ids = []
        self.status = self.trip = self.note = ""  # note: the guide is coming or thinking
        self.bench_width = BENCH_WIDTH
        self.editor = None
        self.make_side_views()

    def make_side_views(self):
        """Every view but the sights. Below the last sight an invisible filler takes the wheel
        (Jakub)."""
        self.filler = make_blank_view(self.window, "")
        self.chat = make_side_view(self.window, "Vetting Bench", {
            "word_wrap": True, "wrap_width": 0, "sight_walk_chat": True, "scroll_past_end": False})
        chat.start(self.chat)
        # Headers over the bench and over the Sights play the role of tabs, since tabs are off.
        self.chat_header = chat.make_header(self.window, self.chat, BENCH)
        self.sights_header = chat.make_header(self.window, self.chat, SIGHTS)
        for header in (self.chat_header, self.sights_header):
            apply_grey(header)
        bench_font(self.chat)  # after the headers, which keep the font of code
        self.below = vetting.make(self.window, self.chat)

    # Loading

    def load(self, specs, root=None, trip=None):
        self.ready = self.measured = False
        self.trip = trip or ""
        chat.catch_up(self.chat)  # what was said on the Vetting strip meanwhile
        self.close_sights()
        self.gutter, self.gutter_tries = GUTTER_PX, 0
        self.sights = [plan.Sight(spec, *parse_spec(spec, root)) for spec in specs]
        self.indicators = []
        paths = list(dict.fromkeys(sight.path for sight in self.sights))
        originals = {path: self.window.open_file(path) for path in paths}
        wait_until_loaded(list(originals.values()), lambda: self.build(originals))

    def close_sights(self):
        if self.editor is not None:
            self.editor.header.close()
            self.editor.view.close()
            self.editor = None
        for sight in self.sights:
            for view in (sight.view, sight.header):
                if view is not None and view.is_valid():
                    view.close()
            if sight.line_one is not None:
                sight.line_one.close()

    def build(self, originals):
        opened = set()
        for sight in self.sights:
            # A file's first sight uses the view Sublime opened, the others clones of it.
            sight.view = prepare_code_view(self.window, originals[sight.path], sight.path in opened)
            sight.header = make_header(self.window, sight_title(sight), sight.view)
            if sight.begin == 1:
                sight.line_one = LineOne(self.window, sight, originals[sight.path])
            opened.add(sight.path)
        self.tint(originals)
        self.draw_gaps()
        self.make_items()
        if self.height is None:
            self.calibrate()
        else:
            self.start()

    def tint(self, paths):
        """Every file in its own hue (see tint)."""
        for path in paths:
            mine = [s for s in self.sights if s.path == path]
            apply_tint([v for s in mine for v in s.code_views()], [s.header for s in mine], path)

    def draw_gaps(self):
        """Room between the gutter and the code on every line a sight shows (see draw_gap)."""
        for sight in self.sights:
            draw_gap(sight.view, sight.begin, sight.end)
            if sight.line_one is not None:
                sight.line_one.draw_gaps()

    def make_items(self):
        """The cells of the virtual document: each sight's header, then its code."""
        self.lh = self.sights[0].view.line_height()
        self.items = []
        for sight in self.sights:
            sight.header_item = plan.Item(sight.header, header_top(sight.header), self.lh)
            content = (sight.end - sight.begin + 1) * self.lh
            sight.code_item = plan.Item(sight.view, line_top(sight.view, sight.begin), content)
            self.items += [sight.header_item, sight.code_item]

    def calibrate(self):
        """Measures the window's height H and the height o a cell adds to its content: a cell over
        the whole column shows H - o, each of two cells of half of it H/2 - o."""
        left, _, right, _ = self.column()
        self.place([(left, 0.0, right, 1)], [self.sights[0].view], 1)
        sublime.set_timeout(self.measure_full, SETTLE_MS)

    def measure_full(self):
        sight = self.sights[0]
        full = sight.view.viewport_extent()[1]
        left, _, right, _ = self.column()
        self.place([(left, 0.0, right, 1), (left, 1, right, 2)], [sight.view, sight.header], 2)
        sublime.set_timeout(lambda: self.measure_half(full), SETTLE_MS)

    def measure_half(self, full):
        half = self.sights[0].view.viewport_extent()[1]
        self.height = 2 * (full - half)
        self.overhead = self.height - full
        self.start()

    def start(self):
        plan.stack(self.items, self.overhead)
        self.ready = True
        self.scroll_to(0)

    def measure_gutter(self):
        """A sight at line 1 shows line 1's code beside its gutter: it must start where the code
        below it starts. The gutter's width moves by the difference, one step per poll. Then the
        reader starts at the top, whatever a view settling meanwhile was read as."""
        line_one = next((s.line_one for s in self.sights if s.line_one), None)
        if line_one is not None and self.gutter_tries < 9:
            off = line_one.misalignment()
            if abs(off) > 0.5:
                self.gutter = max(self.gutter + off, 1)
                self.gutter_tries += 1
                self.render()
                return
        self.measured = True
        self.offset = 0.0
        self.render()

    # Layout

    def share(self, px):
        """px as a share of the window's width. The conversation has no gutter, so its text is
        about as wide as its column."""
        width = self.chat.viewport_extent()[0] / max(self.bench_width, 0.01)
        return px / max(width, 1)

    def spans(self):
        """(bench, sights): the x spans of the Vetting Bench and of the Sights, as shares of the
        width. The bench is left of the Sights or, by the setting bench_side, right of them."""
        side = sublime.load_settings(SETTINGS_FILE).get("bench_side", DEFAULT_BENCH_SIDE)
        w = self.bench_width
        if side == "right":
            return (1.0 - w, 1.0), (0.0, 1.0 - w)
        return (0.0, w), (w, 1.0)

    def column(self):
        """The Sights as shares of the window's width: their left edge, the right edge of a
        sight's gutter, their right edge, and a border's width."""
        left, right = self.spans()[1]
        return left, left + self.share(self.gutter), right, self.share(OVERLAP)

    def conversation_rows(self):
        """The bottoms of the conversation's header and of the conversation, in px; 0, 0 until
        calibrated. The vetting pane takes the rest of the column."""
        if self.overhead is None:
            return 0, 0
        top = 2 * self.chat_header.line_height() + self.overhead  # its font may differ
        settings = sublime.load_settings(SETTINGS_FILE)
        share = settings.get("default_conversation_height", DEFAULT_CONVERSATION_HEIGHT)
        return top, max(self.height * share, top + 2 * self.lh)

    def head(self):
        """The headers' height in px: the Sights start below theirs, level with the bench's."""
        return self.conversation_rows()[0]

    def room(self):
        """The Sights' height in px, below their header."""
        return self.height - self.head()

    def editor_geometry(self):
        """The editor sits to the lower right of the sights, its top left corner set back past their
        header and gutter, so no colour of the frame touches the same colour in the editor."""
        if self.editor is None:
            return None
        header = self.editor.header.line_height() + self.overhead
        _, gutter, right, _ = self.column()
        top = self.head() + self.lh + self.overhead + INSET
        return header, gutter + self.share(INSET), right, top

    def column_rects(self):
        """The Sights' header, every sight's cells below it, then the filler below the last sight:
        (rects, views), rects in px from the top of the screen, shifted by the offset."""
        column = self.column()
        left, _, right, _ = column
        rects, views = [(left, 0.0, right, self.head() + OVERLAP)], [self.sights_header]
        for sight in self.sights:
            more_rects, more_views = self.sight_cells(sight, column)
            rects += more_rects
            views += more_views
        # The filler takes half the border with the last sight, like any neighbour (Jakub).
        end = max(r[3] for r in rects[1:]) - OVERLAP
        rects.append((left, end, right, max(end, 0.0) + self.height))
        views.append(self.filler)
        return rects, views

    def sight_cells(self, sight, column):
        """A sight's header and code. Earlier cells are drawn over later ones, and each neighbour
        takes half the border between them, so neither covers the other's text (Jakub)."""
        left, _, right, _ = column
        rects, views = [], []
        for item in (sight.header_item, sight.code_item):
            top = self.head() + item.y - self.offset - OVERLAP / 2
            bottom = top + item.content + self.overhead + OVERLAP
            if item is sight.code_item and sight.line_one is not None:
                cells = sight.line_one.rects(column, top, bottom, self.lh)
            else:
                cells = [(left, top, right, bottom)], [item.view]
            rects += cells[0]
            views += cells[1]
        return rects, views

    def layout(self, rects, total):
        top, split = self.conversation_rows()
        if top and self.editor is None:
            self.keep_bench_width()
        self.window.set_layout(reader_layout(rects, total, top, split, self.spans()[0],
                                             self.editor_geometry()))
        return top

    def keep_bench_width(self):
        """A bench the user widened by dragging keeps its width."""
        layout = self.window.get_layout()
        group = self.window.get_view_index(self.chat)[0]
        if 0 <= group < len(layout["cells"]):
            x0, _, x1, _ = layout["cells"][group]
            self.bench_width = layout["cols"][x1] - layout["cols"][x0]

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
        """A wheel step only shifts the layout's rows (see column_rects); anything else lays every
        view out again."""
        rects, views = self.column_rects()
        if settle or [v.id() for v in views] != self.last_ids:
            self.arrange(rects, views)
        else:
            self.layout(rects, self.height)
        self.draw_gutter()  # the eyes depend on what is on screen

    def arrange(self, rects, views):
        """Every view into its own group, focused if it was not shown there yet, then the rest of
        what a layout decides."""
        self.place(rects, views, self.height)
        self.window.focus_view(self.chat if self.editor is None else self.editor.view)
        self.last_ids = [v.id() for v in views]
        self.settle_until = time.time() + SETTLE_S  # the views may be off their places a moment
        self.draw_outlines()
        self.show_headers()
        self.draw_edit_buttons()
        self.scroll_views()
        sublime.set_timeout(self.scroll_views, 0)  # again, once Sublime has laid them out

    # Scrolling

    def scroll_to(self, offset, wheel=False):
        if not self.ready:
            return
        limit = plan.max_offset(self.items, self.room(), self.overhead)
        self.offset = min(max(offset, 0.0), limit)
        self.render(settle=not wheel)

    def places(self):
        """Where each view stands in its cell, as a layout y: the filler at its anchor, a sight's
        views at their text, half a border lower, as their cells begin that much higher (never
        above line 1)."""
        places = [(self.filler, anchor(self.filler))]
        for sight in self.sights:
            texts = [(item.view, item.top_layout) for item in (sight.header_item, sight.code_item)]
            if sight.line_one is not None:
                texts += sight.line_one.places()
            places += [(view, max(y - OVERLAP / 2, 0.0)) for view, y in texts]
        return places

    def scroll_views(self):
        """Every view at its place; the cells move, the views do not."""
        for view, place in self.places():
            view.set_viewport_position((view.viewport_position()[0], place), False)
        if self.editor is not None:  # its header's text sits between blank lines too
            self.editor.header.set_viewport_position((0, header_top(self.editor.header)), False)

    def read_wheel(self):
        """The wheel moves the view under the pointer off its place: the reader puts it back and
        takes the movement over. A jump larger than a screen is a view being laid out, not the
        wheel; while a new layout settles, movements are only undone."""
        settling = time.time() < self.settle_until
        for view, place in self.places():
            x, y = view.viewport_position()
            if abs(y - place) <= 0.5:
                continue
            view.set_viewport_position((x, place), False)
            if not settling and abs(y - place) < self.height:
                self.scroll_to(self.offset + y - place, wheel=True)
                return

    # Polling

    def alive(self):
        return state.READERS.get(self.window.id()) is self and self.chat.is_valid()

    def poll(self):
        """The slow loop: the conversation's bottom and header, the gutter's width at first, then
        the window's size."""
        if not self.alive():
            return
        chat.keep_at_bottom(self.chat)
        self.show_headers()  # they rewrap when a column is resized
        if self.ready and not self.measured:
            self.measure_gutter()
        elif self.ready:
            self.follow_resize()
        sublime.set_timeout(self.poll, POLL_MS)

    def poll_wheel(self):
        """Its own loop, far shorter than poll: how long a view scrolls before the reader takes
        the movement over is the give the user feels. Reading a few viewport positions is cheap."""
        if not self.alive():
            return
        if self.ready:
            self.read_wheel()
        sublime.set_timeout(self.poll_wheel, WHEEL_MS)

    def follow_resize(self):
        """A panel or a window resize changes the room. The conversation and the vetting pane
        together span the column under the fixed header, so their heights change one to one."""
        size = self.chat.viewport_extent()[1] + self.below.viewport_extent()[1]
        if self.resize_base is None:
            self.resize_base = (size, self.height)
        elif abs(size - self.resize_base[0] - (self.height - self.resize_base[1])) > 0.5:
            self.height = self.resize_base[1] + size - self.resize_base[0]
            self.render()

    # Marks

    def point(self, new_marks, reveal=True, clear=True):
        resolved = marks.resolve_marks(self.sights, new_marks)
        self.indicators = resolved if clear else self.indicators + resolved
        ys = [marks.line_y(self.sights[m["sight"]], m["line"], self.lh) for m in resolved]
        bottom = self.offset + self.room() - 2 * self.lh
        if reveal and ys and not all(self.offset <= y <= bottom for y in ys):
            self.scroll_to((min(ys) + max(ys)) / 2 - self.room() / 2)
        else:
            self.render()

    def draw_gutter(self):
        """Icons for the marks on screen, an eye for those off it (see marks.gutter_icons)."""
        first, last = marks.visible_lines(self.sights, self.offset, self.room(), self.lh)
        icons = marks.gutter_icons(self.indicators, first, last)
        for index, sight in enumerate(self.sights):
            mine = {line: icon for (i, line), icon in icons.items() if i == index and line}
            draw_icons(sight.view, sight.icons, mine)
            if sight.line_one is not None:
                sight.line_one.draw_icons(sight.icons, mine)
            sight.icons = mine
            # A header's line 0 is drawn on its text line.
            header = {ROOM_LINES + 1: icons[(index, 0)]} if (index, 0) in icons else {}
            draw_icons(sight.header, sight.header_icons, header)
            sight.header_icons = header

    def draw_outlines(self):
        for index, sight in enumerate(self.sights):
            lines = set(m["line"] for m in self.indicators if m["sight"] == index)
            if lines != sight.outlines:
                draw_outlines(sight.view, lines)
                if sight.line_one is not None:
                    sight.line_one.draw_outlines(lines)
                sight.outlines = lines

    # Editing

    def draw_edit_buttons(self):
        for index, sight in enumerate(self.sights):
            draw_edit_button(sight.header, sight_title(sight),
                             lambda _, i=index: self.open_editor(i, self.sights[i].begin))

    def open_editor(self, index, line):
        if self.editor is None:
            if self.sights[index].view.is_dirty():
                # Don't Save could not tell those changes from the editor's and would revert them.
                path = display_path(self.sights[index].path)
                sublime.message_dialog("%s has unsaved changes in another view. Save or discard "
                                       "them there first." % path)
                return
            self.editor = Editor(self, index, line)
        self.render()

    def sight_of(self, view):
        """The index of the sight that shows the view, or None."""
        for index, sight in enumerate(self.sights):
            if view in sight.code_views():
                return index
        return None

    def close_editor(self):
        self.editor.close(self.editor_closed)

    def editor_closed(self, ranges, lines):
        """After Esc. If the file is still dirty, the user chose Don't Save: the sights go back to
        the file on disk. Otherwise the reader takes the edits over and tells the agent."""
        path = self.editor.path
        sight = next(s.view for s in self.sights if s.path == path)
        self.editor = None
        if sight.is_dirty():
            sight.run_command("revert")
            ranges, lines = {}, {}
        sight.set_read_only(True)  # read-only belongs to the buffer
        for k, line in lines.items():
            self.indicators[k]["line"] = line
        for i, (begin, end) in ranges.items():
            self.move_range(self.sights[i], begin, end)
        for sight in self.sights:  # saved: a twin shows the file's new line 1
            if ranges and sight.path == path and sight.line_one is not None:
                sight.line_one.refill()
                sight.outlines = None
        self.draw_gaps()
        self.make_items()
        plan.stack(self.items, self.overhead)
        self.render()

    def move_range(self, sight, begin, end):
        if (begin, end) == (sight.begin, sight.end):
            return
        self.edits.append("%s, now %d-%d" % (sight.spec, begin, end))
        sight.spec = "%s:%d-%d" % (sight.spec.rpartition(":")[0], begin, end)
        sight.begin, sight.end = begin, end
        write_header(sight.header, sight_title(sight))

    def take_edits(self):
        """Ranges the user changed in the editor, for the agent's next message."""
        edits, self.edits = self.edits, []
        return {"edited": edits} if edits else {}

    # Conversation

    def show_headers(self):
        chat.show_header(self.chat_header, BENCH, self.note or self.status)
        chat.show_header(self.sights_header, SIGHTS, self.trip, help_mark=False)

    def note_waiting(self, note):
        self.note = note
        self.show_headers()

    def folder(self):
        """Where a guide started for this trip works: the first sight's repository."""
        path = self.sights[0].path
        return repo_root(path) or os.path.dirname(path)

    def say(self, text, status=None, prefix="A: "):
        if prefix == "A: ":
            self.note = ""  # the answer has come
        if status is not None:
            self.status = status
        self.show_headers()
        chat.say(self.chat, text, prefix)

    def context(self):
        if not self.ready:
            return {"focus": None, "visible": []}
        focus = plan.focus_sight(self.sights, self.offset, self.room(), self.overhead)
        return {"focus": focus.spec if focus else None,
                "visible": plan.visible_specs(self.sights, self.offset, self.room())}
