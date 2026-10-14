"""The Tools pane (Jakub's name for now) under the Vetting Bench, with tabs in its header: Map, the
trip's sights as a call graph drawn by Graphviz, and Scroll, a blank pane in the bench's colours
whose wheel moves the whole trip, like the Sights' fillers (the scroll pad)."""

import hashlib
import os
import shutil
import struct
import subprocess

import sublime

from .callmap import dot_source
from .chat import SYNTAX
from .config import SETTINGS_FILE
from .views import FADED, kept, make_blank_view, make_side_view, match_font, phantoms

TABS = ("Map", "Scroll")
SCROLL = "Scroll"
# Where Graphviz is usually installed; Sublime does not see the shell's PATH.
PLACES = ["/opt/homebrew/bin", "/usr/local/bin", "/usr/bin"]
MAPS = os.path.join(os.path.expanduser("~"), ".sight_walk", "maps")
NO_DOT = ("The map needs Graphviz: <code>brew install graphviz</code>, or set "
          "<code>dot_path</code> in Preferences: SightWalk Settings.")


def make(window, conversation):
    view = make_blank_view(window, SCROLL)
    match_font(view, conversation)
    view.assign_syntax(SYNTAX)  # the bench's colours down the whole column (Jakub)
    return view


def make_map(window):
    view = make_side_view(window, "Map", {"word_wrap": False, "sight_walk_blank": True})
    view.assign_syntax(SYNTAX)
    view.run_command("sight_walk_replace", {"text": " "})
    view.set_read_only(True)
    return view


def show_tabs(header, active, on_select):
    """The tabs as links in the Tools pane's header, the shown one in bold."""
    if kept(header).get("tabs") == active:
        return
    kept(header)["tabs"] = active
    header.run_command("sight_walk_replace", {"text": " "})
    links = ["<b>%s</b>" % t if t == active else
             '<a href="%s" style="text-decoration: none">%s</a>' % (t, t) for t in TABS]
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
        show_note(view, NO_DOT)
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
            sublime.set_timeout(lambda: show_note(view, "Graphviz failed: " + msg), 0)
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
        [sublime.Phantom(sublime.Region(0), html, sublime.LAYOUT_BLOCK)])


def show_note(view, html):
    note = '<div style="color: %s">%s</div>' % (FADED, html)
    phantoms(view, "sight_walk_map").update(
        [sublime.Phantom(sublime.Region(0), note, sublime.LAYOUT_BLOCK)])
