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
        self.y = 0.0


class Sight:
    """A sight: one range of a file, its views, cells and drawn marks."""

    def __init__(self, spec, path, begin, end):
        self.spec, self.path, self.begin, self.end = spec, path, begin, end
        self.view = None
        self.header = None
        self.line_one = None  # the extra views of a sight at line 1 (see line_one)
        self.header_item = None
        self.frozen = []  # (line, view): the lines that open the blocks around the range (Jakub)
        self.frozen_items = []
        self.pad = (0, 0)  # blank lines shown above and below the range as given (spec.breathing)
        self.code_item = None
        self.header_icons = {}
        self.icons = {}
        self.outlines = set()

    def items(self):
        """The sight's cells from top to bottom: header, frozen lines, code."""
        return [self.header_item] + self.frozen_items + [self.code_item]

    def code_views(self):
        """Every view showing the sight's code."""
        return [self.view] + (self.line_one.views() if self.line_one is not None else [])

    def all_views(self):
        """Every view the sight made: code, header, frozen lines."""
        return [v for v in self.code_views() + [self.header] + [v for _, v in self.frozen] if v]


def stack(items, overhead):
    y = 0.0
    for item in items:
        item.y = y
        y += item.content + overhead


def max_offset(items, height, overhead):
    # A last sight that fits on the screen with its header can scroll up until its header is at
    # the top. A taller one scrolls only until the end of its range reaches the bottom.
    header, code = next(i for i in reversed(items) if i.header), items[-1]
    bottom = code.y + code.content + overhead
    if bottom - header.y <= height:
        return header.y
    return bottom - height


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


def offset_range(items, height, overhead, lead_px):
    """How far the trip scrolls: a short one from the ceiling to the floor (Jakub), a taller one
    from its top until its end (see max_offset)."""
    free = free_room(items, height, overhead)
    if free > 0:
        return lead_px - free, lead_px
    return 0.0, max_offset(items, height, overhead)


def visible_specs(sights, offset, height):
    end = offset + height
    return [sight.spec for sight in sights
            if sight.code_item.y < end and sight.code_item.y + sight.code_item.content > offset]

