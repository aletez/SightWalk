import colorsys
import json
import os
import random

import sublime

from .config import OUTLINE_TINT, SETTINGS_FILE, SETTLE_MS, TINT

HUE_START = random.random()
HUES = {}
SCHEMES = {}


def hue_for(path):
    if path not in HUES:
        # Golden-ratio steps keep successive hues far apart on the colour wheel.
        HUES[path] = (HUE_START + len(HUES) * 0.618034) % 1.0
    return HUES[path]


def hex_rgb(colour):
    return [int(colour[i:i + 2], 16) / 255 for i in (1, 3, 5)]


def tint_color(background, hue, amount, target="#808080"):
    """Mixes the background with the fully saturated hue, or with target for hue None."""
    rgb = hex_rgb(background)
    pure = hex_rgb(target) if hue is None else colorsys.hls_to_rgb(hue, 0.5, 1.0)
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


def band_amount():
    # Read on every show, so a new value in the settings applies to the next reader at once.
    return sublime.load_settings(SETTINGS_FILE).get("tint", TINT)


def tinted_schemes(view, hue, amount):
    """Writes two schemes in the file's hue: the code keeps its background and gets the band in
    the gutter and a strong outline colour; the header is the band."""
    base = view.settings().get("color_scheme") or ""
    scheme = load_base_scheme(base)
    if scheme is None:
        return None
    background = view.style().get("background", "#000000")
    # Without a hue, the band is the scheme's text colour mixed in, which always contrasts.
    band = tint_color(background, hue, amount, view.style().get("foreground", "#808080"))
    # Hue and amount are in the name, so a changed setting gives a new file, not a stale one.
    stem = "%s-%s-%03d" % (os.path.splitext(os.path.basename(base))[0],
                           "text" if hue is None else "hue%03d" % int(round(hue * 1000)),
                           int(round(amount * 1000)))
    globals_ = scheme.setdefault("globals", {})
    globals_["gutter"] = band
    scheme.setdefault("rules", []).extend([
        {"scope": "sight_walk.icon", "foreground": "#ffffff"},
        {"scope": "sight_walk.outline", "foreground": tint_color(background, hue, OUTLINE_TINT)}])
    code = write_scheme(scheme, stem + "-code.sublime-color-scheme")
    # The header's caret line paints its gutter in the line highlight; make that the band too.
    globals_["background"] = globals_["line_highlight"] = band
    return [code, write_scheme(scheme, stem + "-header.sublime-color-scheme")]


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
    amount = band_amount()
    key = (path, amount)
    if key not in SCHEMES:
        SCHEMES[key] = tinted_schemes(code_views[0], hue_for(path), amount)
    if SCHEMES[key] is None:
        return
    code, header = SCHEMES[key]

    def set_schemes():
        for views, resource in ((code_views, code), (headers, header)):
            for v in views:
                if v.is_valid():
                    v.settings().set("color_scheme", resource)

    when_indexed([code, header], set_schemes)


def apply_grey(header):
    """The conversation's header: a band like the others, in the text colour, which darkens light
    schemes and lightens dark ones."""
    amount = band_amount()
    key = (None, amount)
    if key not in SCHEMES:
        SCHEMES[key] = tinted_schemes(header, None, amount)
    if SCHEMES[key] is None:
        return
    resource = SCHEMES[key][1]

    def set_scheme():
        if header.is_valid():
            header.settings().set("color_scheme", resource)

    when_indexed([resource], set_scheme)
