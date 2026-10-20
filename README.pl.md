# SightWalk

**Sprawdzaj wygenerowany kod na wycieczce, którą ułoży dla Ciebie przewodnik AI.**

*In English: [README.md](README.md).*

SightWalk to wtyczka do Sublime Text. Zadajesz pytanie o swój kod, a agent AI, **przewodnik**,
układa **wycieczkę**, która na nie odpowiada: wybiera potrzebne funkcje i ustawia je w jednej
kolumnie, najczęściej jako jedno wykonanie programu, funkcja po funkcji, w kolejności, w jakiej
przechodzi przez nie sterowanie. Potem oprowadza Cię po wycieczce, objaśnia ją i zaznacza linie,
a Ty rozmawiasz z nim w ławce obok kodu.

Przewodnikiem może być każdy agent, który mówi przez MCP: Claude Code, którego SightWalk umie
uruchomić sam, albo inny agent, także lokalny model. Nie musi to być agent, który napisał kod.

![Wycieczka z turnusu samej wtyczki, „Registering the guide”. Ławka zaczyna się od opowieści
Pioniera; użytkownik pyta „kto to woła?”, ze słowem połączonym z kodem, i jak run woła
ensure_token i write_config; przewodnik odpowiada numerowanymi ikonami i dwoma skokami
wywołań, w ramkach w swoich słowach i na marginesie; mapa turnusu poniżej](docs/images/trip.jpg)

*Wszystkie zrzuty pochodzą z prawdziwych sesji: wtyczka sprawdza własny kod. Ta rozmowa jest po
angielsku, pozostałe po polsku, tak jak się odbyły; interfejs na zrzutach jest angielski.*

*Stan: publiczna alfa (październik 2026). Na co dzień działa na własnym kodzie; zdarzają się
szorstkie miejsca.*

---

## Po co

AI pisze kod szybciej, niż ludzie go czytają. Wąskie gardło przesunęło się z pisania na
**sprawdzanie**: pewność, że wygenerowany kod robi to, o co prosiłeś, i nic więcej.

W zwykłym edytorze kod leży tak, jak jest *przechowywany*: plik po pliku, w każdym z góry na
dół. Pytanie „co się dzieje, gdy przychodzi żądanie?” oznacza skakanie po pięciu plikach,
gubienie miejsca i trzymanie całej ścieżki w głowie.

W SightWalk przewodnik układa kod tak, jak się *wykonuje*, albo tak, jak potrzebuje go Twoje
pytanie, i zostaje obok, żeby odpowiadać za każdą linię.

## Pomysł w kilku słowach

Wtyczka mówi językiem zwiedzania:

| Nazwa | Co to jest |
|---|---|
| **Panorama** | Prawa kolumna z kodem. |
| **Widok** | Jeden panel panoramy: zakres linii pliku, najwyżej jedna funkcja, cała albo fragment. |
| **Wycieczka** | Ciąg widoków dobranych do jednego pytania, czytany z góry na dół; tak nazywa się też samo okno. |
| **Przewodnik** | Agent AI: dobiera wycieczkę, objaśnia ją, zaznacza linie i odpowiada. |
| **Ławka** | Panel rozmowy z przewodnikiem. |

Wycieczka bywa jednego z trzech rodzajów:

- **wykonanie**: jedno wykonanie programu, widoki w kolejności, w jakiej przechodzi przez nie sterowanie;
- **porównanie**: fragmenty obok siebie, np. dwie implementacje albo kod przed zmianą i po niej;
- **przegląd**: wszystkie miejsca dotyczące jednej rzeczy, np. każda obsługa jednego błędu.

Wycieczki można zapisać, połączyć w **informator** (sieć wycieczek obejmujących cały kod
programu, z przejściami między nimi) i wybrać się na wybrane z nich w ustalonej
kolejności, czyli odbyć **turnus**. Tak opisany jest kod samej wtyczki: [docs/trips.md](docs/trips.md) dzieli go na pełen
turnus 43 wycieczek, a każdą funkcję umieszcza w co najmniej jednej.

