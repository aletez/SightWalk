"""The editor: a full, normal view of one file laid over the code column, opened from a pane and
closed with primary+w. It shares the buffer with the panes, so its edits move the tracked ranges
and marks; the reader catches up when it closes."""

import sublime

from .spec import display_path
from .views import draw_icons, draw_outlines, make_header

EDITOR_SETTINGS = ("sight_walk", "sight_walk_code", "word_wrap", "scroll_past_end")


def clone_for_editing(window, view):
    window.focus_view(view)
    window.run_command("clone_file")
    clone = window.active_view()
    # A clone copies the pane's settings; the editor behaves like any other view.
    for key in EDITOR_SETTINGS:
        clone.settings().erase(key)
    clone.settings().set("sight_walk_editor", True)
    clone.set_read_only(False)  # read-only belongs to the buffer: the panes open up too
    return clone


class Editor:
    def __init__(self, reader, index, line):
        seg = reader.segments[index]
        self.reader, self.path = reader, seg.path
        self.view = clone_for_editing(reader.window, seg.view)
        self.header = make_header(reader.window, display_path(seg.path), self.view)
        for source, target in ((seg.view, self.view), (seg.header, self.header)):
            target.settings().set("color_scheme", source.settings().get("color_scheme"))
        self.track()
        point = self.view.text_point(line - 1, 0)
        self.view.sel().clear()
        self.view.sel().add(sublime.Region(point))
        self.view.show_at_center(point)

    def mine(self, items, path_of):
        return [(k, item) for k, item in enumerate(items) if path_of(item) == self.path]

    def track(self):
        """Hidden regions for the panes' ranges and the marks; edits move them. The marks are
        also drawn, so the user sees where to edit."""
        segs, view = self.reader.segments, self.view
        for i, seg in self.mine(segs, lambda s: s.path):
            region = sublime.Region(view.text_point(seg.begin - 1, 0),
                                    view.line(view.text_point(seg.end - 1, 0)).b)
            view.add_regions("sight_walk_range_%d" % i, [region], "", "", sublime.HIDDEN)
        marks = self.mine(self.reader.indicators, lambda m: segs[m["seg"]].path)
        for k, mark in marks:
            point = view.text_point(mark["line"] - 1, 0)
            view.add_regions("sight_walk_at_%d" % k, [sublime.Region(point)], "", "", sublime.HIDDEN)
        draw_icons(view, {}, {m["line"]: m["icon"] for _, m in marks})
        draw_outlines(view, set(m["line"] for _, m in marks))

    def read_back(self):
        """New (begin, end) per pane and new line per mark, from the tracked regions."""
        def row(point):
            return self.view.rowcol(point)[0] + 1
        ranges, lines = {}, {}
        for i in range(len(self.reader.segments)):
            found = self.view.get_regions("sight_walk_range_%d" % i)
            if found:
                ranges[i] = (row(found[0].a), row(found[0].b))
        for k in range(len(self.reader.indicators)):
            found = self.view.get_regions("sight_walk_at_%d" % k)
            if found:
                lines[k] = row(found[0].a)
        return ranges, lines

    def close(self, on_closed):
        """Closes the view the usual way, so Sublime asks about unsaved changes itself.
        on_closed(ranges, lines) runs only if it did close (not on Cancel)."""
        ranges, lines = self.read_back()

        def done(closed):
            if closed:
                self.header.close()
                on_closed(ranges, lines)

        self.view.close(done)
