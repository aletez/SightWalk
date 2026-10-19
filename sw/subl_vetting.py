"""The Tools pane (Jakub's name for now) under the Vetting Bench, with tabs in its header: Map, the
trip's sights as a call graph drawn by Graphviz, and Tour, an informator's trips in one order."""

import hashlib
import json
import os
import shutil
import struct
import subprocess

import sublime

from .callmap import dot_source
from .subl_chat import MARK_HTML, SYNTAX
from .config import BLANK_LINES, SETTINGS_FILE, SETTLE_MS
from .header import MARK_ROOM
from .subl_views import FADED, kept, make_side_view, phantoms
from .words import word

TABS = ("Map", "Tour")
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
TABS_ROOM = 14  # in the header's columns, wider than the tabs' font
PAN_HELP = "<div><b>%s</b> %%s</div>" % PAN_KEY


TOGGLE_ROOM = 3  # columns the wheel toggle takes before the help mark


def toggle_html(panning):
    """[⇕]: the wheel moves the whole trip; [↕]: it scrolls the tool or the bench itself (Jakub),
    drawn as the help mark is."""
    return MARK_HTML.replace('href="help"', 'href="pan"').replace(">?<", ">%s<" % (
        "⇕" if panning else "↕")) + "&nbsp;"


def show_tabs(header, active, on_select, panning, on_toggle=None):
    """The tabs as links in the Tools pane's header, the shown one in bold, and at the right the
    wheel toggle and the help mark, as on the bench's header: what primary+s does (Jakub)."""
    columns = int(header.viewport_extent()[0] / max(header.em_width(), 1))
    if kept(header).get("tabs") == (active, panning, columns, word("Map")):
        align_mark(header)  # cheap when in place; laid out late, it may need it now
        return
    kept(header)["tabs"] = (active, panning, columns, word("Map"))
    # The tabs, an inline phantom at the start, take about TABS_ROOM columns of the line.
    extra = kept(header).get("extra", 0)  # learned by align_mark
    header.run_command("sight_walk_replace",
                       {"text": " " * max(columns - 6 - TABS_ROOM + extra, 1)})
    state = word("pan_on" if panning else "pan_off")
    point = header.line(0).b
    def clicked(href):
        if href == "pan" and on_toggle is not None:
            on_toggle()
        else:
            header.show_popup(PAN_HELP % (word("pan") % state), location=point)

    phantoms(header, "sight_walk_pan_help").update([sublime.Phantom(
        sublime.Region(point), toggle_html(panning) + MARK_HTML, sublime.LAYOUT_INLINE, clicked)])
    links = ["<b>%s</b>" % word(t) if t == active else
             '<a href="%s" style="text-decoration: none">%s</a>' % (t, word(t)) for t in TABS]
    html = '&nbsp;&nbsp;<span style="color: %s">|</span>&nbsp;&nbsp;' % FADED
    html = html.join(links)
    phantoms(header, "sight_walk_tabs").update(
        [sublime.Phantom(sublime.Region(0), html, sublime.LAYOUT_INLINE, on_select)])
    sublime.set_timeout(lambda: align_mark(header), SETTLE_MS)


def align_mark(header):
    """The help mark to the right edge, where the bench's stands (MARK_ROOM columns from it;
    Jakub: it stood mid-way): the tabs' phantom is wider or narrower than guessed in the
    header's font, so the spaces before the mark are measured again once drawn."""
    if not header.is_valid():
        return
    em = max(header.em_width(), 1)
    end = header.line(0).b
    width = header.viewport_extent()[0]
    if width <= 0 or end < 2:  # not laid out yet
        return
    # A space of the header's font, proportional, is no em wide: measured between two of them.
    space = max(header.text_to_layout(end)[0] - header.text_to_layout(end - 1)[0], 1)
    more = int((width - header.text_to_layout(end)[0] - (MARK_ROOM + TOGGLE_ROOM) * em) / space)
    if more:  # drawn again with that many more spaces before the mark (see show_tabs)
        kept(header)["extra"] = kept(header).get("extra", 0) + more
        kept(header)["tabs"] = None


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
    (Jakub: never ticked by itself); the shown one in bold."""
    if tour is None:
        return show_note(view, word("no_tour"), "sight_walk_tour")
    rows = []
    for number, trip in enumerate(tour, 1):
        box = "☑" if trip.id in walked else "☐"
        name = "<b>%s</b>" % trip.name if trip.id == current else trip.name
        kind = ' <span style="color: %s">(%s)</span>' % (FADED, word(trip.kind)) if trip.kind != "run" \
            else ""
        rows.append('<a href="tick:%s" style="text-decoration: none">%s</a> %d. '
                    '<a href="open:%s" style="text-decoration: none">%s</a>%s'
                    % (trip.id, box, number, trip.id, name, kind))
    html = "<div>%s</div><br>%s" % (tour.name, "<br>".join(rows))
    phantoms(view, "sight_walk_tour").update([sublime.Phantom(
        sublime.Region(content_point(view)), html, sublime.LAYOUT_BLOCK, on_select)])


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
