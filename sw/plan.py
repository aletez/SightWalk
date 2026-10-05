"""Geometry of the virtual document. Pure functions, no Sublime API."""


class Item:
    def __init__(self, view, top_layout, content):
        self.view = view
        self.top_layout = top_layout
        self.content = content
        self.y = 0.0


class Segment:
    def __init__(self, spec, path, begin, end):
        self.spec, self.path, self.begin, self.end = spec, path, begin, end
        self.view = None
        self.header = None
        self.code_item = None
        self.header_item = None
        self.header_icons = {}
        self.icons = {}
        self.outlines = set()


def stack(items, overhead):
    y = 0.0
    for item in items:
        item.y = y
        y += item.content + overhead


def max_offset(items, height, overhead):
    # A last pane that fits on the screen with its header can scroll up until its header is at
    # the top. A taller one scrolls only until the end of its range reaches the bottom.
    header, code = items[-2], items[-1]
    bottom = code.y + code.content + overhead
    if bottom - header.y <= height:
        return header.y
    return bottom - height


def visible_cells(items, offset, height, overhead):
    cells = []
    for item in items:
        top = max(item.y, offset)
        bottom = min(item.y + item.content + overhead, offset + height)
        if bottom > top:
            cells.append([item, top - offset, bottom - offset])
        if bottom >= offset + height:
            break
    return cells


def merge_slivers(cells, min_cell):
    # A sliver too thin for a group is absorbed by its neighbour, which then shows a little context.
    merged = []
    for cell in cells:
        if merged and cell[2] - cell[1] < min_cell:
            merged[-1][2] = cell[2]
        elif merged and merged[-1][2] - merged[-1][1] < min_cell:
            cell[1] = merged.pop()[1]
            merged.append(cell)
        else:
            merged.append(cell)
    return merged


def fill_bottom(cells, filler, height, min_cell):
    # Below the last pane the column shows an empty view, so every pane keeps the height of its
    # range. A gap too thin for a group of its own goes to the last pane while scrolling.
    end = cells[-1][2] if cells else 0.0
    if height - end >= min_cell:
        cells.append([filler, end, height])
    elif cells:
        cells[-1][2] = height
    return cells


def viewport_y(item, offset, top):
    return item.top_layout + offset + top - item.y


def focus_segment(segments, offset, height, overhead):
    mid = offset + height / 2

    def distance(seg):
        lo = seg.code_item.y
        hi = lo + seg.code_item.content + overhead
        return 0 if lo <= mid <= hi else min(abs(mid - lo), abs(mid - hi))

    return min(segments, key=distance) if segments else None


def visible_specs(segments, offset, height):
    end = offset + height
    return [seg.spec for seg in segments
            if seg.code_item.y < end and seg.code_item.y + seg.code_item.content > offset]
