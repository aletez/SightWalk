"""The Tools pane (Jakub's name for now) under the Vetting Bench, with tabs in its header: Map, the
trip's sights as a call graph drawn by Graphviz, and Tour, an informator's trips in one order."""

import hashlib
import json
import os
import shutil
import struct
import subprocess
import textwrap

import sublime

from . import pngcut, tourmap
from .callmap import dot_source
from .subl_chat import MARK_HTML, SYNTAX
from .config import BLANK_LINES, SETTINGS_FILE, SETTLE_MS
from .header import MARK_ROOM
from .permissions import KEYS
from .subl_views import FADED, kept, make_side_view, phantoms
from .words import word

TABS = ("Map", "Tour", "Answers", "Adventures", "Permissions")
WALKED = os.path.join(os.path.expanduser("~"), ".sight_walk", "walked.json")
# Where Graphviz is usually installed; Sublime does not see the shell's PATH.
PLACES = ["/opt/homebrew/bin", "/usr/local/bin", "/usr/bin"]
MAPS = os.path.join(os.path.expanduser("~"), ".sight_walk", "maps")


def make_tool(window, name):
    """A tool's pane (Map, Tour): read-only, in the bench's colours, drawn with phantoms."""
    view = make_side_view(window, name, {"word_wrap": False, "sight_walk_blank": True,
                                         "sight_walk_tool": name})
    view.assign_syntax(SYNTAX)
    view.run_command("sight_walk_replace", {"text": " "})
    view.set_read_only(True)
    return view


def set_panning(view, on, offset=0.0):
    """A tool's pane taking the wheel for the panorama (Jakub): blank lines either way of its
    content, like the fillers, so the wheel moves it both ways; off, its content alone, scrolled
    offset px down, as far as it was while it took the wheel."""
    view.set_read_only(False)
    view.run_command("sight_walk_replace", {"text": "\n" * (2 * BLANK_LINES) if on else " "})
    view.set_read_only(True)
    if not on:
        view.set_viewport_position((0.0, offset), False)


def content_point(view):
    """Where a tool's content is drawn: at the anchor line while it takes the wheel, else at 0."""
    return view.text_point(BLANK_LINES, 0) if view.rowcol(view.size())[0] > BLANK_LINES else 0

PAN_KEY = "⌘S" if sublime.platform() == "osx" else "Ctrl+S"
PAN_HELP = "<div><b>⇕</b> %%s <b>↕</b> %%s <b>%s</b>: %%s</div>" % PAN_KEY
TAB_GAP = "   "  # between the tabs, plain text (Jakub, 2026-10-20: no phantom, which kept its
# links in place while the header scrolled sideways)
# Highlighted like tags in Foggy Morning or Chameleon (Jakub): the others orange and faint, the
# active one yellow and strong. Their colours are rules of the headers' scheme (see subl_tint).
TAB_SCOPE, ACTIVE_SCOPE = "sight_walk.tab", "sight_walk.tab.active"


def toggle_html(panning):
    """[⇕]: the wheel moves the column of sights, the bench and the tool staying put; [↕]: it
    scrolls the tool or the bench itself (Jakub), drawn as the help mark is."""
    return MARK_HTML.replace('href="help"', 'href="pan"').replace(">?<", ">%s<" % (
        "⇕" if panning else "↕")) + "&nbsp;"


def show_tabs(header, active):
    """The tabs as words of the Tools pane's header, the shown one highlighted; a click on one
    shows it (see tab_at)."""
    if kept(header).get("tabs") == (active, word("Map")):
        return
    kept(header)["tabs"] = (active, word("Map"))
    words = [" %s " % word(t) for t in TABS]
    header.run_command("sight_walk_replace", {"text": " " + TAB_GAP.join(words) + " "})
    spans, start = [], 1
    for tab, text in zip(TABS, words):
        spans.append((tab, sublime.Region(start, start + len(text))))
        start += len(text) + len(TAB_GAP)
    kept(header)["tab_spans"] = spans
    flags = sublime.DRAW_NO_OUTLINE
    header.add_regions("sight_walk_tabs", [r for t, r in spans if t != active], TAB_SCOPE, "", flags)
    header.add_regions("sight_walk_tab", [r for t, r in spans if t == active], ACTIVE_SCOPE, "",
                       flags)


