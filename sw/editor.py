"""The editor: a full, normal view of one file laid over the code column, opened from a sight
(Enter or the header's button) and closed with Esc or primary+w. It shares the buffer with the
sights, so its edits move the held ranges and marks; the reader catches up when it closes."""

import sublime

from .spec import display_path
from .views import draw_icons, draw_outlines, make_header

EDITOR_SETTINGS = ("sight_walk", "sight_walk_code", "word_wrap", "scroll_past_end")


def clone_for_editing(window, view):
    window.focus_view(view)
    window.run_command("clone_file")
    clone = window.active_view()
    # A clone copies the sight's settings; the editor behaves like any other view.
    for key in EDITOR_SETTINGS:
        clone.settings().erase(key)
    clone.settings().set("sight_walk_editor", True)
    clone.set_read_only(False)  # read-only belongs to the buffer: the sights open up too
    return clone


class Editor:
    def __init__(self, reader, index, line):
        sight = reader.sights[index]
        self.reader, self.path = reader, sight.path
        self.view = clone_for_editing(reader.window, sight.view)
        self.header = make_header(reader.window, display_path(sight.path), self.view)
        for source, target in ((sight.view, self.view), (sight.header, self.header)):
            target.settings().set("color_scheme", source.settings().get("color_scheme"))
        self.track()
        point = self.view.text_point(line - 1, 0)
        self.view.sel().clear()
        self.view.sel().add(sublime.Region(point))
        self.view.show_at_center(point)

    def track(self):
        """Hidden regions for this file's sight ranges and marks: edits move them, and read_back
        reads where they went. The marks are also drawn, so the user sees where to edit."""
        sights = self.reader.sights
        for i, sight in enumerate(sights):
            if sight.path == self.path:
                self.hold("range_%d" % i, sight.begin, sight.end)
        mine = [(k, m) for k, m in enumerate(self.reader.indicators)
                if sights[m["sight"]].path == self.path]
        for k, mark in mine:
            self.hold("at_%d" % k, mark["line"], mark["line"])
        draw_icons(self.view, {}, {m["line"]: m["icon"] for _, m in mine})
        draw_outlines(self.view, set(m["line"] for _, m in mine))

    def hold(self, key, begin, end):
        """A hidden region from the start of line begin to the end of line end."""
        view = self.view
        region = sublime.Region(view.text_point(begin - 1, 0),
                                view.line(view.text_point(end - 1, 0)).b)
        view.add_regions("sight_walk_" + key, [region], "", "", sublime.HIDDEN)

    def rows(self, key):
        """The first and last line of a held region now, or None."""
        found = self.view.get_regions("sight_walk_" + key)
        if not found:
            return None
        return tuple(self.view.rowcol(p)[0] + 1 for p in (found[0].a, found[0].b))

    def read_back(self):
        """New (begin, end) per sight and new line per mark, from the held regions."""
        ranges = {i: self.rows("range_%d" % i) for i in range(len(self.reader.sights))}
        marks = {k: self.rows("at_%d" % k) for k in range(len(self.reader.indicators))}
        return ({i: r for i, r in ranges.items() if r},
                {k: r[0] for k, r in marks.items() if r})

    def close(self, on_closed):
        """Closes the view the usual way, so Sublime asks about unsaved changes itself.
        on_closed(ranges, lines) runs only if it did close (not on Cancel)."""
        ranges, lines = self.read_back()

        def done(closed):
            if closed:
                self.header.close()
                on_closed(ranges, lines)

        self.view.close(done)