## Spacer po interfejsie

### Wycieczka

Po prawej **panorama**: jedna kolumna widoków, przewijana jak jeden dokument. Każdy widok ma
nagłówek z nazwą, (a), (b), (c)…, i plikiem, zabarwiony kolorem swojego pliku. Linie `def`
i `class`, do których należy fragment, stoją zamrożone pod nagłówkiem, a „⋮ 10 linii Handler”
mówi, co zostało pominięte. Panorama przesuwa się jak jeden dokument, każdy nagłówek
przy swoim kodzie, a ławka stoi: przesuwa ją kółko nad paskiem przewijania, a nad ławką i panelem Narzędzi
wtedy, gdy `⌘S` tak ustawi. Nad kodem widoku kółko przewija tylko ten widok.

Po lewej **ławka**. Na górze strony użytkownik pyta, czemu klient dostaje 202 **here**, a nie
200, z „here” połączonym z linią 105. Przewodnik odpowiada znacznikami: ikony **1** i **2** na
dwóch liniach `reply`, które odrzucają powiadomienie, skok **comes back** z `return None` do
linii 105, ikona **3** na tej linii i skok **asks answer** dla drugiej gałęzi. Na zrzucie
Turnusu niżej użytkownik pyta *po co reply i answer są oddzielnie?*. Nazwy funkcji w ławce mają
kolory takie jak w kodzie.

W ławce mówią trzy głosy. **P:** to **Pionier** wycieczki: ten, kto ją wytyczył, przekarczował
drogę przez kod albo przedarł się przez zastany, i nie zawsze autor kodu. Ławka każdej nowej
wycieczki zaczyna się od jego opowieści. **U:** to ty, **użytkownik**. **A:** to **agent AI**,
twój **przewodnik**, który może być kimś innym niż Pionier, a przy surowym vettingu wcale nie
jego przyjacielem.

◀ ▶ (⌘[ ⌘]) przechodzą po wycieczkach okna, każda z własną rozmową. **Przygoda** to zboczenie
ze szlaku, bo jest ciekawy kwiatek: przewodnik otwiera krótką wycieczkę w oknie nad bieżącym, a
zakładka **Przygody** otwiera dawne z powrotem, takie, jakie je zostawiono.

![Przygoda nad swoją wycieczką: użytkownik zapytał, gdzie sprawdzany jest token, a przewodnik
zboczył ze szlaku w osobnym oknie, z powodem na początku ławki przygody](docs/images/adventure.jpg)

### Każde odniesienie to link

Przewodnik i użytkownik mają jeden język znaczników. Przewodnik wiąże słowa z miejscami tak:
`<here at="(c):34" icon="1">ten warunek</here>` (linia dostaje ikonę 1), `<here at="(c):34:12-16">ta
nazwa</here>` (znaki, bez ikony) albo `<calls at="(a):33 (b):41">wywołuje</calls>` (skok; tak samo
dla każdego typu przejścia). Widzisz słowa w ramce koloru znacznika, ze znakiem ikony po nich, a
linia dostaje tę samą ikonę na marginesie (drugi znacznik
tej samej linii stoi na wąskim pasku na lewo od panoramy). Znacznik przewinięty poza ekran
zostawia oko na najbliższej widocznej linii, więc nie da się go przeoczyć. Kliknięcie obramowanego
słowa zaznacza to, do czego się odnosi (oba końce skoku), i zapala tę samą strzałkę na mapie;
drugie kliknięcie zdejmuje zaznaczenie.

Można też linkować w drugą stronę. Zaznacz słowa w swojej wiadomości, zaznacz kod, naciśnij
`⌘P` (`Ctrl+P`), a przewodnik dostanie wiadomość z tym linkiem jako
`<here at="(c):34-36">to sprawdzenie</here>`. Wiadomość bez linków niesie to, co masz
zaznaczone w kodzie, więc „czemu *to* tu jest?” zawsze znaczy to, na co patrzysz, nigdy zgadywanie.

