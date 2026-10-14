"""The reader: one trip's window, with the sights of one program run (Sights), the conversation
(Vetting Bench), the Tools pane under it and the scroll strip between them.

The code column is a virtual document, every sight's header and code stacked (plan). Each view
keeps a permanent cell at its place in that document, above and below the screen too: a layout's
rows may lie outside 0..1 (Jakub found). Scrolling only shifts the rows (column_rects), which is
one cheap set_layout. The wheel is read by polling: a view the wheel moved off its place is put
back and the movement taken over (read_wheel)."""

import json
import os
import re
import time

import sublime

from . import asked, callmap, chat, marks, ontology, plan, state, vetting
from .config import (BENCH_MARGIN, BENCH_WIDTH, BLANK_LINES, DEFAULT_CONVERSATION_HEIGHT, FROZEN_PARENTS,
                     OVERLAP, POLL_MS, ROOM_LINES, SETTINGS_FILE, SETTLE_MS, SETTLE_S, STRIP_STEP,
                     WHEEL_MS)
from .editor import Editor
from .geometry import Geometry
from .ontology import Sight, Trip
from .header import BENCH, SIGHTS, STRIP
from .words import word
from .spec import ancestors, breathing, display_path, parse_spec, repo_root, sight_title
from .tint import apply_grey, apply_tint, hue_for, tint_color
from .views import (FileCopy, anchor, bench_font, draw_edit_button, draw_gap, draw_icons,
                    draw_outlines, draw_strip_icons, forget, header_top, hide_chrome, line_top,
                    make_blank_view, make_browser, make_copy, make_header, make_side_view,
                    match_font, phantoms, reader_layout, selected_text, to_layout)

CLASS = re.compile(r"^\s*class\s+(\w+)")
EMPTY_HEADER = 0.05  # a header's height in a trip with no sights, as a share (nothing measured)
ARROWS = {"up": "▲", "down": "▼"}
STRIP_BUTTON_HTML = ('<a href="%s" style="text-decoration: none; color: var(--foreground); '
                     'font-size: 1.6rem">%s</a>')


def line_count(view):
    return view.rowcol(view.size())[0] + 1


def defined_name(lines, line, main):
    """The name defined at line, or the line's start when it defines nothing Python knows."""
    found = callmap.DEF.match(lines[line - 1]) if line <= len(lines) else None
    if found:
        return found.group(1)
    return main[1] if line == main[0] else lines[line - 1].strip()[:30]


def item_top(item):
    """The layout y of a cell's top line. A code line is measured afresh: a fresh copy is laid out
    late."""
    return line_top(item.view, item.line) if item.line else item.top_layout