def tab_at(header, point):
    """The tab whose word is at point, or None."""
    return next((t for t, r in kept(header).get("tab_spans", []) if r.a <= point < r.b), None)


MAX_HTML = MARK_HTML.replace('href="help"', 'href="max"').replace(">?<", ">⤢<") + "&nbsp;"


def buttons_help():
    """What the Tools header's buttons do, shown by [?] and on hovering them (Jakub)."""
    return "<div><b>⤢</b>: %s<br>%s</div>" % (word("max_help"), PAN_HELP % (
        word("or"), word("or"), word("pan")))


def show_buttons(view, panning, on_toggle, on_maximize):
    """The Tools header's buttons, in a narrow pane of their own at its right (Jakub): [⤢]
    maximises the pane (Esc makes it small again), then the wheel toggle, what primary+s does.
    Hovering them says what they do (see buttons_help)."""
    if kept(view).get("buttons") == panning:
        return
    kept(view)["buttons"] = panning
    actions = {"pan": on_toggle, "max": on_maximize}
    def clicked(href):
        if href in actions:
            actions[href]()
        else:
            view.show_popup(buttons_help(), location=0)
    phantoms(view, "sight_walk_buttons").update([sublime.Phantom(
        sublime.Region(0), MAX_HTML + toggle_html(panning), sublime.LAYOUT_INLINE,
        clicked)])


# The map

def find_dot():
    named = sublime.load_settings(SETTINGS_FILE).get("dot_path")
    if named:
        return os.path.expanduser(named)
    return shutil.which("dot", path=os.pathsep.join(PLACES + [os.environ.get("PATH", "")]))


def draw_map(view, nodes, arrows, style, lit=None):
    """Draws the map off the main thread (a subprocess would block the executor), then shows it.
    lit: a jump the user clicked (see callmap.dot_source)."""
    dot = find_dot()
    if dot is None:
        show_note(view, word("no_dot"))
        return
    source = dot_source(nodes, arrows, style, lit)
    sublime.set_timeout_async(lambda: render(view, dot, source), 0)


def render(view, dot, source):
    os.makedirs(MAPS, exist_ok=True)
    path = os.path.join(MAPS, hashlib.sha1(source.encode("utf-8")).hexdigest()[:16] + "-288.png")
    with open(path[:-4] + ".dot", "w", encoding="utf-8") as f:  # to read what was drawn
        f.write(source)
    if not os.path.exists(path):
        done = subprocess.run([dot, "-Tpng", "-Gdpi=288", "-o", path], input=source.encode(),
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=20)
        if done.returncode:
            msg = done.stderr.decode("utf-8", "replace")[:300]
            sublime.set_timeout(lambda: show_note(view, word("dot_failed") + msg), 0)
            return
    sublime.set_timeout(lambda: show_image(view, path), 0)


def png_size(path):
    with open(path, "rb") as f:
        return struct.unpack(">II", f.read(24)[16:24])


ZOOM_STEP = 1.25
ZOOM_HTML = ('<div><a href="out" style="text-decoration: none">&nbsp;−&nbsp;</a>&nbsp;&nbsp;'
             '<a href="in" style="text-decoration: none">&nbsp;+&nbsp;</a>&nbsp;&nbsp;'
             '<a href="fit" style="text-decoration: none">%s</a></div>')


