"""Overlay scroll bars while a reader has the focus, the user's own value otherwise. Sublime has
no per-window switch, so the application setting is changed in memory only, never saved."""

import sublime

PREFS = "Preferences.sublime-settings"
KEY = "overlay_scroll_bars"
SAVED = []  # (whether the user had a value, the value) while a reader has the focus


def reader_focused(focused):
    prefs = sublime.load_settings(PREFS)
    if focused and not SAVED:
        SAVED.append((prefs.has(KEY), prefs.get(KEY)))
        prefs.set(KEY, "enabled")
    elif not focused and SAVED:
        had, value = SAVED.pop()
        if had:
            prefs.set(KEY, value)
        else:
            prefs.erase(KEY)
