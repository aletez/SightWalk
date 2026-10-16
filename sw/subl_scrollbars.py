"""No scroll bars while a reader has the focus, the user's own ones otherwise. Sublime has no
per-window switch, so application settings are changed in memory only, never saved: overlay scroll
bars (they take no room) and a flag the package's theme rules read to make them invisible."""

import sublime

PREFS = "Preferences.sublime-settings"
KEY = "overlay_scroll_bars"
HIDE = "sight_walk_hide_scroll_bars"
SAVED = []  # (whether the user had a value, the value) while a reader has the focus


def reader_focused(focused):
    prefs = sublime.load_settings(PREFS)
    # Read by the rules in the package's Default and Adaptive themes, which hide the bars.
    prefs.set(HIDE, bool(focused))
    if focused and not SAVED:
        SAVED.append((prefs.has(KEY), prefs.get(KEY)))
        prefs.set(KEY, "enabled")
    elif not focused and SAVED:
        had, value = SAVED.pop()
        if had:
            prefs.set(KEY, value)
        else:
            prefs.erase(KEY)