def show_image(view, path=None):
    """The map, at first as wide as the pane at most, then zoomed (Jakub): − and + over it, or
    primary+minus and primary+= with the Map in focus; at most its own pixels (drawn at 288 dpi,
    shown at a quarter to fit, so it stays sharp four times larger)."""
    path = path or kept(view).get("map_path")
    if not view.is_valid() or not path:
        return
    kept(view)["map_path"] = path
    width, height = png_size(path)
    fit = min(0.25, max(view.viewport_extent()[0] - 16, 50) / width)
    scale = min(fit * view.settings().get("sight_walk_zoom", 1.0), 1.0)
    html = ZOOM_HTML % word("fit") + '<img src="file://%s" width="%d" height="%d">' % (
        path, width * scale, height * scale)
    phantoms(view, "sight_walk_map").update([sublime.Phantom(
        sublime.Region(content_point(view)), html, sublime.LAYOUT_BLOCK,
        lambda href: zoom(view, href))])


def zoom(view, how):
    """in, out or fit: the Map larger, smaller, or as wide as the pane again."""
    now = view.settings().get("sight_walk_zoom", 1.0)
    now = {"in": now * ZOOM_STEP, "out": max(now / ZOOM_STEP, 1.0)}.get(how, 1.0)
    view.settings().set("sight_walk_zoom", min(now, 8.0))
    show_image(view)


def show_note(view, html, key="sight_walk_map"):
    note = '<div style="color: %s">%s</div>' % (FADED, html)
    phantoms(view, key).update(
        [sublime.Phantom(sublime.Region(content_point(view)), note, sublime.LAYOUT_BLOCK)])


# The tour

def show_tour(view, tour, walked, current, on_select):
    """The tour's trips in order, each a link, and a box the user ticks for a trip walked
    (Jakub: never ticked by itself); the shown one in bold. Under them the tour map, once drawn
    (see draw_tour_map)."""
    if tour is None:
        return show_note(view, word("no_tour"), "sight_walk_tour")
    kept(view)["tour_rows"] = tour_rows(tour, walked, current)
    show_tour_page(view, on_select)


def show_tour_page(view, on_select):
    html = kept(view).get("tour_rows", "") + tour_map_html(view)
    phantoms(view, "sight_walk_tour").update([sublime.Phantom(
        sublime.Region(content_point(view)), html, sublime.LAYOUT_BLOCK, on_select)])


def tour_rows(tour, walked, current):
    rows = []
    for number, trip in enumerate(tour, 1):
        box = "☑" if trip.id in walked else "☐"
        name = code_words(trip.name)
        name = "<b>%s</b>" % name if trip.id == current else name
        kind = ' <span style="color: %s">(%s)</span>' % (FADED, word(trip.kind)) if trip.kind != "run" \
            else ""
        rows.append('<a href="tick:%s" style="text-decoration: none">%s</a> %d. '
                    '<a href="open:%s" style="text-decoration: none">%s</a>%s'
                    % (trip.id, box, number, trip.id, name, kind))
    return "<div>%s</div><br>%s" % (tour.name, "<br>".join(rows))


def code_words(text):
    """`say` in a title as code (Jakub: else "say: on the bench" reads as an order to the user):
    in a colour of its own, without the backticks."""
    parts = html_escape(text).split("`")
    return "".join('<span style="color: %s">%s</span>' % (CODE_COLOUR, p) if k % 2 else p
                   for k, p in enumerate(parts))


CODE_COLOUR = "color(var(--purplish) blend(var(--foreground) 70%))"


def draw_tour_map(view, source, ids, on_select):
    """The tour map under the list, drawn off the main thread like the Map, cut into tiles, each
    a link that opens the trip whose frame it lies in (minihtml has no image maps)."""
    dot = find_dot()
    if dot is None or kept(view).get("tour_source") == source:
        return
    kept(view)["tour_source"] = source
    sublime.set_timeout_async(lambda: render_tiles(view, dot, source, ids, on_select), 0)


