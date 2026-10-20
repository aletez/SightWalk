"""The words the user reads, in English or Polish (Jakub), by the setting language. The Polish
names are a metaphor of their own: panorama, widok, wycieczka, mapa, turnus, ławka. Pure, no
Sublime API: the plugin sets LANGUAGE when the setting changes."""

LANGUAGES = ("en", "pl")
LANGUAGE = "en"

WORDS = {
    "bench": ("Bench", "Ławka"),
    "bench_view": ("Vetting Bench", "Ławka"),
    "sights": ("Sights", "Panorama"),
    "or": ("or", "lub"),
    "max_help": ("the tools over almost the whole window, or back (Esc too)",
                 "narzędzia na prawie całe okno albo z powrotem (także Esc)"),
    "nav_help": ("back and forward through this window's trips",
                 "wstecz i naprzód po wycieczkach tego okna"),
    "reset_help": ("the sights back where the guide showed them",
                   "widoki z powrotem tam, gdzie pokazał je przewodnik"),
    "trip_title": ("Trip", "Wycieczka"),  # the Sights' header: Sights stays for the manual (Jakub)
    "link_help": ("link the selected words to the selected code",
                  "połącz zaznaczone słowa z zaznaczonym kodem"),
    "tools": ("Tools", "Narzędzia"),
    "Map": ("Map", "Mapa"),
    "Tour": ("Tour", "Turnus"),
    "Permissions": ("Permissions", "Uprawnienia"),
    "Answers": ("Answers", "Odpowiedzi"),
    "Adventures": ("Adventures", "Przygody"),
    "adventure_title": ("Adventure", "Przygoda"),
    "no_adventures": ("No adventures yet: a guide opens one off the trail when something along it "
                      "is worth a closer look.",
                      "Nie było jeszcze przygód: przewodnik otwiera przygodę z dala od szlaku, gdy "
                      "coś po drodze jest warte bliższego spojrzenia."),
    "no_answers": ("No questions or answers on the bench yet.",
                   "Na ławce nie ma jeszcze pytań ani odpowiedzi."),
    "icons_n": ("(icons: %d)", "(ikony: %d)"),
    "stale": ("(stale)", "(nieaktualne)"),
    "earlier_trip": ("(an earlier trip)", "(wcześniejsza wycieczka)"),
    "perm_intro": ("What the guide SightWalk starts may do. A change restarts it while it waits; "
                   "the conversation goes on.",
                   "Co może przewodnik uruchamiany przez SightWalk. Zmiana restartuje go, gdy "
                   "czeka; rozmowa trwa dalej."),
    "perm_not_ours": ("The guide now listening was not started by SightWalk (a terminal session): "
                      "it has that session's permissions, which this tab does not change.",
                      "Teraz słucha przewodnik nieuruchomiony przez SightWalk (sesja z terminala): "
                      "ma uprawnienia tamtej sesji, których ta zakładka nie zmienia."),
    "perm_read": ("Reading (always)", "Czytanie (zawsze)"),
    "perm_read_tip": ("Read, Grep, Glob: any file your account can read, secrets too if asked to. "
                      "Nothing changes on disk.",
                      "Read, Grep, Glob: każdy plik, który może czytać Twoje konto, także sekrety, "
                      "jeśli o nie poprosisz. Nic się nie zmienia na dysku."),
    "perm_edit": ("Editing files in:", "Edycja plików w:"),
    "perm_edit_tip": ("Edit and Write, only inside these folders. Changes code; git can undo it. "
                      "The edited sights reload, so you see each change.",
                      "Edit i Write, tylko w tych folderach. Zmienia kod; git to odwróci. "
                      "Zmienione widoki się przeładowują, więc widzisz każdą zmianę."),
    "perm_add_folder": ("+ folder", "+ folder"),
    "perm_folder_prompt": ("Folder the guide may edit:", "Folder, który przewodnik może edytować:"),
    "perm_git_look": ("Bash: git, look", "Bash: git, podgląd"),
    "perm_git_look_tip": ("git status, log, diff, show, blame. Changes nothing.",
                          "git status, log, diff, show, blame. Niczego nie zmienia."),
    "perm_tests": ("Bash: tests", "Bash: testy"),
    "perm_tests_tip": ("python3 -m unittest, pytest, npm test. Runs the project's code.",
                       "python3 -m unittest, pytest, npm test. Uruchamia kod projektu."),
    "perm_web": ("Web", "Sieć"),
    "perm_web_tip": ("WebFetch, WebSearch: library docs, error messages. Sends queries and URLs "
                     "out; cannot change the code.",
                     "WebFetch, WebSearch: dokumentacja bibliotek, komunikaty błędów. Wysyła "
                     "zapytania i adresy na zewnątrz; nie zmienia kodu."),
    "perm_scripts": ("Bash: run scripts", "Bash: uruchamianie skryptów"),
    "perm_scripts_tip": ("python3 …, node …: runs any code, also code the guide writes. "
                         "Remembered, shown on the bench's header while on.",
                         "python3 …, node …: uruchamia dowolny kod, także napisany przez "
                         "przewodnika. Pamiętane, widoczne w nagłówku ławki, póki włączone."),
    "perm_git_commit": ("Bash: git, commit", "Bash: git, commit"),
    "perm_git_commit_tip": ("git add, git commit: local history only, never push. Remembered, "
                            "shown on the bench's header while on.",
                            "git add, git commit: tylko lokalna historia, bez push. Pamiętane, "
                            "widoczne w nagłówku ławki, póki włączone."),
    "perm_install": ("Bash: install", "Bash: instalowanie"),
    "perm_install_tip": ("pip, npm, brew install: downloads and runs third-party code. "
                         "Remembered, shown on the bench's header while on.",
                         "pip, npm, brew install: pobiera i uruchamia cudzy kod. Pamiętane, "
                         "widoczne w nagłówku ławki, póki włączone."),
    "perm_git_push": ("Bash: git, push", "Bash: git, push"),
    "perm_git_push_tip": ("git push: publishes, cannot be taken back. One guide session only, "
                          "never remembered.",
                          "git push: publikuje, nie da się cofnąć. Tylko na jedną sesję "
                          "przewodnika, nigdy niepamiętane."),
    "perm_bash_all": ("Bash: everything", "Bash: wszystko"),
    "perm_bash_all_tip": ("Any command you could type in a terminal. One guide session only, "
                          "never remembered.",
                          "Każde polecenie, które mógłbyś wpisać w terminalu. Tylko na jedną "
                          "sesję przewodnika, nigdy niepamiętane."),
    "guide_may": ("guide may: %s", "przewodnik może: %s"),
    "fit": ("fit", "dopasuj"),
    "edit": ("Edit (Enter)", "Edytuj (Enter)"),
    "end_edit": ("End editing (Esc)", "Zakończ edycję (Esc)"),
    "reset": ("Reset positions", "Przywróć położenia"),
    "stop": ("Stop (Esc)", "Zatrzymaj (Esc)"),
    "stopped": ("(stopped)", "(zatrzymano)"),
    "coming": ("the guide is coming…", "przewodnik nadchodzi…"),
    "thinking": ("the guide is thinking…", "przewodnik myśli…"),
    "send": ("send", "wyślij"),
    "new_line": ("new line", "nowa linia"),
    "pan": ("the wheel over the bench and the tools moves the pane under it or the column of sights",
            "kółko nad ławką i narzędziami przesuwa panel pod spodem lub panoramę widoków"),
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
    "scheme_general": (["General", "one colour scheme, light or dark alike"],
                       ["Wspólny", "jeden schemat kolorów, jasny i ciemny"]),
    "scheme_light": (["Light", "while the system is light; light schemes only"],
                     ["Jasny", "gdy system jest jasny; tylko jasne schematy"]),
    "scheme_dark": (["Dark", "while the system is dark; dark schemes only"],
                    ["Ciemny", "gdy system jest ciemny; tylko ciemne schematy"]),
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


def lines_of(n, name):
    """"14 lines of run", "14 linii run": what a fragment leaves out (Jakub), no "more"."""
    if LANGUAGE != "pl":
        return "%d line%s of %s" % (n, "" if n == 1 else "s", name)
    few = n % 10 in (2, 3, 4) and n % 100 not in (12, 13, 14)
    return "%d %s %s" % (n, "linia" if n == 1 else "linie" if few else "linii", name)


def trips_count(n):
    """"35 trips", "35 wycieczek": Polish has three plural forms."""
    if LANGUAGE != "pl":
        return "%d trip%s" % (n, "" if n == 1 else "s")
    if n == 1:
        return "1 wycieczka"
    few = n % 10 in (2, 3, 4) and n % 100 not in (12, 13, 14)
    return "%d %s" % (n, "wycieczki" if few else "wycieczek")
