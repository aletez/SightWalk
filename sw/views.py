import sublime

from .config import COLS, SETTLE_MS

SIDE_SETTINGS = (("gutter", False), ("line_numbers", False), ("draw_indent_guides", False),
                 ("highlight_line", False), ("scroll_past_end", True), ("sight_walk", True))
CODE_SETTINGS = (("word_wrap", False), ("scroll_past_end", True), ("sight_walk", True))
# Everything that decides how tall a line is. Copied from the code view, so that view settings
# override syntax-specific ones (Plain Text may have its own font) and every line has one height.
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


def reader_layout(heights, total):
    rows, y = [0.0], 0.0
    for h in heights[:-1]:
        y += h
        rows.append(y / total)
    rows.append(1.0)
    n = len(heights)
    cells = [[0, i, 1, i + 1] for i in range(n)]
    cells += [[1, 0, 2, n], [2, 0, 3, n]]
    return {"cols": COLS, "rows": rows, "cells": cells}


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
    view = make_side_view(window, text, {"word_wrap": False})
    match_font(view, code_view)
    view.run_command("sight_walk_replace", {"text": text})
    view.set_read_only(True)
    return view


def outline_range(view, begin, end):
    # The colour comes from the file's tinted scheme, which defines the sight_walk.range scope.
    last_line = view.line(view.text_point(end - 1, 0))
    region = sublime.Region(view.text_point(begin - 1, 0), last_line.end())
    view.add_regions("sight_walk_range", [region], "sight_walk.range", "", sublime.DRAW_NO_FILL)


def prepare_code_view(window, view, clone):
    if clone:
        window.focus_view(view)
        window.run_command("clone_file")
        view = window.active_view()
    for key, value in CODE_SETTINGS:
        view.settings().set(key, value)
    return view