def render_tiles(view, dot, source, ids, on_select):
    """dot's layout as JSON gives each trip's frame; the picture drawn once and cut (see
    pngcut), the tiles kept beside the maps with an index, so a tour drawn before is not cut
    again."""
    stem = os.path.join(MAPS, "tour-" + hashlib.sha1(source.encode("utf-8")).hexdigest()[:16])
    os.makedirs(MAPS, exist_ok=True)
    try:
        if not os.path.exists(stem + ".json"):
            cut_tiles(dot, source, stem, ids)
        with open(stem + ".json", encoding="utf-8") as f:
            drawn = json.load(f)
    except (OSError, ValueError, KeyError, subprocess.SubprocessError):
        return
    def show():
        kept(view)["tour_tiles"] = drawn
        show_tour_page(view, on_select)
    sublime.set_timeout(show, 0)


def cut_tiles(dot, source, stem, ids):
    layout = json.loads(run_dot(dot, source, ["-Tjson"]))
    bb = [float(x) for x in layout["bb"].split(",")]
    frames = {int(o["name"].split("_")[1]): [float(x) for x in o["bb"].split(",")]
              for o in layout.get("objects", [])
              if o.get("name", "").startswith("cluster_") and o["name"][8:].isdigit()}
    # Sharp, yet small enough to cut in pure Python in a few seconds, once per tour.
    dpi = max(min(TILES_DPI, TILES_PX * 72.0 / max(bb[2] - bb[0], bb[3] - bb[1], 1)), 36)
    run_dot(dot, source, ["-Tpng", "-Gdpi=%d" % dpi, "-o", stem + ".png"])
    width, height, colour, pixels = pngcut.read(stem + ".png")
    rows = []
    for r, (y0, y1, cells) in enumerate(tourmap.tiles(bb, frames, width, height, TILE_PX)):
        row = []
        for c, (x0, x1, trip) in enumerate(cells):
            path = "%s-%d-%d.png" % (stem, r, c)
            pngcut.write(path, x1 - x0, y1 - y0, colour, pngcut.crop(pixels, colour, x0, y0, x1, y1))
            row.append([path, None if trip is None else ids[trip]])
        rows.append(row)
    with open(stem + ".json", "w", encoding="utf-8") as f:
        json.dump({"width": width, "dpi": dpi, "rows": rows}, f)


TILES_PX = 8000  # the picture's longer side at most, in pixels
TILES_DPI = 100  # shown at 72 dpi, its text as large as the Map's
TILE_PX = 60  # a tile's side: a click finds its trip within this


def run_dot(dot, source, options):
    done = subprocess.run([dot] + options, input=source.encode(), stdout=subprocess.PIPE,
                          stderr=subprocess.PIPE, timeout=20)
    if done.returncode:
        raise ValueError(done.stderr.decode("utf-8", "replace")[:300])
    return done.stdout


def tour_map_html(view):
    """The tiles row by row, as wide as the pane at most; a tile in a trip's frame opens it."""
    drawn = kept(view).get("tour_tiles")
    if not drawn:
        return ""
    scale = min(72.0 / drawn.get("dpi", 72), max(view.viewport_extent()[0] - 16, 50)
                / max(drawn["width"], 1))
    rows = []
    for row in drawn["rows"]:
        cells = []
        for path, trip in row:
            width, height = png_size(path)
            image = '<img src="file://%s" width="%d" height="%d">' % (
                path, round(width * scale), round(height * scale))
            cells.append('<a href="open:%s">%s</a>' % (trip, image) if trip else image)
        rows.append("<div>%s</div>" % "".join(cells))
    return "<br>" + "".join(rows)


def read_walked(informator):
    """The ids of the informator's trips the user has opened, kept across sessions."""
    try:
        with open(WALKED, encoding="utf-8") as f:
            return set(json.load(f).get(informator, []))
    except (OSError, ValueError):
        return set()


