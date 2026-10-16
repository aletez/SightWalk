"""Making views and drawing on them, and the window's layout."""

import os

import sublime

from .config import (BENCH_FONTS, SETTINGS_FILE, GAP_PX, OVERLAP, ROOM_LINES, SETTLE_MS, BLANK_LINES,
                     STRIP_ICON_SHIFT)
from . import marks
from .words import word

SIDE_SETTINGS = (("gutter", False), ("line_numbers", False), ("draw_indent_guides", False),
                 ("highlight_line", False), ("scroll_past_end", True), ("sight_walk", True))
# No fold buttons, so the gutter is narrower (Jakub).
CODE_SETTINGS = (("word_wrap", False), ("scroll_past_end", True), ("sight_walk", True),
                 ("sight_walk_code", True), ("fold_buttons", False))
# Everything that decides how tall a line is. Copied from the code view, so that view settings
# override syntax-specific ones (Plain Text may have its own font) and every line has one height.
FONT_KEYS = ("font_face", "font_size", "font_options", "line_padding_top", "line_padding_bottom")
ICONS = "Packages/SightWalk/icons/%s.png"
ICON_FLAGS = sublime.DRAW_NO_FILL | sublime.DRAW_NO_OUTLINE
# On the scroll strip: a little shorter than the line, which an image as tall as it leaves as it is
# (measured by Jakub: 17 px stays 17, 19 makes the line 19).
STRIP_IMG = '<img src="res://Packages/SightWalk/icons/%s@3x.png" width="%d" height="%d">'
FADED = "color(var(--foreground) alpha(0.45))"
# Faded and outlined at all times, so it reads as a control, not as text.
BUTTON_STYLE = ('style="color: %s; text-decoration: none; border: 1px solid %s; border-radius: 3px; '
                'padding: 0 4px"' % (FADED, FADED))


def button_html(label, href="edit"):
    """A faded, outlined button: the sign of something read-only (Jakub)."""
    return '<a href="%s" %s>%s</a>' % (href, BUTTON_STYLE, label)
# A zero-width space: Sublime leaves out an empty phantom.
GAP_HTML = '<span style="padding-left: %dpx">&#8203;</span>' % GAP_PX
# view id: what SightWalk keeps for that view (phantom sets, text last drawn). Forgotten when the
# view closes: Sublime reuses the ids of closed views.
KEPT = {}


# Kept per view

def kept(view):
    return KEPT.setdefault(view.id(), {})


def phantoms(view, key):
    """The view's phantom set named key, made on first use."""
    mine = kept(view)
    if key not in mine:
        mine[key] = sublime.PhantomSet(view, key)
    return mine[key]


def forget(view):
    KEPT.pop(view.id(), None)


# The window

def hide_chrome(window):
    window.set_tabs_visible(False)
    window.set_sidebar_visible(False)
    window.set_minimap_visible(False)


def wait_until_loaded(views, callback):
    if any(v.is_loading() for v in views):
        sublime.set_timeout(lambda: wait_until_loaded(views, callback), SETTLE_MS)
    else:
        callback()


def to_layout(rects, total):
    """rects: (x0, y0, x1, y1), x as a share of the width and y in px, in group order."""
    xs = sorted(set(x for r in rects for x in (r[0], r[2])))
    ys = sorted(set(y for r in rects for y in (r[1], r[3])))
    col = {x: i for i, x in enumerate(xs)}
    row = {y: i for i, y in enumerate(ys)}
    cells = [[col[r[0]], row[r[1]], col[r[2]], row[r[3]]] for r in rects]
    return {"cols": xs, "rows": [y / total for y in ys], "cells": cells}


def reader_layout(code_rects, total, top, split, bench, front=(), editor=None, status=0.0):
    """code_rects: the Sights' rectangles, in drawing order (earlier is on top). Groups in order:
    the editor if open; once top is known, the Tools pane; the Sights; the conversation and, once
    top is known, its header and the Tools pane's header.
    top: the conversation header's bottom, split: the conversation's bottom (px).
    bench: the Vetting Bench's (left, right) as shares of the width.
    front: rects whose groups come before all but the editor's, so they are drawn over the bench
    and the Tools pane: the strip, reaching over them while they take the wheel (Jakub: a view
    reaching over another gets a shadow on its right edge, so the strip reaches, not they).
    editor: (header height, left, right, top) or None.
    status: the status line's height (px), at the conversation's bottom; its group comes last."""
    rects = list(code_rects)
    x0, x1 = bench
    if not top:
        return to_layout(list(front) + rects + [(x0, 0.0, x1, total)], total)
    # The Tools pane's header is as tall as the bench's, and stays put while the pane scrolls.
    below = split + top
    rects = list(front) + [(x0, below, x1, total)] + rects + [
        (x0, top, x1, split - status), (x0, -OVERLAP, x1, top + OVERLAP),
        (x0, split, x1, below + OVERLAP), (x0, split - status, x1, split)]
    if editor:
        header, left, right, dy = editor
        rects = [(left, dy, right, dy + header + OVERLAP), (left, dy + header, right, total)] + rects
    return to_layout(rects, total)


