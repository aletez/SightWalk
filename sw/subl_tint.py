"""Per-file hues: each file gets colour schemes of its own, written into Packages/User, with the
gutter and the header in the file's hue."""

import colorsys
import json
import os
import plistlib
import random
import re
import time

import sublime

from . import marks, state
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
    """The base scheme as a .sublime-color-scheme dict; a .tmTheme is converted (Jakub)."""
    found = sublime.find_resources(os.path.basename(base))
    if not found:
        return None
    try:
        if base.endswith(".tmTheme"):
            return from_tm_theme(plistlib.loads(sublime.load_binary_resource(found[0])))
        if base.endswith(".sublime-color-scheme"):
            return sublime.decode_value(sublime.load_resource(found[0]))
    except Exception:
        pass
    return None


TM_RULE = {"foreground": "foreground", "background": "background", "fontStyle": "font_style"}


def from_tm_theme(theme):
    """A tmTheme's plist: its first, scope-less entry holds the globals, the rest are rules."""
    entries = theme.get("settings", [])
    plain = [e for e in entries if "scope" not in e]
    # tmTheme names are camelCase (lineHighlight), the scheme's snake_case (line_highlight).
    globals_ = {re.sub("([A-Z])", r"_\1", k).lower(): v
                for e in plain for k, v in e.get("settings", {}).items()}
    rules = [dict({"name": e.get("name", ""), "scope": e["scope"]},
                  **{TM_RULE[k]: v for k, v in e.get("settings", {}).items() if k in TM_RULE})
             for e in entries if "scope" in e]
    return {"name": theme.get("name", ""), "globals": globals_, "rules": rules}


def scheme_folder():
    return os.path.join(sublime.packages_path(), "User", "SightWalk")


def write_scheme(scheme, name):
    folder = scheme_folder()
    os.makedirs(folder, exist_ok=True)
    with open(os.path.join(folder, name), "w", encoding="utf-8") as f:
        json.dump(scheme, f)
    return "Packages/User/SightWalk/" + name


def band_amount():
    # Read on every show, so a new value in the settings applies to the next reader at once.
    return sublime.load_settings(SETTINGS_FILE).get("tint", TINT)


def scheme_stem(base, hue, amount):
    """Hue and amount are in the name, so a changed setting gives a new file, not a stale one."""
    hue_part = "text" if hue is None else "hue%03d" % int(round(hue * 1000))
    name = os.path.splitext(os.path.basename(base))[0]
    return "%s-%s-%03d" % (name, hue_part, int(round(amount * 1000)))


SCHEME_KEYS = ("color_scheme", "light_color_scheme", "dark_color_scheme")
PREVIEW = None  # a scheme shown while the user browses the list (see the command)


def chosen_scheme():
    """The scheme the SightWalk settings give every view of a trip (Jakub): light_ or
    dark_color_scheme by the system's style, else color_scheme; None keeps Sublime's own."""
    if PREVIEW:
        return PREVIEW
    settings = sublime.load_settings(SETTINGS_FILE)
    try:
        style = sublime.ui_info()["system"]["style"]
    except Exception:
        style = ""
    return settings.get(style + "_color_scheme") or settings.get("color_scheme") or None


def resolved_scheme(view):
    """The view's scheme file: the one chosen for SightWalk, else the view's; "auto" (light or
    dark by the system) as Sublime resolved it."""
    own = view.settings().get("color_scheme") or ""
    if own.startswith("Packages/User/SightWalk/"):  # a hue of ours, never a base
        own = ""
    base = chosen_scheme() or own or "auto"
    if base == "auto":
        try:
            base = sublime.ui_info()["color_scheme"]["resolved_value"]
        except Exception:
            return ""
    return base