def save_walked(informator, walked):
    try:
        with open(WALKED, encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, ValueError):
        data = {}
    data[informator] = sorted(walked)
    os.makedirs(os.path.dirname(WALKED), exist_ok=True)
    with open(WALKED, "w", encoding="utf-8") as f:
        json.dump(data, f)


# Adventures (Jakub, 2026-10-20)

def show_adventures(view, records, on_click):
    """The adventures this trip's conversation went on, each a link that opens it again."""
    if not records:
        return show_note(view, word("no_adventures"), "sight_walk_adventures")
    rows = ['<a href="%d" style="text-decoration: none">%s %d</a> · %s'
            % (k, word("adventure_title"), r["n"], r["trip"].name) for k, r in enumerate(records)]
    phantoms(view, "sight_walk_adventures").update([sublime.Phantom(
        sublime.Region(content_point(view)), "<br>".join(rows), sublime.LAYOUT_BLOCK,
        lambda href: on_click(int(href)))])


# The guide's permissions (Jakub, see docs/guide-permissions.md)

LINK = '<a href="%s" style="text-decoration: none">%s</a>'


def show_permissions(view, chosen, folders, ours, on_click):
    """A box per field, ticked by a click, and a [?] that explains it; under Editing, its
    folders, each with × to drop it, and + folder."""
    columns = int(view.viewport_extent()[0] / view.em_width()) - 4
    columns = columns if columns > 20 else 40  # the pane does not wrap, minihtml ignores width
    if not ours:
        return show_note(view, "<br>".join(textwrap.wrap(word("perm_not_ours"), columns)),
                         "sight_walk_permissions")
    rows = ["☑ %s %s" % (word("perm_read"), LINK % ("tip:read", "[?]"))]
    for key in KEYS:
        box = "☑" if key in chosen else "☐"
        rows.append("%s %s" % (LINK % ("tick:" + key, box + " " + word("perm_" + key)),
                               LINK % ("tip:" + key, "[?]")))
        if key == "edit":
            rows += ["&nbsp;&nbsp;&nbsp;&nbsp;%s %s" % (LINK % ("drop:%d" % i, "×"), folder)
                     for i, folder in enumerate(folders)]
            rows.append("&nbsp;&nbsp;&nbsp;&nbsp;" + LINK % ("add", word("perm_add_folder")))
    intro = "<br>".join(textwrap.wrap(word("perm_intro"), columns))
    html = '<div style="color: %s">%s</div><br>%s' % (FADED, intro, "<br>".join(rows))
    phantoms(view, "sight_walk_permissions").update([sublime.Phantom(
        sublime.Region(content_point(view)), html, sublime.LAYOUT_BLOCK, on_click)])


def show_tip(view, key):
    view.show_popup("<div>%s</div>" % word("perm_%s_tip" % key), sublime.HIDE_ON_MOUSE_MOVE_AWAY,
                    content_point(view), 500)


# The bench's questions and answers (Jakub)

def show_answers(view, rows, shown, on_click):
    """rows: [(kind, offset, words, note)], each a link by its offset; the shown one in bold, a
    note (the answer's icons, or stale) in grey."""
    if not rows:
        return show_note(view, word("no_answers"), "sight_walk_answers")
    lines, columns = [], int(view.viewport_extent()[0] / view.em_width()) - 2
    for kind, offset, words, note in rows:
        room = max(columns - len(kind) - 3 - len(note), 10)  # the pane does not wrap
        words = words if len(words) <= room else words[:room - 1].rstrip(" …") + "…"
        text = html_escape(words)
        text = "<b>%s</b>" % text if offset == shown else text
        grey = ' <span style="color: %s">%s</span>' % (FADED, note) if note else ""
        lines.append('%s: <a href="%d" style="text-decoration: none">%s</a>%s'
                     % (kind, offset, text, grey))
    phantoms(view, "sight_walk_answers").update([sublime.Phantom(
        sublime.Region(content_point(view)), "<br>".join(lines), sublime.LAYOUT_BLOCK, on_click)])


def html_escape(text):
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
