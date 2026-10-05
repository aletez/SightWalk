import sublime

from .config import COLS, HEADER_PAD, INSET, OVERLAP, SETTLE_MS

SIDE_SETTINGS = (("gutter", False), ("line_numbers", False), ("draw_indent_guides", False),
                 ("highlight_line", False), ("scroll_past_end", True), ("sight_walk", True))
CODE_SETTINGS = (("word_wrap", False), ("scroll_past_end", True), ("sight_walk", True),
                 ("sight_walk_code", True))  # a twin overrides the last two
# Everything that decides how tall a line is. Copied from the code view, so that view settings
# override syntax-specific ones (Plain Text may have its own font) and every line has one height.
ICONS = "Packages/SightWalk/icons/%s.png"
ICON_FLAGS = sublime.DRAW_NO_FILL | sublime.DRAW_NO_OUTLINE
FADED = "color(var(--foreground) alpha(0.45))"
# Faded and outlined at all times, so it reads as a control, not as text.
BUTTON = "Edit (Enter)"
BUTTON_HTML = ('<a href="edit" style="color: %s; text-decoration: none; border: 1px solid %s; '
               'border-radius: 3px; padding: 0 4px">%s</a>' % (FADED, FADED, BUTTON))
BUTTONS = {}
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


def to_layout(rects, total):
    """rects: (x0, y0, x1, y1), x as a share of the width and y in px, in group order."""
    xs = sorted(set(x for r in rects for x in (r[0], r[2])))
    ys = sorted(set(y for r in rects for y in (r[1], r[3])))
    col = {x: i for i, x in enumerate(xs)}
    row = {y: i for i, y in enumerate(ys)}
    cells = [[col[r[0]], row[r[1]], col[r[2]], row[r[3]]] for r in rects]
    return {"cols": xs, "rows": [y / total for y in ys], "cells": cells}


def reader_layout(heights, total, overlaps=(), top=0, split=0, cols=COLS, editor=None, twins=()):
    """Groups in order: the editor's header and view if open (first, because Sublime draws earlier
    groups over later ones), the code cells, then the conversation and, once top is known, its
    header and the vetting pane.
    overlaps[i]: cell i reaches OVERLAP px into the next, which hides the border between.
    top: the conversation header's height, split: the conversation's bottom.
    editor: (header height, left offset as a share of the width, top offset in px), laid over
    the lower right of the code column.
    twins[i]: (visible width of cell i's left strip, its real width) as shares. The twin takes
    the rest and is drawn over the strip's hidden part, which hides its scroll bar (see twin.py)."""
    rects, y = [], 0.0
    for i, h in enumerate(heights):
        reach = OVERLAP if i < len(overlaps) and overlaps[i] and i + 1 < len(heights) else 0
        dx = twins[i] if i < len(twins) else 0
        if dx:
            visible, wide = dx
            # The twin comes first: earlier groups are drawn over later ones.
            rects.append((cols[1] + visible, y, cols[2], y + h + reach))
            rects.append((cols[1], y, cols[1] + wide, y + h + reach))
        else:
            rects.append((cols[1], y, cols[2], y + h + reach))
        y += h
    if not top:
        return to_layout(rects + [(cols[0], 0.0, cols[1], total)], total)
    # The vetting pane spans both columns; the code cells, drawn over it, leave it an L.
    rects += [(cols[0], top, cols[1], split), (cols[0], 0.0, cols[1], top + OVERLAP),
              (cols[0], split, cols[2], total)]
    if editor:
        header, dx, dy = editor
        left, right = cols[1] + dx, cols[2]
        rects = [(left, dy, right, dy + header + OVERLAP), (left, dy + header, right, total)] + rects
    return to_layout(rects, total)


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


def write_header(view, text):
    """A header's text on line HEADER_PAD, between blank lines: room for a long touchpad swipe
    either way. The caret sits on the text, so focusing never scrolls. Works with overlay
    scroll bars only (see scrollbars), else the bars cover the header's one visible line."""
    view.run_command("sight_walk_replace", {"text": "\n" * HEADER_PAD + text + "\n" * HEADER_PAD})
    view.sel().clear()
    view.sel().add(sublime.Region(view.text_point(HEADER_PAD, 0)))


def header_top(view):
    return view.text_to_layout(view.text_point(HEADER_PAD, 0))[1]


def make_header(window, text, code_view):
    # A gutter without line numbers, so an eye can sit on the header.
    view = make_side_view(window, text, {"word_wrap": False, "gutter": True, "line_numbers": False})
    match_font(view, code_view)
    write_header(view, text)
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
    view.set_read_only(True)  # editing happens in the editor
    return view


def keep_caret_visible(view, top, height):
    """Puts the caret on the first line of [top, top + height) in layout coordinates unless it is
    there already, so focusing the view never scrolls it."""
    caret = view.sel()[0].b if view.sel() else 0
    y = view.text_to_layout(caret)[1]
    if not top <= y < top + height:
        view.sel().clear()
        view.sel().add(sublime.Region(view.layout_to_text((0.0, top + 0.5))))


def draw_edit_button(header, text, on_click):
    """The header's text, padded so the edit button sits at its right edge."""
    columns = int(header.viewport_extent()[0] / max(header.em_width(), 1))
    padded = text.ljust(max(columns - len(BUTTON) - 4, len(text) + 1))
    button = BUTTONS.setdefault(header.id(), [sublime.PhantomSet(header, "sight_walk_edit"), None])
    if button[1] == padded:
        return
    button[1] = padded
    write_header(header, padded)
    point = header.line(header.text_point(HEADER_PAD, 0)).b
    button[0].update([sublime.Phantom(sublime.Region(point), BUTTON_HTML, sublime.LAYOUT_INLINE,
                                      on_click)])