# Making views

def make_side_view(window, name, extra):
    view = window.new_file()
    view.set_scratch(True)
    view.set_name(name)
    settings = view.settings()
    for key, value in SIDE_SETTINGS + tuple(extra.items()):
        settings.set(key, value)
    return view


def make_browser(window, folder):
    """The FileBrowser package's view of folder, for a trip with no sights yet (Jakub); a blank
    view when that package is not installed."""
    view = window.new_file()
    view.set_scratch(True)
    if not sublime.find_resources("dired.sublime-syntax"):
        return view
    view.set_syntax_file("Packages/FileBrowser/dired.sublime-syntax")
    view.settings().set("dired_path", folder.rstrip(os.sep) + os.sep)
    view.settings().set("dired_rename_mode", False)
    view.run_command("dired_refresh", {"reset_sels": True})
    return view


def make_blank_view(window, name):
    """Blank lines either way of the caret's line, the anchor: an invisible view that takes the
    wheel both ways."""
    view = make_side_view(window, name, {"word_wrap": False, "sight_walk_blank": True})
    view.run_command("sight_walk_replace", {"text": "\n" * (2 * BLANK_LINES)})
    view.sel().clear()  # no caret: a click there puts none either (see on_selection_modified)
    view.set_read_only(True)
    return view


def anchor(view):
    """The layout y a blank view stands at."""
    return BLANK_LINES * view.line_height()


class FileCopy:
    """A file's text read from disk, with the syntax Sublime would give it."""

    def __init__(self, path):
        with open(path, encoding="utf-8", errors="replace") as f:
            self.text = f.read()
        self.lines = self.text.split("\n")
        self.syntax = sublime.find_syntax_for_file(path, self.lines[0] if self.lines else "")


def make_copy(window, copy, name):
    """A sight's view: a scratch copy of the file, not the file, so no two views of a file share a
    buffer (phantoms, read-only) and nothing can change the file but the editor (Jakub)."""
    view = window.new_file()
    view.set_scratch(True)
    view.set_name(name)
    if copy.syntax is not None:
        view.assign_syntax(copy.syntax)
    view.run_command("sight_walk_replace", {"text": copy.text})
    for key, value in CODE_SETTINGS:
        view.settings().set(key, value)
    view.set_read_only(True)  # editing happens in the editor
    return view


def bench_font(view):
    """A proportional font for the conversation: narration reads more easily in it (Jakub).
    bench_font_face is a font, or one per system ({"osx": …, "windows": …, "linux": …}); "" keeps
    the editor's font. The size is the bench syntax's (SightWalkChat.sublime-settings), so it is
    not set here."""
    face = sublime.load_settings(SETTINGS_FILE).get("bench_font_face", BENCH_FONTS)
    if isinstance(face, dict):
        face = face.get(sublime.platform(), "")
    if face:
        view.settings().set("font_face", face)


def match_font(view, code_view):
    for key in FONT_KEYS:
        value = code_view.settings().get(key)
        if value is not None:
            view.settings().set(key, value)


# Headers

def make_header(window, text, code_view):
    # A gutter without line numbers, so an eye can sit on the header.
    view = make_side_view(window, text, {"word_wrap": False, "gutter": True, "line_numbers": False})
    match_font(view, code_view)
    write_header(view, text)
    view.set_read_only(True)
    return view


def write_header(view, text):
    """A header's text on line ROOM_LINES, between blank lines: room for the wheel either way
    (scroll bars are hidden, see scrollbars). The caret sits on the text, so focus never scrolls."""
    view.run_command("sight_walk_replace", {"text": "\n" * ROOM_LINES + text + "\n" * ROOM_LINES})
    view.sel().clear()
    view.sel().add(sublime.Region(view.text_point(ROOM_LINES, 0)))


def line_top(view, line):
    return view.text_to_layout(view.text_point(line - 1, 0))[1]