### Mapa

![Mapa w panelu Narzędzi rozłożonym na okno: pięć funkcji jako prostokąty w swojej klasie i
dwóch plikach, wywołania nazwane przez przewodnika jako strzałki](docs/images/map.jpg)

Panel Narzędzi pod ławką rysuje wycieczkę jako graf wywołań (przez Graphviz). Każdy widok to
prostokąt w swojej klasie i pliku, a każde przejście nazwane przez przewodnika to strzałka.
Każdy typ ma własny wygląd: `calls`, `returns`, `leads_to`, `passes_data`, `unblocks` (odblokowuje:
trzeba zrozumieć najpierw), `comparable`. Mapa pokazuje dokładnie to, co zadeklarował przewodnik, i
niczego nie zgaduje. Gdy rysunek jest zły, zła jest relacja przewodnika, a to już samo w sobie
jest znaleziskiem.

### Turnusy

![Mapa turnusu rozłożona na okno: wycieczki jako kolumny widoków w barwach ich plików, przejścia
między wycieczkami jako strzałki, legenda w prawym górnym rogu](docs/images/tour-map.jpg)

**SightWalk: Open Tour** wylicza turnusy znalezione w otwartych folderach. Zakładka Turnus
pokazuje wycieczki po kolei, w nagłówku „Wycieczka 4 · …”, a przebytą wycieczkę odhaczasz sam.
Każda wycieczka pamięta swoją rozmowę i znaczniki przewodnika, więc spacer trwa dalej tam, gdzie
się urwał.

Pod listą stoi **mapa turnusu**, tym dla turnusu, czym Mapa dla wycieczki: drogowskaz głównych i
tajnych przejść między wycieczkami. Każda wycieczka to kolumna jej widoków, nazwanych
plik:funkcja w barwie swojego pliku, a strzałki między wycieczkami to `leads_to` i `unblocks`
autora, więc da się wyczytać inną kolejność niż turnusu i zobaczyć z lotu ptaka, co umiesz,
czego nie, a co chcesz teraz umieć. Kliknięcie widoku otwiera jego wycieczkę. Wycieczki są
krótkie, około pięciu kroków, a każdy krok może rozwinąć przygoda. `[⤢]` w nagłówku Narzędzi
rozkłada dowolną zakładkę na prawie całe okno; `[⤢]` jeszcze raz albo `Esc` ją przywraca.

### Edycja na miejscu

![Edytor otwarty nad panoramą: cały plik w liniach widoku, znaczniki przewodnika na jego
marginesie, „Zakończ edycję (Esc)” w nagłówku widoku](docs/images/editor.jpg)

`Enter` w widoku otwiera prawdziwy plik wprost nad wycieczką, w tych samych
liniach. Zapisz, a wycieczka się przeładuje: każdy widok w nowym zakresie, każdy znacznik w
nowej linii. Następna wiadomość powie przewodnikowi, które zakresy się zmieniły. `Esc` chowa
edytor, a panele wracają tam, gdzie były.

### Co wolno przewodnikowi

![Zakładka Uprawnienia: pole przy każdym uprawnieniu, każde z wyjaśnieniem](docs/images/permissions.jpg)

Gdy zadasz pytanie w ławce, a żaden przewodnik nie jest połączony, SightWalk go uruchamia:
sesję Claude Code w tle, w repozytorium wycieczki. Domyślnie może tylko czytać kod. Zakładka
Uprawnienia podnosi to według celu. Każde pole ma `[?]`, które mówi dokładnie, na co pozwala:
edycja plików (w folderach, które wskażesz), zestawy poleceń powłoki (podgląd gita, testy,
skrypty, commit, instalowanie, push) i szukanie w sieci. Wybory nieodwracalne, jak `git push` i
nieograniczona powłoka, obowiązują tylko przez jedną sesję i nie są zapamiętywane. Zmiana
restartuje przewodnika, a rozmowa zostaje. Gdy przewodnikowi czegoś brakuje, mówi o tym w ławce
i nazywa pole. Uzasadnienie zestawów jest w
[docs/guide-permissions.md](docs/guide-permissions.md) (po angielsku).

