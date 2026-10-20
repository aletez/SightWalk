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

from .callmap import dot_source
from .subl_chat import MARK_HTML, SYNTAX
from .config import BLANK_LINES, SETTINGS_FILE, SETTLE_MS
from .header import MARK_ROOM
from .permissions import KEYS
from .subl_views import FADED, kept, make_side_view, phantoms
from .words import word

TABS = ("Map", "Tour", "Answers", "Permissions")
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


def show_buttons(view, panning, on_toggle):
    """The Tools header's buttons, in a narrow pane of their own at its right (Jakub): the
    wheel toggle and the help mark, what primary+s does."""
    if kept(view).get("buttons") == panning:
        return
    kept(view)["buttons"] = panning
    def clicked(href):
        if href == "pan":
            on_toggle()
        else:
            view.show_popup(PAN_HELP % (word("or"), word("or"), word("pan")), location=0)
    phantoms(view, "sight_walk_buttons").update([sublime.Phantom(
        sublime.Region(0), toggle_html(panning) + MARK_HTML, sublime.LAYOUT_INLINE, clicked)])


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
