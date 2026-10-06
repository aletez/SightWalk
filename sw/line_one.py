"""A sight starting at its file's line 1. Its view cannot move up past line 1, so the wheel over it
could not scroll the reader up, and a long touchpad swipe would stop on it. Such a sight is three
views (Jakub):

- line 1's gutter: the sight's own view, in a cell as wide as the gutter;
- line 1's code: a twin, with room above it that the sight's header hides;
- the rest of the sight, gutter and code: a second view of the file, which has line 1 above it to
  move into, so it takes the wheel.
"""

from . import twin
from .config import GUTTER_REACH, OVERLAP
from .views import draw_gap, draw_icons, draw_outlines, prepare_code_view


def line_top(view, line):
    return view.text_to_layout(view.text_point(line - 1, 0))[1]


class LineOne:
    def __init__(self, window, sight, original):
        self.sight = sight
        self.rest = prepare_code_view(window, original, True)
        self.twin = twin.make(window, sight.spec, sight.view, self.first_line())

    def first_line(self):
        return self.sight.view.substr(self.sight.view.line(0))

    def misalignment(self):
        """px by which line 1's code (in the twin) starts left of the code below it."""
        def x(view):
            return view.text_to_window(view.text_point(1, 0))[0]
        return x(self.rest) - x(self.twin)

    def views(self):
        return [self.rest, self.twin]

    def places(self):
        """Measured afresh each time: phantoms are laid out late, and a stale place would read
        as the wheel."""
        return [(self.rest, line_top(self.rest, 2)), (self.twin, twin.content_top(self.twin))]

    def rects(self, column, top, bottom, lh):
        """Cells in drawing order, each over the next, with the views they show. column: (left,
        gutter's right edge, right) as shares of the width; top, bottom: the sight's cell in px.
        Line 1's view reaches down to line 10 under the rest: Sublime sizes a gutter by the line
        numbers it shows, so its gutter is as wide as the rest's (Jakub)."""
        left, split, right, overlap = column
        half = OVERLAP / 2
        first = top + half + lh  # where line 2 starts
        reach = min(bottom, first + (GUTTER_REACH - 1) * lh)
        # Each neighbour takes half of a border, as between sights.
        rects = [(left, first - half, right, bottom), (left, top, split + overlap, reach),
                 (split, top, right, first + half)]
        return rects, [self.rest, self.sight.view, self.twin]

    def draw_gaps(self):
        draw_gap(self.rest, 2, self.sight.end)
        draw_gap(self.twin, 2, 2)

    def draw_icons(self, old, new):
        draw_icons(self.rest, old, new)  # the rest's gutter shows them from line 2 on

    def draw_outlines(self, lines):
        draw_outlines(self.rest, lines)
        draw_outlines(self.twin, {2} if 1 in lines else set())  # the twin's line 2 is line 1

    def refill(self):
        """After the file was saved, the twin shows its new line 1."""
        twin.fill(self.twin, self.first_line(), self.sight.view.line_height())

    def close(self):
        for view in self.views():
            if view.is_valid():
                view.close()
