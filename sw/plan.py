"""Geometry of the virtual document. Pure functions, no Sublime API."""


class Item:
    """A cell of the virtual document: the view it shows, the layout y of the view's text at the
    cell's top, the content's height, and the cell's y in the document (set by stack)."""

    def __init__(self, view, top_layout, content, header=False, line=None):
        self.view = view
        self.header = header
        self.line = line  # the file line at the cell's top, for a code cell (measured afresh)
        self.top_layout = top_layout
        self.content = content
        self.lead = 0.0  # room above line (a "…" of its own), part of the cell
        self.y = 0.0


class Pane:
    """A sight as shown (ontology.Sight): the range on screen (with the blank lines around it),
    its file's path, its views, cells and drawn marks."""

    def __init__(self, sight, path, begin, end):
        self.sight, self.path, self.begin, self.end = sight, path, begin, end
        self.view = None
        self.header = None
        self.header_item = None
        self.frozen = []  # (line, view): the lines that open the blocks around the range (Jakub)
        self.frozen_items = []
        self.pad = (0, 0)  # blank lines shown above and below the range as given (spec.breathing)
        self.room = (0, 0)  # lines of "…" added above and below the range (spec.elided)
        self.ellipses = {}  # "above"/"below": (line, block) of each "…" drawn
        self.code_item = None
        self.header_icons = {}
        self.icons = {}
        self.outlines = {}

    @property
    def spec(self):
        return self.sight.spec

    def items(self):
        """The sight's cells from top to bottom: header, frozen lines, code."""
        return [self.header_item] + self.frozen_items + [self.code_item]

    def all_views(self):
        """Every view the sight made: code, header, frozen lines."""
        return [v for v in [self.view, self.header] + [v for _, v in self.frozen] if v]


def stack(items, overhead, lh=None):
    """Each item's y, one under another. With lh, every sight's code starts a whole number of
    lines below the first sight's, so the scroll strip's lines stay level with the code: the slack
    (under a line) goes to the bottom of the code above, never between a header and its code."""
    y, first, code = 0.0, None, None
    for group in sight_groups(items):
        start = y + sum(i.content + overhead for i in group[:-1])  # where this code would start
        if lh and first is not None:
            slack = (first - start) % lh
            slack = 0.0 if lh - slack < 1e-6 else slack
            code.content += slack
            y, start = y + slack, start + slack
        first = start if first is None else first
        for item in group:
            item.y = y
            y += item.content + overhead
        code = group[-1]


def sight_groups(items):
    """items cut before every header: one list per sight, its code last."""
    groups = []
    for item in items:
        if item.header or not groups:
            groups.append([])
        groups[-1].append(item)
    return groups


def free_room(items, height, overhead):
    """The room a trip shorter than the screen leaves free; 0 for a taller one."""
    code = items[-1]
    return max(height - (code.y + code.content + overhead), 0.0)


def lead(items, height, overhead, middle):
    """Room above a short trip: its middle level with middle, the window's (Jakub), as far as it
    fits. A trip as tall as the screen or taller starts at the top."""
    free = free_room(items, height, overhead)
    total = height - free
    return min(max(middle - total / 2, 0.0), free)


def offset_range(items, height, overhead, lead_px, floor_px):
    """How far the trip scrolls: down to the floor of the screen (a short one) or its top (a
    taller one), and up until its end is level with the bench's floor, floor_px below the
    Sights' top (Jakub: scrolling brings the code level with the eyes reading the bench). A
    short one starts centred (lead_px)."""
    free = free_room(items, height, overhead)
    low = lead_px - free if free > 0 else 0.0
    end = items[-1].y + items[-1].content + overhead
    return low, max(lead_px + end - floor_px, lead_px if free > 0 else 0.0)


def visible_specs(sights, offset, height):
    end = offset + height
    return [sight.spec for sight in sights
            if sight.code_item.y < end and sight.code_item.y + sight.code_item.content > offset]