### Odpowiedzi

<img src="docs/images/answers.jpg" alt="Zakładka Odpowiedzi pod ławką: każda opowieść, pytanie i odpowiedź rozmowy po pierwszych słowach, odpowiedzi z liczbą ikon; kliknięte pytanie pogrubione" width="420">

Zakładka Odpowiedzi wylicza wszystkie pytania i odpowiedzi z ławki po pierwszych słowach.
Kliknięcie przenosi jedno z nich na górę ławki razem ze znacznikami (przy pytaniu: z tym, co było
zaznaczone, gdy je wysłałeś). Drugie kliknięcie je chowa i przywraca ławkę tam, gdzie była.

## Jak to jest zbudowane

```
Przewodnik ──MCP przez HTTP──▶ subl_mcp_http ──▶ validator (czysty) ──▶ subl_executor ──▶ Sublime
                                  sama wtyczka                              wycieczka, ławka, mapa
```

- **Wtyczka jest serwerem MCP.** Nie ma osobnego procesu: serwer HTTP z tokenem działa w
  Pythonie 3.8 samego Sublime, na samej bibliotece standardowej.
- **Każde wywołanie jest oceniane, zanim zadziała.** Czysty moduł `validator` odrzuca wywołanie
  łamiące regułę, a jego komunikat mówi, co zrobić zamiast tego. Na przykład `show` odrzuca widok
  z dwiema funkcjami, a `say` linię z trzema znacznikami. Wykonawca zbiera fakty, walidator tylko
  je ocenia. Agenci uczą się z tych odmów jeszcze w tej samej sesji.
- **Czysty rdzeń, cienka warstwa Sublime.** Moduły bez API Sublime (`spec`, `plan`, `marks`,
  `ontology`, `callmap`, `validator`, `manual`, `permissions`…) trzymają logikę i są testowane
  zwykłym Pythonem. Moduły z przedrostkiem `subl_` robią tylko to, czego trzeba od edytora, więc
  przeniesienie do innego edytora zaczyna się od tego samego rdzenia.
- **Ontologia zamiast doraźnych list.** Widoki, wycieczki, informatory i turnusy to jedna
  hierarchia kolekcji z typowanymi przejściami między miejscami (`sw/ontology.py`); pliki
  wycieczek to jej postać w JSON.
- **Sprawdzana sobą.** Funkcje mają około 25 linii, żeby każda mieściła się w jednym widoku.
  Skrypt `tools/trips.py` zapisuje kod wtyczki jako wycieczki i wymienia każdą funkcję, której
  żadna wycieczka nie obejmuje, więc dokumentacja nie zostanie po cichu w tyle za kodem.

Około 7100 linii Pythona w 33 modułach, około 400 commitów od 4 października 2026.

## Jak powstała

**Koncepcja i projekt: Jakub Kozakoszczak. Kod: napisany przez Claude'a** (model Anthropic, w
Claude Code).

Ten podział to metoda, nie przypis. Jakub projektuje każde zachowanie, decyduje i sprawdza każdą
zmianę w Sublime. Claude implementuje, testuje i proponuje alternatywy z uzasadnieniem. Zasady
współpracy są w [CLAUDE.md](CLAUDE.md). Każda decyzja projektowa, jej powód i obecny stan są w
[DECISIONS.md](DECISIONS.md): najnowsze na górze, każda oznaczona jako sprawdzona, zmieniona
bez sprawdzenia albo otwarta. Nic nie jest uznane za działające, dopóki projektant nie zobaczy,
że działa.

SightWalk jest też narzędziem, którego ten sposób pracy potrzebował: kodem pisanym przez AI, za
którym da się nadążyć, który da się przepytać i któremu można zaufać.

