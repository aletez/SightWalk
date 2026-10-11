"""Shows in a trip the questions the code already asks (see questions): a stored object used in a
sight without a question the code asks about it elsewhere gets a faint dotted underline, and
hovering it shows where the code asks. Only for Python files."""

import os

import sublime

from . import questions
from .spec import repo_root

SKIP = ("__pycache__", "venv", ".venv", "node_modules")
MAX_FILES = 500
FLAGS = sublime.DRAW_NO_FILL | sublime.DRAW_NO_OUTLINE | sublime.DRAW_STIPPLED_UNDERLINE
SHOWN = {}  # view id: (view, [(region, html)])
ON = [True]  # the underlines are shown; the "References without sentinel" button toggles it


def sources(root):
    """{path: text} of the Python files under root, skipping hidden and tool folders."""
    found = {}
    for folder, dirs, files in os.walk(root):
        dirs[:] = [d for d in dirs if not d.startswith(".") and d not in SKIP]
        for name in files:
            if name.endswith(".py") and len(found) < MAX_FILES:
                path = os.path.join(folder, name)
                with open(path, encoding="utf-8", errors="replace") as f:
                    found[path] = f.read()
    return found


def draw(sights):
    """Underlines, in every Python sight, the uses the code's own questions point at."""
    known_by_root = {}
    for sight in sights:
        if not sight.path.endswith(".py"):
            continue
        root = repo_root(sight.path) or os.path.dirname(sight.path)
        if root not in known_by_root:
            known_by_root[root] = questions.catalogue(sources(root))
        text = sight.view.substr(sublime.Region(0, sight.view.size()))
        found = questions.unasked(text, sight.begin, sight.end, known_by_root[root])
        for view in sight.code_views()[:2]:  # not a twin: it holds only line 1
            mark(view, found, known_by_root[root])


def mark(view, found, known):
    shown = []
    for line, start, end, missing in found:
        text = view.substr(view.line(view.text_point(line - 1, 0)))
        raw = text.encode("utf-8")  # the parser counts columns in bytes
        a = len(raw[:start].decode("utf-8", "replace"))
        b = len(raw[:end].decode("utf-8", "replace"))
        region = sublime.Region(view.text_point(line - 1, a), view.text_point(line - 1, b))
        shown.append((region, popup_html(missing, known)))
    SHOWN[view.id()] = (view, shown)
    paint(view, shown)


def paint(view, shown):
    regions = [r for r, _ in shown] if ON[0] else []
    view.add_regions("sight_walk_asked", regions, "sight_walk.outline", "", FLAGS)


def toggle():
    """The "References without sentinel" button: underlines on or off in every trip (Jakub)."""
    ON[0] = not ON[0]
    for view, shown in list(SHOWN.values()):
        if view.is_valid():
            paint(view, shown)


def popup_html(missing, known):
    """Where the code asks each question it does not ask here, three places at most."""
    rows = []
    for question in missing:
        for path, line, function, text in known[question][:3]:
            rows.append("<code>%s</code><br><small>%s:%d, %s</small>" % (
                escape(text), escape(os.path.basename(path)), line, escape(function)))
    return ("<div><b>The code asks this elsewhere:</b><br>%s</div>" % "<br>".join(rows))


def escape(text):
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def show_popup(view, point):
    """On hovering an underlined use."""
    for region, html in SHOWN.get(view.id(), (view, []))[1] if ON[0] else []:
        if region.contains(point):
            view.show_popup(html, sublime.HIDE_ON_MOUSE_MOVE_AWAY, point, max_width=700)
            return