class Reader(Geometry):
    def __init__(self, window):
        self.window = window
        self.sights, self.items, self.indicators, self.edits = [], [], [], []
        self.offset = self.lead = 0.0  # lead: room above a short trip (see plan.lead)
        # px: the window's height, the height a cell adds to its content, a code line's height.
        self.height = self.overhead = self.lh = None
        self.ready = False
        self.resize_base = None
        self.settle_until = 0.0
        self.last_ids = []
        # note: non-empty = an answer is on its way (guide coming or thinking); shows [Stop]
        self.status = self.note = ""
        self.trip = None  # the ontology.Trip shown
        self.informator = self.tour = self.informator_root = None  # see open_tour
        self.informator_path = self.tour_trip = None
        self.walked = set()
        self.bench_width = BENCH_WIDTH
        self.editor = None
        self.strip_marks = None  # the icons last drawn on the strip
        self.touched = None  # the code view whose selection the user changed last: "here" (Jakub)
        self.root = self.browser = None  # a trip with no sights yet: its folder and file browser
        self.make_side_views()

    def make_side_views(self):
        """Every view but the sights. Below the last sight an invisible filler takes the wheel
        (Jakub)."""
        self.filler = make_blank_view(self.window, "")
        self.filler.assign_syntax(chat.SYNTAX)  # the bench's colours below the sights (Jakub)
        self.top_filler = make_blank_view(self.window, "")  # above a short trip (see plan.lead)
        self.top_filler.assign_syntax(chat.SYNTAX)
        # Between the bench and the Sights, an empty strip whose wheel moves the whole trip; the
        # wheel over a sight scrolls only that sight, until the trip next moves (Jakub).
        self.strip = make_blank_view(self.window, "")
        self.strip.assign_syntax(chat.SYNTAX)  # the bench's colours (Jakub)
        self.strip.settings().set("margin", 0)  # room for an icon in a scroll bar's width
        self.strip_floor = make_blank_view(self.window, "")  # ▼, under the strip (Jakub)
        self.strip_floor.assign_syntax(chat.SYNTAX)
        self.strip_floor.settings().set("margin", 0)
        self.chat = make_side_view(self.window, "Vetting Bench", {
            "word_wrap": True, "wrap_width": 0, "sight_walk_chat": True, "scroll_past_end": False})
        self.chat.settings().set("margin", BENCH_MARGIN)
        chat.start(self.chat)
        # Headers over the bench and over the Sights play the role of tabs, since tabs are off.
        self.chat_header = chat.make_header(self.window, self.chat, BENCH)
        self.sights_header = chat.make_header(self.window, self.chat, SIGHTS)
        self.strip_header = chat.make_header(self.window, self.chat, STRIP)
        for header in (self.chat_header, self.sights_header, self.strip_header):
            apply_grey(header)
        self.strip_header.settings().set("gutter", False)  # ▲ in a scroll bar's width
        self.strip_header.settings().set("margin", 0)
        bench_font(self.chat)  # after the headers, which keep the font of code
        self.below = vetting.make(self.window, self.chat)
        self.map_view = vetting.make_tool(self.window, "Map")
        self.tour_view = vetting.make_tool(self.window, "Tour")
        self.pan = True  # bench, Map and Tour take the wheel for the panorama (primary+s, Jakub)
        for view in (self.map_view, self.tour_view):
            vetting.set_panning(view, self.pan)
        self.chat.settings().set("scroll_past_end", self.pan)
        self.tool = vetting.SCROLL  # the Tools pane's tab shown
        self.below_header = chat.make_header(self.window, self.chat, "Tools")
        self.status_view = chat.make_status(self.window, self.chat)
        bench_font(self.status_view)
        apply_grey(self.below_header)

    # Loading

    def load(self, trip, root=None, marks=None):
        """Shows trip (an ontology.Trip): its sights' files read, every view made."""
        self.shown = (trip, root)  # for Reset Sights
        self.ready = False
        self.trip = trip
        chat.catch_up(self.chat)  # what was said in another trip meanwhile
        self.close_sights()
        self.sights = [plan.Pane(sight, *parse_spec(sight.spec, root)) for sight in trip]
        self.indicators = marks or []
        paths = list(dict.fromkeys(sight.path for sight in self.sights))
        self.build({path: FileCopy(path) for path in paths})

    def open_empty(self, folder):
        """A trip with no sights yet: the bench, and the folder's files in the Sights' place (Jakub).
        The first message starts a guide there, and its show replaces the files."""
        self.root, self.browser = folder, make_browser(self.window, folder)
        self.empty_layout()

    def empty_layout(self):
        """Before any sight is measured: the usual columns at fixed heights (Jakub)."""
        h, split = EMPTY_HEADER, DEFAULT_CONVERSATION_HEIGHT
        (b0, b1), (c0, c1), (s0, s1) = self.spans()[0], self.spans()[1], self.strip_span()
        cells = [((b0, 0.0, b1, h), self.chat_header), ((b0, h, b1, split - h / 2), self.chat),
                 ((b0, split - h / 2, b1, split), self.status_view),
                 ((b0, split, b1, split + h), self.below_header),
                 ((b0, split + h, b1, 1.0), self.tool_view()),
                 ((s0, 0.0, s1, h), self.strip_header),
                 ((s0, h, s1, 1.0), self.strip), ((c0, 0.0, c1, h), self.sights_header),
                 ((c0, h, c1, 1.0), self.browser)]  # the browser heads itself with its folder
        self.window.set_layout(to_layout([rect for rect, _ in cells], 1.0))
        for group, (_, view) in enumerate(cells):
            self.window.set_view_index(view, group, 0)
        self.window.set_view_index(self.filler, len(cells) - 1, 1)
        self.window.set_view_index(self.strip_floor, len(cells) - 1, 2)
        self.show_headers()
        self.window.focus_view(self.browser)

    def close_hijacker(self):
        """FileBrowser may take over a new window with a view of its own (its setting
        dired_hijack_new_window), which would lie in one of the trip's cells."""
        for view in self.window.views():
            if view != self.browser and view.settings().has("dired_path"):
                view.close()

    def take_file(self, view):
        """A file opened from the file browser replaces it, the whole file as one sight (Jakub)."""
        if self.browser is None or view.is_loading() or not view.file_name():
            return
        if view in (self.browser, self.chat):
            return
        path, lines = view.file_name(), line_count(view)
        view.close()  # the sight is a copy; the file itself opens only in the editor
        self.load(Trip("", [Sight(path, 1, lines)]))

    def close_sights(self):
        if self.browser is not None and self.browser.is_valid():
            self.browser.close()
        self.browser = None
        if self.editor is not None:
            self.editor.header.close()
            self.editor.view.close()
            self.editor = None
        for view in [v for sight in self.sights for v in sight.all_views() if v.is_valid()]:
            forget(view)
            view.close()

    def build(self, copies):
        for sight in self.sights:
            copy = copies[sight.path]
            sight.view = make_copy(self.window, copy, display_path(sight.path))
            sight.header = make_header(self.window, sight_title(sight), sight.view)
            self.surround(sight, copy)
        self.tint(copies)
        self.draw_gaps()
        asked.draw(self.sights)
        self.make_items()
        if self.height is None:
            self.calibrate()
        else:
            self.start()

    def surround(self, sight, copy):
        """The lines that open the blocks around the sight, frozen under its header, and the blank
        lines just around it, so a function does not look cramped (Jakub)."""
        lines = copy.lines
        keywords = set(sublime.load_settings(SETTINGS_FILE).get("frozen_parents", FROZEN_PARENTS))
        for line in ancestors(lines, sight.begin, keywords):
            view = make_copy(self.window, copy, display_path(sight.path))
            draw_gap(view, line, line)
            sight.frozen.append((line, view))
        begin, end = breathing(lines, sight.begin, sight.end)
        sight.pad = (sight.begin - begin, end - sight.end)
        sight.begin, sight.end = begin, end

    def tint(self, paths):
        """Every file in its own hue (see tint)."""
        for path in paths:
            mine = [s for s in self.sights if s.path == path]
            views = [v for s in mine for v in s.all_views() if v != s.header]
            apply_tint(views, [s.header for s in mine], path)

    def draw_gaps(self):
        """Room between the gutter and the code on every line of each sight's copy, not only its
        range: a sight scrolled on its own shows its neighbours aligned too (Jakub)."""
        for sight in self.sights:
            draw_gap(sight.view, 1, line_count(sight.view))

    def make_items(self):
        """The cells of the virtual document: each sight's header, then its code."""
        self.lh = self.sights[0].view.line_height()
        match_font(self.strip, self.sights[0].view)  # the strip's lines level with the code's
        self.items = []
        for sight in self.sights:
            sight.header_item = plan.Item(sight.header, header_top(sight.header), self.lh, True)
            sight.frozen_items = [plan.Item(view, line_top(view, line), self.lh, line=line)
                                  for line, view in sight.frozen]
            content = (sight.end - sight.begin + 1) * self.lh
            sight.code_item = plan.Item(sight.view, line_top(sight.view, sight.begin), content,
                                        line=sight.begin)
            self.items += sight.items()

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
        plan.stack(self.items, self.overhead, self.lh)
        self.lead = self.centred_lead()
        self.write_strip()
        self.ready = True
        self.scroll_to(0)
        self.draw_map()
        self.draw_tour()
        # Widths are shares measured from the bench (see share), which Sublime reports right only
        # once this layout is drawn: once more then.
        sublime.set_timeout(lambda: self.scroll_to(self.offset), SETTLE_MS)

    # Layout

    def layout(self, rects, total, front=()):
        top, split = self.conversation_rows()
        if top and self.editor is None:
            self.keep_bench_width()
        status = self.status_view.line_height() + self.overhead if top else 0.0
        cover = None
        if front:  # the strip's far edge: the status line and the Tools header reach across it
            x0, _, x1, _ = front[0]
            cover = x1 if self.bench_side() != "right" else x0
        self.window.set_layout(reader_layout(rects, total, top, split, self.spans()[0], front,
                                             self.editor_geometry(), status, cover))
        return top

    def strip_in_front(self, rects, views):
        """While the scroll pad or the bench takes the wheel, the strip reaches over the border
        between them and comes first, so the blank areas read as one (Jakub); the strip reaches,
        not they, as a view reaching over another gets a shadow on its right edge."""
        if not (self.pan or self.tool == vetting.SCROLL) or self.strip not in views:
            return [], []
        i = views.index(self.strip)
        x0, y0, x1, y1 = rects.pop(i)
        views.pop(i)
        reach = self.share(3 * OVERLAP)
        rect = (x0 - reach, y0, x1, y1) if self.bench_side() != "right" else (x0, y0, x1 + reach, y1)
        return [rect], [self.strip]

    def keep_bench_width(self):
        """A bench the user widened by dragging keeps its width. Measured on its header, whose
        cell never reaches over the strip (the bench's does while it takes the wheel)."""
        layout = self.window.get_layout()
        group = self.window.get_view_index(self.chat_header)[0]
        if 0 <= group < len(layout["cells"]):
            x0, _, x1, _ = layout["cells"][group]
            self.bench_width = layout["cols"][x1] - layout["cols"][x0]

    def place(self, rects, views, total):
        rects, views = list(rects), list(views)
        front_rects, front_views = self.strip_in_front(rects, views)
        top = self.layout(rects, total, front_rects)
        self.assign_groups(front_views + views, bool(top), len(front_views))
        hide_chrome(self.window)

    def assign_groups(self, views, full, front=0):
        """views: the front ones (see strip_in_front), then the Sights' and the strip's."""
        # Until calibrated, the headers and the Tools pane wait behind the conversation.
        first = [] if self.editor is None else [self.editor.header, self.editor.view]
        tools = [self.tool_view()] if full else []
        lines = [self.status_view, self.below_header] if full and front else []
        ordered = first + lines + views[:front] + tools + views[front:] + [self.chat]
        for group, view in enumerate(ordered):
            # Moving and focusing views is what makes a layout slow: only views not already
            # shown in their group are moved, and focused so their group shows them.
            if self.window.active_view_in_group(group) != view:
                self.window.set_view_index(view, group, 0)
                self.window.focus_view(view)
        n = len(ordered)
        rest = [self.chat_header] + ([] if lines else [self.below_header, self.status_view])
        if full:
            for k, view in enumerate(rest):
                self.window.set_view_index(view, n + k, 0)
        else:
            for k, view in enumerate(rest + [self.tool_view()]):
                self.window.set_view_index(view, n - 1, k + 1)
        for view in self.hidden_tools():  # behind the conversation
            self.window.set_view_index(view, ordered.index(self.chat), 1)

    def render(self, settle=True):
        """A wheel step only shifts the layout's rows (see column_rects); anything else lays every
        view out again."""
        rects, views = self.column_rects()
        if settle or [v.id() for v in views] != self.last_ids:
            self.arrange(rects, views)
        else:
            rects, views = list(rects), list(views)
            self.layout(rects, self.height, self.strip_in_front(rects, views)[0])
            self.scroll_views()  # a sight scrolled on its own goes back to its first line (Jakub)
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
        self.draw_strip_buttons()
        sublime.set_timeout(self.draw_strip_buttons, SETTLE_MS)  # once the strip has its height
        self.scroll_views()
        sublime.set_timeout(self.scroll_views, 0)  # again, once Sublime has laid them out

    # Scrolling

    def centred_lead(self):
        """Room above a short trip, so its middle is level with the window's (Jakub)."""
        middle = self.height / 2 - self.head()
        return plan.lead(self.items, self.room(), self.overhead, middle)

    def scroll_to(self, offset, wheel=False):
        if not self.ready:
            return
        low, high = plan.offset_range(self.items, self.room(), self.overhead, self.lead)
        self.offset = min(max(offset, low), high)
        self.render(settle=not wheel)

    def places(self):
        """Where each view stands in its cell, as a layout y: the filler at its anchor, a sight's
        views at their text, half a border lower, as their cells begin that much higher (never
        above line 1)."""
        tools = (self.tool_view(),) if self.panning() else ()
        places = [(view, anchor(view)) for view in
                  (self.filler, self.strip_floor, self.top_filler, self.below) + tools]
        if self.pan:
            places.insert(5, (self.chat, chat.bottom_place(self.chat)))
        places.insert(1, (self.strip, self.strip_place()))
        for sight in self.sights:
            texts = [(item.view, item_top(item)) for item in sight.items()]
            places += [(view, max(y - OVERLAP / 2, 0.0)) for view, y in texts]
        return places

    def wheel_places(self):
        """The views whose wheel moves the whole trip: the strip, the fillers and the scroll pad
        under the bench, ▼'s cell, and Map or Tour while they take the wheel. A sight's code
        scrolls on its own (Jakub)."""
        return self.places()[:5 + self.panning() + self.pan]

    def pinned_places(self):
        """The views the wheel does nothing to (Jakub): the sights' headers and frozen lines. A
        wheel step over them is only undone."""
        heads = [i for s in self.sights for i in [s.header_item] + s.frozen_items]
        return [(i.view, max(item_top(i) - OVERLAP / 2, 0.0)) for i in heads]

    def scroll_views(self):
        """Every view at its place; the cells move, the views do not. Views already there are
        left alone, as this runs on every wheel step. The blank views never move sideways: a
        touchpad's sideways part carried the strip's ▲▼ off to the left (Jakub)."""
        blank = [view for view, _ in self.wheel_places()]
        for view, place in self.places():
            x, y = view.viewport_position()
            x = 0.0 if view in blank else x
            if abs(y - place) > 0.5 or x != view.viewport_position()[0]:
                view.set_viewport_position((x, place), False)
        if self.editor is not None:  # its header's text sits between blank lines too
            self.editor.header.set_viewport_position((0, header_top(self.editor.header)), False)

    def read_wheel(self):
        """The wheel moves a view of wheel_places off its place: the trip takes the movement over,
        and scroll_views puts every view at its new place; the strip is already there, as its
        place follows the offset (see strip_place). A jump larger than a screen is a view being
        laid out, not the wheel; while a new layout settles, movements are only undone."""
        settling = time.time() < self.settle_until
        for view, place in self.pinned_places():
            x, y = view.viewport_position()
            if abs(y - place) > 0.5:
                view.set_viewport_position((x, place), False)
        for view, place in self.wheel_places():
            x, y = view.viewport_position()
            if abs(y - place) <= 0.5 and x == 0:
                continue
            if settling or abs(y - place) >= self.height:
                view.set_viewport_position((0.0, place), False)
                continue
            self.scroll_to(self.offset + y - place, wheel=True)
            return

    def strip_place(self):
        """Where the strip stands, so its lines are level with the code's: line BLANK_LINES is the
        first sight's code start, and every sight's code starts whole lines from it (plan.stack)."""
        first = self.sights[0].code_item.y if self.sights else 0.0
        return BLANK_LINES * self.lh + self.offset - self.lead - first

    def write_strip(self):
        """As many lines as the trip, with BLANK_LINES of room either way for the wheel."""
        code = self.items[-1]
        lines = 2 * BLANK_LINES + int((code.y + code.content) / self.lh) + 1
        self.strip.run_command("sight_walk_replace", {"text": "\n" * lines})
        self.strip.sel().clear()
        self.strip_marks = None  # drawn again (see draw_gutter)

    # Polling

    def alive(self):
        return state.READERS.get(self.window.id()) is self and self.chat.is_valid()

    def poll(self):
        """The slow loop: the conversation's bottom, the headers and the window's size."""
        if not self.alive():
            return
        chat.keep_at_bottom(self.chat)
        self.show_headers()  # they rewrap when a column is resized
        if self.ready:
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
        """A panel or a window resize changes the room. The conversation and the Tools pane
        together span the column under the fixed header, so their heights change one to one."""
        size = self.chat.viewport_extent()[1] + self.tool_view().viewport_extent()[1]
        if self.resize_base is None:
            self.resize_base = (size, self.height)
        elif abs(size - self.resize_base[0] - (self.height - self.resize_base[1])) > 0.5:
            self.height = self.resize_base[1] + size - self.resize_base[0]
            self.lead = self.centred_lead()
            self.render()
            self.draw_strip_buttons()

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
        """A line's first mark in the gutter, with an eye for marks off screen (see
        marks.gutter_icons); its second on the strip (Jakub)."""
        self.draw_strip_marks()
        first, last = marks.visible_lines(self.sights, self.offset, self.room(), self.lh)
        icons = marks.gutter_icons(self.indicators, first, last)
        for index, sight in enumerate(self.sights):
            mine = {line: icon for (i, line), icon in icons.items() if i == index and line}
            draw_icons(sight.view, sight.icons, mine)
            sight.icons = mine
            # A header's line 0 is drawn on its text line.
            header = {ROOM_LINES + 1: icons[(index, 0)]} if (index, 0) in icons else {}
            draw_icons(sight.header, sight.header_icons, header)
            sight.header_icons = header

    def draw_strip_marks(self):
        """Second marks on the strip, which scrolls with the code; drawn only when they change."""
        lines = marks.strip_icons(self.sights, self.indicators, self.lh)
        if lines != self.strip_marks:
            draw_strip_icons(self.strip, BLANK_LINES, lines)
            self.strip_marks = lines

    def draw_outlines(self):
        for index, sight in enumerate(self.sights):
            lines = set(m["line"] for m in self.indicators if m["sight"] == index)
            if lines != sight.outlines:
                draw_outlines(sight.view, lines)
                sight.outlines = lines

    # Editing

    def draw_edit_buttons(self):
        for index, sight in enumerate(self.sights):
            draw_edit_button(sight.header, sight_title(sight),
                             lambda _, i=index: self.open_editor(i, self.sights[i].begin))

    def open_editor(self, index, line):
        if self.editor is None:
            path = self.sights[index].path
            if any(v.is_dirty() for w in sublime.windows() for v in [w.find_open_file(path)] if v):
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
            if view == sight.view:
                return index
        return None

    def close_editor(self):
        self.editor.close(self.editor_closed)

    def editor_closed(self, ranges, lines, saved):
        """After Esc. Not saved (Don't Save, or no change): the trip stays as it was. Saved: the
        trip is shown again from the file, each sight at its new range, the marks on their new
        lines, and the agent's next message carries the changed ranges."""
        self.editor = None
        if not saved:
            self.render()
            return
        for k, line in lines.items():
            self.indicators[k]["line"] = line
        for i, sight in enumerate(self.sights):
            begin, end = ranges.get(i, (sight.begin, sight.end))
            self.move_range(sight, begin + sight.pad[0], end - sight.pad[1])
        self.load(self.trip.moved([s.sight for s in self.sights]), self.shown[1], self.indicators)

    def move_range(self, sight, begin, end):
        """The range as given (without the blank lines shown around it) moved to begin-end."""
        if (begin, end) == (sight.begin + sight.pad[0], sight.end - sight.pad[1]):
            return
        self.edits.append("%s, now %d-%d" % (sight.spec, begin, end))
        sight.sight = Sight(sight.sight.file, begin, end)

    def take_edits(self):
        """Ranges the user changed in the editor, for the agent's next message."""
        edits, self.edits = self.edits, []
        return {"edited": edits} if edits else {}

    # Conversation

    def show_headers(self):
        chat.show_header(self.chat_header, word("bench"), "")
        self.chat.set_name(word("bench_view"))
        chat.show_status(self.status_view, " · ".join(t for t in (self.status, self.note) if t),
                         self.stop_answer if self.note else None)
        vetting.show_tabs(self.below_header, self.tool, self.select_tool, self.pan)
        chat.show_header(self.sights_header, word("sights"), self.trip.name if self.trip else "",
                         button=(word("reset"), self.reset_sights))
        # The strip is a scroll bar's width now: its header keeps the band, without the name.
        chat.show_header(self.strip_header, "", "", help_mark=False)

    def toggle_focus(self, view):
        """To the bench, or from it back to the view used last (Jakub)."""
        if view != self.chat:
            self.window.focus_view(self.chat)
            return
        if self.browser is not None:
            self.window.focus_view(self.browser)
        elif self.touched is not None and self.touched.is_valid():
            self.window.focus_view(self.touched)
        elif self.sights:
            self.window.focus_view(self.sights[0].view)

    def note_selection(self, view):
        """The user put the caret or a selection in view: "here" is there now (Jakub)."""
        if self.sight_of(view) is not None:
            self.touched = view

    def reset_sights(self):
        """[Reset positions] in the Sights' header (alpha, Jakub): the trip shown again as given."""
        if self.sights:
            self.load(*self.shown)

    def draw_strip_buttons(self):
        """▲ in the strip's header and ▼ in its own cell under the strip, which scrolls now
        (Jakub): for a mouse without a wheel."""
        for view, line, href in ((self.strip_header, 0, "up"), (self.strip_floor, BLANK_LINES,
                                                                  "down")):
            phantoms(view, "sight_walk_strip_buttons").update([sublime.Phantom(
                sublime.Region(view.text_point(line, 0)), STRIP_BUTTON_HTML % (href, ARROWS[href]),
                sublime.LAYOUT_INLINE, self.strip_button)])

    def strip_button(self, href):
        step = sublime.load_settings(SETTINGS_FILE).get("strip_step", STRIP_STEP)
        self.scroll_to(self.offset + (-step if href == "up" else step) * self.room())

    # Tools

    def tools(self):
        return {"Map": self.map_view, "Tour": self.tour_view, vetting.SCROLL: self.below}

    def tool_view(self):
        return self.tools()[self.tool]

    def hidden_tools(self):
        return [view for name, view in self.tools().items() if name != self.tool]

    def select_tool(self, name):
        self.tool = name
        if self.ready:
            self.render()
            sublime.set_timeout(self.draw_map, SETTLE_MS)  # once the pane has its width
        self.draw_tour()

    def panning(self):
        """Map or Tour shown and taking the wheel for the panorama (Jakub)."""
        return self.pan and self.tool != vetting.SCROLL

    def toggle_panning(self):
        """primary+s: the wheel over the bench, Map and Tour moves the whole trip, or them."""
        self.pan = not self.pan
        for view in (self.map_view, self.tour_view):
            vetting.set_panning(view, self.pan)
        self.chat.settings().set("scroll_past_end", self.pan)  # so the wheel moves it down too
        self.show_headers()
        self.select_tool(self.tool)  # lays out again, draws the tools at their new place

    # An informator and its tour (Jakub)

    def open_tour(self, path, tour=None):
        """The informator in path and a tour of it, written by hand in the file tour or else
        all its trips in reading order, in the Tour tab; the first trip not walked yet shown."""
        self.informator = ontology.informator_from(read_json(path), lambda file: read_json(
            os.path.join(os.path.dirname(path), file)))
        self.informator_root, self.informator_path = repo_root(path), path
        self.informator.transcripts = read_transcripts(path)
        self.tour = ontology.tour_from(read_json(tour), self.informator) if tour \
            else ontology.tour(self.informator)
        if not tour:
            self.tour.name = "%s: %s" % (self.informator.name, word("all_trips"))
        self.walked = vetting.read_walked(self.informator.id)
        self.tool = "Tour"
        first = next((t for t in self.tour if t.id not in self.walked), self.tour.members[0])
        self.tour_link("open:" + first.id)

    def tour_link(self, href):
        """open:<trip> shows a trip of the tour; tick:<trip> ticks or unticks it as walked,
        only by hand (Jakub)."""
        what, _, key = href.partition(":")
        if what == "open":
            self.keep_transcript()
            chat.set_transcript(self.informator.transcripts.get(key, ""))
            self.tour_trip = key
            self.load(self.informator.member(key), self.informator_root)
        elif what == "tick":
            self.walked ^= {key}
            vetting.save_walked(self.informator.id, self.walked)
        self.draw_tour()

    def keep_transcript(self):
        """The bench's conversation kept under the tour's trip shown (Jakub), so after Sublime
        closes it goes on from there. After every message, in a file beside the informator's that
        git ignores (Jakub: conversations stay out of git)."""
        if self.informator is None or self.trip is None or self.trip.id != self.tour_trip:
            return
        self.informator.transcripts[self.tour_trip] = chat.TRANSCRIPT
        with open(transcripts_path(self.informator_path), "w", encoding="utf-8") as f:
            json.dump(self.informator.transcripts, f, indent=1, ensure_ascii=False)

    def draw_tour(self):
        vetting.show_tour(self.tour_view, self.tour, self.walked,
                             self.trip.id if self.trip else None, self.tour_link)

    def draw_map(self):
        if self.sights:
            nodes = [n for i in range(len(self.sights)) for n in self.map_nodes(i)]
            definitions = {}
            for node in nodes:
                definitions.setdefault(node.key[0], []).append(node.key[1])
            arrows = callmap.edges(definitions, [(t.type, t.source, t.target)
                                                 for t in self.trip.transitions])
            vetting.draw_map(self.map_view, nodes, arrows, ("Helvetica", "#222222", "#888888"))

    def map_nodes(self, index):
        """The map's nodes for a sight: its first definition and every line a call in the trip
        points at, with the class around them, the file and its hue."""
        sight = self.sights[index]
        lines = sight.view.substr(sublime.Region(0, sight.view.size())).split("\n")
        # A sight without a function (a script's top-level code) is named by its range (Jakub).
        main = callmap.first_definition(lines, sight.begin, sight.end) or (
            sight.begin, sight_title(sight).rsplit("/", 1)[-1])
        targets = {t.target[1] for t in self.trip.transitions
                   if t.type == "calls" and len(t.target) == 2 and t.target[0] == index}
        colour = tint_color("#ffffff", hue_for(sight.path), 0.25)
        return [callmap.Node((index, line), defined_name(lines, line, main), self.owner(sight),
                             display_path(sight.path), colour)
                for line in sorted({main[0]} | targets)]

    def owner(self, sight):
        """The class around a sight, from its frozen lines, or ""."""
        found = [CLASS.match(v.substr(v.line(v.text_point(line - 1, 0))))
                 for line, v in sight.frozen]
        return next((m.group(1) for m in reversed(found) if m), "")

    def note_waiting(self, note):
        self.note = note
        self.show_headers()

    def stop_answer(self):
        """[Stop] or Esc while an answer is on its way (Jakub): the agent's further say, show and
        point are refused until it waits for the user again (see bridge)."""
        if not self.note:
            return
        state.STOPPED, self.note = True, ""
        self.withdraw_unread_messages()
        self.say(word("stopped"), prefix="")

    def withdraw_unread_messages(self):
        """A message no agent has taken yet is withdrawn."""
        while not state.INBOX.empty():
            state.INBOX.get_nowait()

    def folder(self):
        """Where a guide started for this trip works: the first sight's repository."""
        if not self.sights:
            return self.root
        path = self.sights[0].path
        return repo_root(path) or os.path.dirname(path)

    def say(self, text, status=None, prefix="A: "):
        if prefix == "A: ":
            self.note = ""  # the answer has come
        if status is not None:
            self.status = status
        self.show_headers()
        chat.say(self.chat, text, prefix)
        self.keep_transcript()

    def context(self):
        if not self.ready:
            return {"focus": None, "visible": []}
        context = {"focus": None, "visible": plan.visible_specs(self.sights, self.offset,
                                                                self.room())}
        view = self.touched
        index = self.sight_of(view) if view is not None and view.is_valid() else None
        if index is None:
            return context
        spec = self.sights[index].spec
        line = view.rowcol(view.sel()[0].b)[0] + 1 if len(view.sel()) else None
        context.update(focus=spec, here="%s:%s" % (spec.rsplit(":", 1)[0], line))
        if selected_text(view):
            context["selected"] = selected_text(view)
        return context


def transcripts_path(informator_path):
    """sightwalk.json's conversations: sightwalk.transcripts.json, ignored by git."""
    return os.path.splitext(informator_path)[0] + ".transcripts.json"


def read_transcripts(informator_path):
    try:
        with open(transcripts_path(informator_path), encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return {}


def read_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)
