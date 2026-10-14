"""The Tools pane (Jakub's name for now) under the Vetting Bench, with tabs in its header: Map, the
trip's sights as a call graph drawn by Graphviz; Tour, an informator's trips in one order; and
Scroll, a blank pane in the bench's colours whose wheel moves the whole trip, like the Sights'
fillers (the scroll pad)."""

import hashlib
import json
import os
import shutil
import struct
import subprocess

import sublime

from .callmap import dot_source
from .chat import MARK_HTML, SYNTAX
from .config import BLANK_LINES, SETTINGS_FILE
from .views import FADED, kept, make_blank_view, make_side_view, match_font, phantoms
from .words import word

TABS = ("Map", "Tour", "Scroll")
SCROLL = "Scroll"
WALKED = os.path.join(os.path.expanduser("~"), ".sight_walk", "walked.json")
# Where Graphviz is usually installed; Sublime does not see the shell's PATH.
PLACES = ["/opt/homebrew/bin", "/usr/local/bin", "/usr/bin"]
MAPS = os.path.join(os.path.expanduser("~"), ".sight_walk", "maps")


def make(window, conversation):
    view = make_blank_view(window, SCROLL)
    match_font(view, conversation)
    view.assign_syntax(SYNTAX)  # the bench's colours down the whole column (Jakub)
    return view


def make_tool(window, name):
    """A tool's pane (Map, Tour): read-only, in the bench's colours, drawn with phantoms."""
    view = make_side_view(window, name, {"word_wrap": False, "sight_walk_blank": True})
    view.assign_syntax(SYNTAX)
    view.run_command("sight_walk_replace", {"text": " "})
    view.set_read_only(True)
    return view


def set_panning(view, on):
    """A tool's pane taking the wheel for the panorama (Jakub): blank lines either way of its
    content, like the scroll pad, so the wheel moves it both ways; off, its content alone."""
    view.set_read_only(False)
    view.run_command("sight_walk_replace", {"text": "\n" * (2 * BLANK_LINES) if on else " "})
    view.set_read_only(True)
    if not on:
        view.set_viewport_position((0.0, 0.0), False)


def content_point(view):
    """Where a tool's content is drawn: at the anchor line while it takes the wheel, else at 0."""
    return view.text_point(BLANK_LINES, 0) if view.rowcol(view.size())[0] > BLANK_LINES else 0

PAN_KEY = "ctrl+s"
TABS_ROOM = 14  # in the header's columns, wider than the tabs' font
PAN_HELP = "<div><b>%s</b> %%s</div>" % PAN_KEY


def show_tabs(header, active, on_select, panning):
    """The tabs as links in the Tools pane's header, the shown one in bold, and at the right the
    help mark, as on the bench's header: what ctrl+s does (Jakub)."""
    columns = int(header.viewport_extent()[0] / max(header.em_width(), 1))
    if kept(header).get("tabs") == (active, panning, columns, word("Map")):
        return
    kept(header)["tabs"] = (active, panning, columns, word("Map"))
    # The tabs, an inline phantom at the start, take about TABS_ROOM columns of the line.
    header.run_command("sight_walk_replace", {"text": " " * max(columns - 6 - TABS_ROOM, 1)})
    state = word("pan_on" if panning else "pan_off")
    point = header.line(0).b
    phantoms(header, "sight_walk_pan_help").update([sublime.Phantom(
        sublime.Region(point), MARK_HTML, sublime.LAYOUT_INLINE,
        lambda _: header.show_popup(PAN_HELP % (word("pan") % state), location=point))])
    links = ["<b>%s</b>" % word(t) if t == active else
             '<a href="%s" style="text-decoration: none">%s</a>' % (t, word(t)) for t in TABS]
    html = '&nbsp;&nbsp;<span style="color: %s">|</span>&nbsp;&nbsp;' % FADED
    html = html.join(links)
    phantoms(header, "sight_walk_tabs").update(
        [sublime.Phantom(sublime.Region(0), html, sublime.LAYOUT_INLINE, on_select)])


# The map

def find_dot():
    named = sublime.load_settings(SETTINGS_FILE).get("dot_path")
    if named:
        return os.path.expanduser(named)
    return shutil.which("dot", path=os.pathsep.join(PLACES + [os.environ.get("PATH", "")]))


def draw_map(view, nodes, arrows, style):
    """Draws the map off the main thread (a subprocess would block the bridge), then shows it."""
    dot = find_dot()
    if dot is None:
        show_note(view, word("no_dot"))
        return
    source = dot_source(nodes, arrows, style)
    sublime.set_timeout_async(lambda: render(view, dot, source), 0)


def render(view, dot, source):
    os.makedirs(MAPS, exist_ok=True)
    path = os.path.join(MAPS, hashlib.sha1(source.encode("utf-8")).hexdigest()[:16] + ".png")
    with open(path[:-4] + ".dot", "w", encoding="utf-8") as f:  # to read what was drawn
        f.write(source)
    if not os.path.exists(path):
        done = subprocess.run([dot, "-Tpng", "-Gdpi=144", "-o", path], input=source.encode(),
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=20)
        if done.returncode:
            msg = done.stderr.decode("utf-8", "replace")[:300]
            sublime.set_timeout(lambda: show_note(view, word("dot_failed") + msg), 0)
            return
    sublime.set_timeout(lambda: show_image(view, path), 0)


def png_size(path):
    with open(path, "rb") as f:
        return struct.unpack(">II", f.read(24)[16:24])


def show_image(view, path):
    """The map as wide as the pane at most, at half its pixels (it is drawn at 144 dpi)."""
    if not view.is_valid():
        return
    width, height = png_size(path)
    scale = min(0.5, max(view.viewport_extent()[0] - 16, 50) / width)
    html = '<img src="file://%s" width="%d" height="%d">' % (path, width * scale, height * scale)
    phantoms(view, "sight_walk_map").update(
        [sublime.Phantom(sublime.Region(content_point(view)), html, sublime.LAYOUT_BLOCK)])


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
        kind = ' <span style="color: %s">%s</span>' % (FADED, word(trip.kind)) if trip.kind != "run" \
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