## Instalacja (alfa)

Wymagania: macOS, Linux albo Windows; [Sublime Text 4](https://www.sublimetext.com/);
[Claude Code](https://claude.com/claude-code); do mapy [Graphviz](https://graphviz.org/)
(`brew install graphviz`).

1. Umieść repozytorium w pakietach Sublime, np. dowiązaniem (przykład dla macOS):
   ```bash
   ln -s "$PWD" ~/Library/Application\ Support/Sublime\ Text/Packages/SightWalk
   ```
2. W Sublime uruchom z palety poleceń **SightWalk: Set Up Agent Bridge**. Utworzy token i
   położy polecenie rejestracji w schowku.
3. Wklej to polecenie w terminalu i je uruchom (`claude mcp add … sight-walk …`).
4. Otwórz sesję Claude Code w swoim projekcie i poproś na przykład: *„Użyj sight-walk, żeby
   oprowadzić mnie po tym, co się dzieje, gdy przychodzi żądanie, a potem czekaj na moje
   pytania.”* Możesz też napisać pytanie w ławce pustej wycieczki (`⌘G` / `Ctrl+G`, gdy ten skrót
   jest włączony), a SightWalk sam uruchomi przewodnika.

### Klawisze

| Klawisz | W wycieczce |
|---|---|
| `Enter`, `⇧Enter` | wyślij wiadomość z ławki; nowa linia |
| `⌘P` | połącz zaznaczone słowa z zaznaczonym kodem |
| `Enter`, `Esc` | otwórz edytor widoku, zamknij go |
| `Alt+R` | przywróć położenia |
| `⌘[`, `⌘]` | wstecz i naprzód po wycieczkach okna (◀ ▶) |
| `⌘S` | przełącza, co robi kółko nad ławką i panelem Narzędzi: przesuwa panoramę widoków albo przewija ten panel |
| `Ctrl+Tab` | fokus na następny widok na ekranie |

`⌘` to `Ctrl` w Windows i Linuksie. Interfejs mówi po angielsku i po polsku
(**SightWalk: Switch Language**).

## Stan i ograniczenia

- Alfa, budowana i używana na macOS; Windows i Linux nie były testowane.
- SightWalk sam uruchamia Claude Code jako przewodnika. Zamiast niego może się połączyć każdy
  inny agent MCP i dostaje ten sam podręcznik przez MCP; sprawdzony jest tylko Claude Code.
- Granice funkcji są rozpoznawane w Pythonie. W innych językach widok nigdy nie jest odrzucany
  za dwie funkcje.
- `Esc` jeszcze nie u każdego zmniejsza powiększony panel Narzędzi; `[⤢]` tak.
- W planach: notatki linkowane do rozmowy, legenda znaczników na ekranie, lista sprawdzeń, które
  kod robi gdzie indziej, a tu nie, i osobny przewodnik dla każdej przygody, znający tylko jej
  wątek.

## Mapa repozytorium

| Ścieżka | Co |
|---|---|
| `sight_walk.py` | punkt wejścia ładowany przez Sublime |
| `sw/` | wtyczka: moduły czyste i moduły `subl_*`, które używają Sublime |
| `tests/` | testy jednostkowe czystych modułów (`python3 -m unittest discover tests`) |
| `tools/poke.py` | steruje wtyczką przez MCP bez agenta |
| `tools/trips.py` | zapisuje kod wtyczki jako wycieczki w `docs/` |
| `docs/` | wycieczki, informator i turnusy samej wtyczki; testowanie; uprawnienia |
| `DECISIONS.md` | decyzje projektowe, powody i stan |
| `CLAUDE.md` | jak projektant i AI pracują nad tym repozytorium |

## Autor

Jakub Kozakoszczak, koncepcja i projekt: [LinkedIn](https://www.linkedin.com/in/jakub-kozakoszczak/)

## Licencja

[MIT](LICENSE)
