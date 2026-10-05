import sublime

from .config import COLS, OVERLAP, SETTLE_MS

SIDE_SETTINGS = (("gutter", False), ("line_numbers", False), ("draw_indent_guides", False),
                 ("highlight_line", False), ("scroll_past_end", True), ("sight_walk", True))
CODE_SETTINGS = (("word_wrap", False), ("scroll_past_end", True), ("sight_walk", True))
# Everything that decides how tall a line is. Copied from the code view, so that view settings
# override syntax-specific ones (Plain Text may have its own font) and every line has one height.
ICONS = "Packages/SightWalk/icons/%s.png"
ICON_FLAGS = sublime.DRAW_NO_FILL | sublime.DRAW_NO_OUTLINE
FONT_KEYS = ("font_face", "font_size", "font_options", "line_padding_top", "line_padding_bottom")


def hide_chrome(window):
    window.set_tabs_visible(False)
    window.set_sidebar_visible(False)
    window.set_minimap_visible(False)


def wait_until_loaded(views, callback):
    if any(v.is_loading() for v in views):
        sublime.set_timeout(lambda: wait_until_loaded(views, callback), SETTLE_MS)
    else:
        callback()


def reader_layout(heights, total, overlaps=(), top=0):
    """overlaps[i]: cell i reaches OVERLAP px into the next cell, which hides the border between.
    top: height of the conversation's header; 0 leaves it out."""
    edges, y = [0.0], 0.0
    for h in heights:
        y += h
        edges.append(y)
    bottoms = [edges[i + 1] + OVERLAP if i < len(overlaps) and overlaps[i] and i + 1 < len(heights)
               else edges[i + 1] for i in range(len(heights))]
    rows = sorted(set(edges + bottoms + ([top] if top else [])))
    row = {value: index for index, value in enumerate(rows)}
    # Groups: the code cells first, then the strip, the conversation and its header.
    cells = [[1, row[edges[i]], 2, row[bottoms[i]]] for i in range(len(heights))]
    n = len(rows) - 1
    cells += [[2, 0, 3, n], [0, row[top] if top else 0, 1, n]]
    if top:
        cells.append([0, 0, 1, row[top]])
    return {"cols": COLS, "rows": [r / total for r in rows], "cells": cells}


def make_side_view(window, name, extra):
    view = window.new_file()
    view.set_scratch(True)
    view.set_name(name)
    settings = view.settings()
    for key, value in SIDE_SETTINGS + tuple(extra.items()):
        settings.set(key, value)
    return view


def match_font(view, code_view):
    for key in FONT_KEYS:
        value = code_view.settings().get(key)
        if value is not None:
            view.settings().set(key, value)


def make_header(window, text, code_view):
    # A gutter without line numbers, so an eye can sit on the header.
    view = make_side_view(window, text, {"word_wrap": False, "gutter": True, "line_numbers": False})
    match_font(view, code_view)
    view.run_command("sight_walk_replace", {"text": text})
    view.set_read_only(True)
    return view


def draw_icons(view, old, new):
    """Gutter icons for one pane: {line: icon name}. Only changed lines are redrawn."""
    for line, icon in old.items():
        if new.get(line) != icon:
            view.erase_regions("sight_walk_icon_%d" % line)
    for line, icon in new.items():
        if old.get(line) != icon:
            point = view.text_point(line - 1, 0)
            view.add_regions("sight_walk_icon_%d" % line, [sublime.Region(point)],
                             "sight_walk.icon", ICONS % icon, ICON_FLAGS)


def draw_outlines(view, lines):
    """An outline around the text of each marked line, in the file's strong hue."""
    regions = []
    for line in sorted(lines):
        whole = view.line(view.text_point(line - 1, 0))
        text = view.substr(whole)
        start = whole.a + len(text) - len(text.lstrip())
        end = whole.b - (len(text) - len(text.rstrip()))
        if start < end:
            regions.append(sublime.Region(start, end))
    view.add_regions("sight_walk_outline", regions, "sight_walk.outline", "", sublime.DRAW_NO_FILL)


def prepare_code_view(window, view, clone):
    if clone:
        window.focus_view(view)
        window.run_command("clone_file")
        view = window.active_view()
    for key, value in CODE_SETTINGS:
        view.settings().set(key, value)
    return view
