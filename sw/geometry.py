"""Where the reader's columns and cells lie: the bench, the strip and the Sights side by side, the
headers' and the conversation's heights, and every sight's cells in the virtual document (see
plan), in px from the top of the screen, x as shares of the width. Reader inherits it."""

import sublime

from .config import (DEFAULT_BENCH_SIDE, DEFAULT_CONVERSATION_HEIGHT, GUTTER_PX, INSET, OVERLAP,
                     SETTINGS_FILE, STRIP_PX)


class Geometry:
    def share(self, px):
        """px as a share of the window's width. The conversation has no gutter, so its text is
        about as wide as its column."""
        width = self.chat.viewport_extent()[0] / max(self.bench_width, 0.01)
        return px / max(width, 1)

    def spans(self):
        """(bench, sights): the x spans of the Vetting Bench and of the Sights, as shares of the
        width. The bench is left of the Sights or, by the setting bench_side, right of them; the
        scroll strip stands between them."""
        w, s = self.bench_width, self.strip_share()
        if self.bench_side() == "right":
            return (1.0 - w, 1.0), (0.0, 1.0 - w - s)
        return (0.0, w), (w + s, 1.0)

    def strip_span(self):
        w, s = self.bench_width, self.strip_share()
        if self.bench_side() == "right":
            return 1.0 - w - s, 1.0 - w
        return w, w + s

    def strip_share(self):
        """STRIP_PX as a share of the width; a guess until the bench has been laid out."""
        return self.share(STRIP_PX) if self.ready else 0.06

    def bench_side(self):
        return sublime.load_settings(SETTINGS_FILE).get("bench_side", DEFAULT_BENCH_SIDE)

    def column(self):
        """The Sights as shares of the window's width: their left edge, the right edge of a
        sight's gutter, their right edge, and a border's width."""
        left, right = self.spans()[1]
        return left, left + self.share(GUTTER_PX), right, self.share(OVERLAP)

    def conversation_rows(self):
        """The bottoms of the conversation's header and of the conversation, in px; 0, 0 until
        calibrated. The Tools pane takes the rest of the column."""
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
        # The headers reach above the screen, so their own border does not leave a slit there
        # through which the code scrolled under them shows (Jakub).
        rects, views = [(left, -OVERLAP, right, self.head() + OVERLAP)], [self.sights_header]
        lead_bottom = self.head() + self.lead - self.offset
        if lead_bottom > self.head() + 1:
            rects.append((left, self.head(), right, lead_bottom))
            views.append(self.top_filler)
        for sight in self.sights:
            more_rects, more_views = self.sight_cells(sight, column)
            rects += more_rects
            views += more_views
        # The filler takes half the border with the last sight, like any neighbour (Jakub).
        end = max(r[3] for r in rects[1:]) - OVERLAP
        rects.append((left, end, right, max(end, 0.0) + self.height))
        views.append(self.filler)
        strip_left, strip_right = self.strip_span()
        floor = self.height - self.floor_height()
        rects += [(strip_left, -OVERLAP, strip_right, self.head() + OVERLAP),
                  (strip_left, self.head(), strip_right, floor + OVERLAP),
                  (strip_left, floor, strip_right, self.height)]
        views += [self.strip_header, self.strip, self.strip_floor]
        return rects, views

    def floor_height(self):
        """▼'s cell under the strip: two of its lines, room for the larger arrow."""
        return 2 * self.strip_floor.line_height() + self.overhead

    def sight_cells(self, sight, column):
        """A sight's header and code. Earlier cells are drawn over later ones, and each neighbour
        takes half the border between them, so neither covers the other's text (Jakub)."""
        left, _, right, _ = column
        rects, views = [], []
        for item in sight.items():
            top = self.head() + self.lead + item.y - self.offset - OVERLAP / 2
            rects.append((left, top, right, top + item.content + self.overhead + OVERLAP))
            views.append(item.view)
        return rects, views
