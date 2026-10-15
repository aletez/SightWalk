"""The editor: the file itself, laid over the code column, opened from a sight (Enter or the
header's button) and closed with Esc or primary+w. The sights are copies of the file; the editor's
edits move held ranges and marks, and when it closes after a save, the trip is shown again from
the file with the new ranges."""

import os

import sublime

from .marks import icon_colour
from .spec import display_path
from .views import draw_icons, draw_outlines, make_header, wait_until_loaded


def open_live(window, path):
    """The file itself, the one view a trip shows of it that is not a copy (Jakub)."""
    view = window.open_file(path)
    view.settings().set("sight_walk_editor", True)
    return view


class Editor:
    def __init__(self, reader, index, line):
        sight = reader.sights[index]
        self.reader, self.path = reader, sight.path
        self.mtime = os.path.getmtime(sight.path)
        self.view = open_live(reader.window, sight.path)
        self.header = make_header(reader.window, display_path(sight.path), sight.view)
        for source, target in ((sight.view, self.view), (sight.header, self.header)):
            target.settings().set("color_scheme", source.settings().get("color_scheme"))
        wait_until_loaded([self.view], lambda: self.start(line))

    def start(self, line):
        # Line for line with the sight it covers; once loaded, or the syntax's setting wins.
        self.view.settings().set("word_wrap", False)
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
        draw_outlines(self.view, {m["line"]: icon_colour(m["icon"]) for _, m in mine})

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
        on_closed(ranges, lines, saved) runs only if it did close (not on Cancel); saved: the file
        on disk changed since the editor opened."""
        ranges, lines = self.read_back()

        def done(closed):
            if closed:
                self.header.close()
                on_closed(ranges, lines, os.path.getmtime(self.path) != self.mtime)

        self.view.close(done)