def header_top(view):
    return view.text_to_layout(view.text_point(ROOM_LINES, 0))[1]


def draw_edit_button(header, text, on_click):
    """The header's text, padded so the edit button sits at its right edge."""
    columns = int(header.viewport_extent()[0] / max(header.em_width(), 1))
    label = word("edit")
    padded = text.ljust(max(columns - len(label) - 4, len(text) + 1))
    if kept(header).get("edit_text") == (padded, label):
        return
    kept(header)["edit_text"] = (padded, label)
    write_header(header, padded)
    point = header.line(header.text_point(ROOM_LINES, 0)).b
    phantoms(header, "sight_walk_edit").update([
        sublime.Phantom(sublime.Region(point), button_html(label), sublime.LAYOUT_INLINE,
                        on_click)])


# Drawing on code views

def draw_icons(view, old, new):
    """Gutter icons for one sight: {line: icon name}. Only changed lines are redrawn."""
    for line, icon in old.items():
        if new.get(line) != icon:
            view.erase_regions("sight_walk_icon_%d" % line)
    for line, icon in new.items():
        if old.get(line) != icon:
            point = view.text_point(line - 1, 0)
            view.add_regions("sight_walk_icon_%d" % line, [sublime.Region(point)],
                             "sight_walk.icon", ICONS % icon, ICON_FLAGS)


def draw_strip_icons(strip, first_line, lines):
    """Second marks on the strip: {line from first_line: [icon]}, as far from the border as the
    gutter's icon is on its other side (Jakub)."""
    size = int(strip.line_height()) - 2
    html = '<body style="margin: 0; padding: 0 0 0 %dpx">%%s</body>' % STRIP_ICON_SHIFT
    phantoms(strip, "sight_walk_strip_icons").update([
        sublime.Phantom(sublime.Region(strip.text_point(first_line + line, 0)),
                        html % "".join(STRIP_IMG % (icon, size, size) for icon in icons),
                        sublime.LAYOUT_INLINE)
        for line, icons in sorted(lines.items())])


OUTLINE_KEYS = tuple(marks.ICON_COLOURS)


def draw_outlines(view, lines):
    """An outline around the text of each marked line ({line: colour key}), in its icon's colour
    (marks.ICON_COLOURS)."""
    regions = {}
    for line, colour in sorted(lines.items()):
        whole = view.line(view.text_point(line - 1, 0))
        text = view.substr(whole)
        start = whole.a + len(text) - len(text.lstrip())
        end = whole.b - (len(text) - len(text.rstrip()))
        if start < end:
            regions.setdefault(colour, []).append(sublime.Region(start, end))
    for colour in OUTLINE_KEYS:
        view.add_regions("sight_walk_outline_" + colour, regions.get(colour, []),
                         "sight_walk.outline." + colour, "", sublime.DRAW_NO_FILL)


ELLIPSIS_HTML = ('<body style="margin: 0; padding: 0"><div style="margin: 0; padding: 0 0 0 %dpx; '
                 'height: %%dpx; line-height: %%dpx; font-size: 1rem; color: %s">…</div></body>'
                 % (GAP_PX, FADED))


def draw_ellipsis(view, key, line, block, height):
    """"…" where a fragment of a function leaves code out (Jakub), key "above" or "below": on
    a blank line shown around the range (inline, no room added), or as a line of its own below
    line (block), height px tall before the room Sublime adds around it."""
    point = view.line(view.text_point(line - 1, 0)).b if block else view.text_point(line - 1, 0)
    phantoms(view, "sight_walk_ellipsis_" + key).update([sublime.Phantom(
        sublime.Region(point), ELLIPSIS_HTML % (height, height),
        sublime.LAYOUT_BLOCK if block else sublime.LAYOUT_INLINE)])


def draw_gap(view, first, last):
    """An inline phantom at the start of lines first..last (1-based): room between the gutter and
    the code, which the margin setting cannot give, as Sublime paints the margin in the gutter's
    colour (Jakub). Sublime shows phantoms in every clone of a view, so sights are copies, never
    clones (see make_copy)."""
    points = [view.text_point(line - 1, 0) for line in range(first, last + 1)]
    phantoms(view, "sight_walk_gap").update([
        sublime.Phantom(sublime.Region(p), GAP_HTML, sublime.LAYOUT_INLINE) for p in points])


def selected_text(view):
    """The text the user selected in the view, or None: what "this" means (Jakub)."""
    if not view.sel() or view.sel()[0].empty():
        return None
    return view.substr(view.sel()[0])[:2000]
