"""Geometry of the virtual document. Pure functions, no Sublime API."""


class Item:
    """A cell of the virtual document: the view it shows, the layout y of the view's text at the
    cell's top, the content's height, and the cell's y in the document (set by stack)."""

    def __init__(self, view, top_layout, content):
        self.view = view
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
        self.code_item = None
        self.header_icons = {}
        self.icons = {}
        self.outlines = set()

    def code_views(self):
        """Every view showing the sight's code."""
        return [self.view] + (self.line_one.views() if self.line_one is not None else [])


def stack(items, overhead):
    y = 0.0
    for item in items:
        item.y = y
        y += item.content + overhead


def max_offset(items, height, overhead):
    # A last sight that fits on the screen with its header can scroll up until its header is at
    # the top. A taller one scrolls only until the end of its range reaches the bottom.
    header, code = items[-2], items[-1]
    bottom = code.y + code.content + overhead
    if bottom - header.y <= height:
        return header.y
    return bottom - height


def focus_sight(sights, offset, height, overhead):
    mid = offset + height / 2

    def distance(sight):
        lo = sight.code_item.y
        hi = lo + sight.code_item.content + overhead
        return 0 if lo <= mid <= hi else min(abs(mid - lo), abs(mid - hi))

    return min(sights, key=distance) if sights else None


def visible_specs(sights, offset, height):
    end = offset + height
    return [sight.spec for sight in sights
            if sight.code_item.y < end and sight.code_item.y + sight.code_item.content > offset]