def tinted_schemes(view, hue, amount):
    """Writes two schemes in the file's hue: the code keeps its background and gets the band in
    the gutter and a strong outline colour; the header is the band."""
    base = resolved_scheme(view)
    scheme = load_base_scheme(base)
    if scheme is None:
        return None
    # From the scheme itself: the view may still show another while a new one is chosen.
    background, foreground = scheme_colours(scheme, view)
    # Without a hue, the band is the scheme's text colour mixed in, which always contrasts.
    band = tint_color(background, hue, amount, foreground)
    stem = scheme_stem(base, hue, amount)
    globals_ = scheme.setdefault("globals", {})
    globals_["gutter"] = band
    # Line numbers in the text colour: a faint gutter_foreground vanishes on a coloured band.
    globals_["gutter_foreground"] = globals_["gutter_foreground_highlight"] = foreground
    scheme.setdefault("rules", []).extend([
        {"scope": "sight_walk.icon", "foreground": "#ffffff"},
        {"scope": "sight_walk.outline", "foreground": tint_color(background, hue, OUTLINE_TINT)}]
        + [{"scope": "sight_walk.outline." + key, "foreground": colour}
           for key, colour in marks.ICON_COLOURS.items()])
    code = write_scheme(scheme, stem + "-code.sublime-color-scheme")
    # The header's caret line paints its gutter in the line highlight; make that the band too.
    globals_["background"] = globals_["line_highlight"] = band
    # A sight's name greyed (Jakub): the text mixed half with the band, grey in any scheme.
    scheme["rules"].append({"scope": "meta.sight-name.sight-walk", "foreground": tint_color(
        band, None, 0.5, foreground)})
    return [code, write_scheme(scheme, stem + "-header.sublime-color-scheme")]


def scheme_colours(scheme, view=None):
    """(background, foreground) of a scheme dict, its variables resolved. What cannot be read
    is guessed from the other, not taken from the view, which may still show another scheme
    (a preview's dark background stayed in the bands of the light one chosen back)."""
    found = [resolve_colour(scheme, (scheme.get("globals") or {}).get(key, ""))
             for key in ("background", "foreground")]
    if found[0] is None:
        found[0] = "#ffffff" if found[1] and luminance(found[1]) < 0.5 else "#1e1e1e"
    if found[1] is None:
        found[1] = "#1e1e1e" if luminance(found[0]) >= 0.5 else "#dddddd"
    return tuple(found)


def luminance(colour):
    r, g, b = hex_rgb(colour)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def resolve_colour(scheme, value, depth=5):
    """A "#rrggbb" from a scheme's value: #rgb, #rrggbb, rgb(), hsl(), var(name), and color(x
    ...) by its base colour x (its adjusters left out); None if it cannot be read."""
    value = str(value).strip()
    found = re.match(r"^(?:var\((\w[\w-]*)\)|color\(\s*(.+?)\s+\w+\(.*\)\s*\))$", value)
    if found and depth:
        inner = (scheme.get("variables") or {}).get(found.group(1), "") if found.group(1) \
            else found.group(2)
        return resolve_colour(scheme, inner, depth - 1)
    return plain_colour(value)


def plain_colour(value):
    """#rgb, #rrggbb(aa), rgb(a)() or hsl(a)() as "#rrggbb", or None."""
    if re.match(r"^#[0-9a-fA-F]{6}", value):
        return value[:7]
    if re.match(r"^#[0-9a-fA-F]{3}$", value):
        return "#" + "".join(c * 2 for c in value[1:])
    numbers = [float(n) for n in re.findall(r"[\d.]+", value)[:3]]
    if len(numbers) == 3 and value.startswith("rgb"):
        return "#%02x%02x%02x" % tuple(int(round(n)) for n in numbers)
    if len(numbers) == 3 and value.startswith("hsl"):
        r, g, b = colorsys.hls_to_rgb(numbers[0] / 360, numbers[2] / 100, numbers[1] / 100)
        return "#%02x%02x%02x" % tuple(int(round(c * 255)) for c in (r, g, b))
    return None


def is_dark(path):
    """Whether a scheme's background is dark, by its luminance; None if it cannot be read."""
    scheme = load_base_scheme(path)
    background = scheme and resolve_colour(scheme, (scheme.get("globals") or {}).get("background"))
    return None if not background else luminance(background) < 0.5


