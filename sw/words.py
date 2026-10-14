"""The words the user reads, in English or Polish (Jakub), by the setting language. The Polish
names are a metaphor of their own: panorama, widok, wycieczka, mapa, turnus, ławka. Pure, no
Sublime API: the plugin sets LANGUAGE when the setting changes."""

LANGUAGES = ("en", "pl")
LANGUAGE = "en"

WORDS = {
    "bench": ("Bench", "Ławka"),
    "bench_view": ("Vetting Bench", "Ławka"),
    "sights": ("Sights", "Panorama"),
    "tools": ("Tools", "Narzędzia"),
    "Map": ("Map", "Mapa"),
    "Tour": ("Tour", "Turnus"),
    "Scroll": ("Scroll", "Przewijanie"),
    "edit": ("Edit (Enter)", "Edytuj (Enter)"),
    "reset": ("Reset positions", "Przywróć położenia"),
    "stop": ("Stop (Esc)", "Zatrzymaj (Esc)"),
    "stopped": ("(stopped)", "(zatrzymano)"),
    "coming": ("the guide is coming…", "przewodnik nadchodzi…"),
    "thinking": ("the guide is thinking…", "przewodnik myśli…"),
    "send": ("send", "wyślij"),
    "new_line": ("new line", "nowa linia"),
    "next": ("explain next", "wyjaśnij następny krok"),
    "previous": ("explain previous", "wyjaśnij poprzedni krok"),
    "pan": ("the wheel over the bench, Map and Tour: %s (press to change)",
            "kółko nad ławką, Mapą i Turnusem: %s (naciśnij, by zmienić)"),
    "pan_on": ("moves the whole trip", "przesuwa całą wycieczkę"),
    "pan_off": ("scrolls the tool itself", "przewija samo narzędzie"),
    "no_tour": ("No tour is open: <i>SightWalk: Open Tour</i> in the command palette.",
                "Żaden turnus nie jest otwarty: <i>SightWalk: Open Tour</i> w palecie poleceń."),
    "no_dot": ("The map needs Graphviz: <code>brew install graphviz</code>, or set "
               "<code>dot_path</code> in Preferences: SightWalk Settings.",
               "Mapa potrzebuje Graphviza: <code>brew install graphviz</code> albo ustaw "
               "<code>dot_path</code> w Preferences: SightWalk Settings."),
    "dot_failed": ("Graphviz failed: ", "Graphviz zawiódł: "),
    "run": ("run", "przebieg"),
    "comparison": ("comparison", "porównanie"),
    "survey": ("survey", "przegląd"),
    "all_trips": ("All trips", "Wszystkie wycieczki"),
    "asked": ("The code asks this elsewhere:", "Kod pyta o to gdzie indziej:"),
    "close_trip": ("Close the trip's window?", "Zamknąć okno wycieczki?"),
    "close": ("Close", "Zamknij"),
    "no_informators": ("SightWalk found no informators/*.json in the open folders.",
                       "SightWalk nie znalazł informators/*.json w otwartych folderach."),
    "no_claude": ('SightWalk could not find Claude Code. Set "claude_path" in Preferences: '
                  "SightWalk Settings, or start claude yourself.",
                  "SightWalk nie znalazł Claude Code. Ustaw \"claude_path\" w Preferences: "
                  "SightWalk Settings albo uruchom claude sam."),
}


def word(key):
    return WORDS[key][1 if LANGUAGE == "pl" else 0]


def set_language(language):
    global LANGUAGE
    LANGUAGE = language if language in LANGUAGES else "en"


def trips_count(n):
    """"35 trips", "35 wycieczek": Polish has three plural forms."""
    if LANGUAGE != "pl":
        return "%d trip%s" % (n, "" if n == 1 else "s")
    if n == 1:
        return "1 wycieczka"
    few = n % 10 in (2, 3, 4) and n % 100 not in (12, 13, 14)
    return "%d %s" % (n, "wycieczki" if few else "wycieczek")
