import colorsys
import json
import os
import random

import sublime

from .config import HEADER_TINT, SETTINGS_FILE, SETTLE_MS, TINT

HUE_START = random.random()
HUES = {}
SCHEMES = {}


def hue_for(path):
    if path not in HUES:
        # Golden-ratio steps keep successive hues far apart on the colour wheel.
        HUES[path] = (HUE_START + len(HUES) * 0.618034) % 1.0
    return HUES[path]


def tint_color(background, hue, amount):
    bg = background[1:7]
    rgb = [int(bg[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    pure = colorsys.hls_to_rgb(hue, 0.5, 1.0)
    mixed = [c * (1 - amount) + p * amount for c, p in zip(rgb, pure)]
    return "#%02x%02x%02x" % tuple(int(round(c * 255)) for c in mixed)


def load_base_scheme(base):
    if not base.endswith(".sublime-color-scheme"):
        return None
    found = sublime.find_resources(os.path.basename(base))
    if not found:
        return None
    try:
        return sublime.decode_value(sublime.load_resource(found[0]))
    except Exception:
        return None


def write_scheme(scheme, name):
    folder = os.path.join(sublime.packages_path(), "User", "SightWalk")
    os.makedirs(folder, exist_ok=True)
    with open(os.path.join(folder, name), "w", encoding="utf-8") as f:
        json.dump(scheme, f)
    return "Packages/User/SightWalk/" + name


def tint_amounts():
    # Read on every show, so a new value in the settings applies to the next reader at once.
    settings = sublime.load_settings(SETTINGS_FILE)
    return settings.get("tint", TINT), settings.get("header_tint", HEADER_TINT)


def tinted_schemes(view, hue, amounts):
    """Writes a faint tint for the code and a stronger one for the header, both in the file's hue."""
    base = view.settings().get("color_scheme") or ""
    scheme = load_base_scheme(base)
    if scheme is None:
        return None
    background = view.style().get("background", "#000000")
    stem = "%s-hue%03d" % (os.path.splitext(os.path.basename(base))[0], int(round(hue * 1000)))
    # The gutter, where the icons sit, has the header's band colour.
    scheme.setdefault("globals", {})["gutter"] = tint_color(background, hue, amounts[1])
    scheme.setdefault("rules", []).append({"scope": "sight_walk.icon", "foreground": "#ffffff"})
    stem += "-g%03d" % int(round(amounts[1] * 1000))
    resources = []
    for amount, part in zip(amounts, ("", "-header")):
        scheme["globals"]["background"] = tint_color(background, hue, amount)
        if part:
            # The header's caret line paints its gutter in the line highlight; make that the band.
            scheme["globals"]["line_highlight"] = scheme["globals"]["background"]
        # The amount is in the name, so a changed setting gives a new file instead of a stale one.
        name = "%s%s-%03d.sublime-color-scheme" % (stem, part, int(round(amount * 1000)))
        resources.append(write_scheme(scheme, name))
    return resources


def when_indexed(resources, callback, tries=200):
    # Sublime finds a freshly written file only after it indexes it, and setting a scheme it
    # can't find yet opens an error dialog. So poll the index instead of guessing a delay.
    # Up to 10 s: right after a plugin reload, indexing can take several seconds.
    if all(sublime.find_resources(os.path.basename(r)) for r in resources):
        callback()
    elif tries:
        sublime.set_timeout(lambda: when_indexed(resources, callback, tries - 1), SETTLE_MS)
    else:
        print("SightWalk: colour schemes not indexed in time, panes stay untinted:", resources)


def apply_tint(code_views, headers, path):
    # Written once per file and setting, so a file keeps its colours across show calls.
    amounts = tint_amounts()
    key = (path, amounts)
    if key not in SCHEMES:
        SCHEMES[key] = tinted_schemes(code_views[0], hue_for(path), amounts)
    if SCHEMES[key] is None:
        return
    code, header = SCHEMES[key]

    def set_schemes():
        for views, resource in ((code_views, code), (headers, header)):
            for v in views:
                if v.is_valid():
                    v.settings().set("color_scheme", resource)

    when_indexed([code, header], set_schemes)