def apply_plain(views):
    """The views no file's hue tints (the bench, the Tools, blank views) take the chosen
    scheme as it is, or their own back when none is chosen."""
    chosen = chosen_scheme()
    for view in views:
        if chosen:
            view.settings().set("color_scheme", chosen)
        else:
            view.settings().erase("color_scheme")


def when_indexed(resources, callback, tries=200):
    # Sublime finds a freshly written file only after it indexes it, and setting a scheme it
    # can't find yet opens an error dialog. So poll the index instead of guessing a delay.
    # Up to 10 s: right after a plugin reload, indexing can take several seconds.
    if all(sublime.find_resources(os.path.basename(r)) for r in resources):
        callback()
    elif tries:
        sublime.set_timeout(lambda: when_indexed(resources, callback, tries - 1), SETTLE_MS)
    else:
        print("SightWalk: colour schemes not indexed in time, sights stay untinted:", resources)


def schemes_for(key, view, hue):
    """The code and header schemes for a file (key: path) or the conversation (key: None),
    written once per key and band amount, so a file keeps its colours across show calls."""
    amount, base = band_amount(), resolved_scheme(view)
    if (key, amount, base) not in SCHEMES:
        SCHEMES[(key, amount, base)] = tinted_schemes(view, hue, amount)
    return SCHEMES[(key, amount, base)]


GENERATION = [0]  # bumped by every change of the chosen scheme (see refresh_all)


def refresh_all():
    """A chosen colour scheme shows in every trip at once; schemes still waiting to be indexed
    for an earlier choice are dropped (see set_schemes)."""
    GENERATION[0] += 1
    for reader in list(state.READERS.values()):
        if reader.ready and reader.window.is_valid():
            reader.refresh_schemes()


def set_schemes(pairs):
    """pairs: (views, scheme resource). Set once Sublime has indexed the schemes, unless the
    chosen scheme changed meanwhile: a preview's schemes, indexed late, overwrote the scheme
    chosen back after them."""
    generation = GENERATION[0]

    def apply():
        if generation != GENERATION[0]:
            return
        for views, resource in pairs:
            for view in views:
                if view.is_valid():
                    view.settings().set("color_scheme", resource)

    when_indexed([resource for _, resource in pairs], apply)


def apply_tint(code_views, headers, path):
    schemes = schemes_for(path, code_views[0], hue_for(path))
    if schemes is not None:
        set_schemes([(code_views, schemes[0]), (headers, schemes[1])])


def apply_grey(header):
    """The conversation's header: a band like the others, in the text colour, which darkens light
    schemes and lightens dark ones."""
    schemes = schemes_for(None, header, None)
    if schemes is not None:
        set_schemes([([header], schemes[1])])


def clear_schemes():
    """Deletes the schemes SightWalk wrote that no trip's view uses (Jakub: left behind, they
    crowd Sublime's list of colour schemes), with the backups Sublime may have made. Asks the
    views (a timer of a module reloaded since knows no trips): a view of SightWalk's keeps its
    scheme; any other that kept one (a file opened in a trip and moved out) gets its own back,
    or Sublime would complain of a missing scheme."""
    used = set()
    for view in [v for w in sublime.windows() for v in w.views()]:
        scheme = view.settings().get("color_scheme") or ""
        if view.settings().get("sight_walk") or view.settings().get("sight_walk_editor"):
            used.add(scheme)
        elif scheme.startswith("Packages/User/SightWalk/"):
            view.settings().erase("color_scheme")
    for key, schemes in list(SCHEMES.items()):
        if schemes and not used & set(schemes):
            del SCHEMES[key]
    folder = scheme_folder()
    for name in os.listdir(folder) if os.path.isdir(folder) else []:
        path = os.path.join(folder, name)
        resource = "Packages/User/SightWalk/" + name.replace(".chback", "")
        # A scheme written a moment ago may wait for Sublime to index it before a view uses it.
        if ".sublime-color-scheme" in name and resource not in used \
                and time.time() - os.path.getmtime(path) > 60:
            try:
                os.remove(path)
            except OSError:
                pass
