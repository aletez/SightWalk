"""The user's links between words on the bench and places in the code (Jakub): primary+p joins a
phrase of the draft to one or more selections in the sights, both framed in the text's colour.
Two ways: the phrase selected first, then the code (every selection since), primary+p in the
sights; or the code first, then the phrase, primary+p on the bench (every selection of the sight
touched last).
The guide gets the phrase as <here at="(c):34-36 (d):12">the phrase</here>."""

import sublime

from .marks import here_tags, span_relation
from .spec import sight_name
from .subl_chat import PROTECTED

SCOPE = "sight_walk.link"  # no scheme names it: frames in the text's colour
FLAGS = sublime.DRAW_NO_FILL


class Links:
    def __init__(self, reader):
        self.reader = reader
        self.phrase = None  # the draft's last selection (a Region of the bench)
        self.picks = []  # [(sight index, Region)]: the code's selections since then
        self.last = None  # the selections of the sight touched last, [(sight index, Region)]
        self.links = {}  # bench key: [(sight index, Region)], in the order made
        self.sent = set()  # the keys of links that went out with a message, fixed since
        self.count = 0  # for the next key
        self.shown = None  # the link a click showed, so a second click hides it (Jakub)
        self.ours = None  # the bench selection this module set itself, no phrase to link

    def note_bench(self, view):
        """A selection in the draft is the phrase to link; the code's selections count anew."""
        sel = view.sel()
        if len(sel) == 1 and not sel[0].empty() and sel[0].a >= self.draft_start(view) \
                and sel[0] != self.ours:
            self.phrase, self.picks = sel[0], []

    def note_code(self, view, index):
        """Selections in a sight, all of them (several at once with primary+click): each is one
        more pick, or replaces a pick it overlaps (a drag growing it)."""
        if not len(view.sel()):
            return
        # The second way joins every selection of the sight touched last (Jakub), or the caret's
        # line when nothing is selected there.
        chosen = [(index, r) for r in view.sel() if not r.empty()]
        self.last = chosen or [(index, view.line(view.sel()[len(view.sel()) - 1]))]
        for region in [r for _, r in chosen]:
            same = [k for k, (i, r) in enumerate(self.picks) if i == index and r.intersects(region)]
            if same:
                self.picks[same[0]] = (index, region)
            else:
                self.picks.append((index, region))

    def link_from_code(self):
        """primary+p in the sights: the phrase selected on the bench joins every pick since."""
        if self.phrase is None or not self.picks:
            print("SightWalk: select words on the bench first, then code here.")
            return
        self.add(self.phrase, list(self.picks))
        self.phrase, self.picks = None, []

    def link_from_bench(self, view):
        """primary+p on the bench: the selected words (or the word at the caret) join every
        selection of the sight touched last, as the first way joins every pick (Jakub)."""
        if self.last is None:
            print("SightWalk: select code in the sights first.")
            return
        region = view.sel()[0] if len(view.sel()) else None
        if region is not None and region.empty():
            region = view.word(region)
        if region is None or region.empty() or region.a < self.draft_start(view):
            return
        self.add(region, list(self.last))

    def add(self, phrase, places):
        """A link drawn, if its words are a constituent among the draft's links (Jakub): the same
        words linked anew replace the old link, words within or around linked ones add a nested
        link, crossing words are refused. The selections give way to carets (see show_made)."""
        for key in self.draft_keys():
            relation = span_relation(tuple(phrase), tuple(self.bench_region(key)))
            if relation == "crossing":
                print("SightWalk: these words cross linked words; link a phrase within or around "
                      "them.")  # the console, where someone looks (Jakub)
                return
            if relation == "same":
                self.remove(key)
        key = "sight_walk_link_%d" % self.count
        self.count += 1
        self.links[key] = places
        self.reader.chat.add_regions(key, [phrase], SCOPE, "", FLAGS)
        for index, mine in self.by_sight(places).items():
            self.reader.sights[index].view.add_regions(key, mine, SCOPE, "", FLAGS)
        self.show_made(phrase, places)

    def show_made(self, phrase, places):
        """The selections replaced by a caret at each linked region's end, so the user sees the
        link took (Jakub)."""
        carets(self.reader.chat, [phrase])
        for index, mine in self.by_sight(places).items():
            carets(self.reader.sights[index].view, mine)

    def remove(self, key):
        self.reader.chat.erase_regions(key)
        for sight in self.reader.sights:
            sight.view.erase_regions(key)
        self.links.pop(key, None)
        self.shown = None if self.shown == key else self.shown

    def prune(self, view):
        """Linked words deleted from the draft: their region stays, of length zero, until erased
        (Jakub), so a link goes when its length does."""
        for key in self.draft_keys():
            if self.bench_region(key).empty():
                self.remove(key)

    def draft_keys(self):
        return [key for key in self.links if key not in self.sent]

    def bench_region(self, key):
        found = self.reader.chat.get_regions(key)
        return found[0] if found else sublime.Region(0)

    def by_sight(self, places):
        found = {}
        for index, region in places:
            found.setdefault(index, []).append(region)
        return found

    def tagged(self, view):
        """The draft with its links as <here> tags, nested where the words nest, stripped as the
        bench sends it; those links are fixed from now on."""
        start = self.draft_start(view)
        text = view.substr(sublime.Region(start, view.size()))
        spans = [(r.a - start, r.b - start, self.places(self.links[key]))
                 for key, r in ((k, self.bench_region(k)) for k in self.draft_keys())
                 if r.a >= start and not r.empty()]
        self.sent.update(self.links)
        return here_tags(text, spans).strip()

    def places(self, places):
        """'(c):34-36 (d):12' for the guide."""
        found = []
        for index, region in places:
            view = self.reader.sights[index].view
            first, last = (view.rowcol(p)[0] + 1 for p in (region.begin(), max(region.begin(),
                                                                               region.end() - 1)))
            lines = str(first) if first == last else "%d-%d" % (first, last)
            found.append("%s:%s" % (sight_name(index), lines))
        return " ".join(found)

    def follow(self, view):
        """A click into linked words on the bench selects their places in the code and shows the
        first; a second click on them takes the selection off again, as many schemes leave
        selected code uncoloured (Jakub). Called on the click itself (drag_select): a second
        click leaves the caret where it was, and Sublime reports no change of selection."""
        sel = view.sel()
        if len(sel) != 1 or not sel[0].empty():
            return False
        key = next((k for k in self.links if self.bench_region(k).contains(sel[0].b)
                    and not self.bench_region(k).empty()), None)
        if key is None:
            self.shown = None
            return False
        places = self.links[key]
        for index, mine in self.by_sight(places).items():
            code = self.reader.sights[index].view
            if key == self.shown:
                carets(code, mine)
            else:
                code.sel().clear()
                code.sel().add_all(mine)
            repaint(code)
        self.shown = None if key == self.shown else key
        if self.shown:
            index, region = places[0]
            self.reader.show_place(index, self.reader.sights[index].view.rowcol(region.a)[0] + 1)
        return True

    def follow_code(self, view, index):
        """A click into a linked place in the code selects every phrase on the bench that refers
        to it (Jakub); a second click takes the selection off."""
        sel = view.sel()
        if len(sel) != 1 or not sel[0].empty():
            return
        keys = [k for k, places in self.links.items()
                if any(i == index and r.contains(sel[0].b) for i, r in places)]
        phrases = [self.bench_region(k) for k in keys]
        if not phrases or ("code", tuple(keys)) == self.shown:
            self.shown = None
            if phrases:
                carets(self.reader.chat, phrases)
                self.repaint_bench()
            return
        self.shown = ("code", tuple(keys))
        self.ours = phrases[0] if len(phrases) == 1 else None
        self.reader.chat.sel().clear()
        self.reader.chat.sel().add_all(phrases)
        self.repaint_bench()

    def repaint_bench(self):
        """The bench drawn now, as a sight is (see repaint): its pixel's move marked as an edit
        of it, so it is not read as the wheel moving the trip (see Reader.bench_edited). Not
        scrolled to the phrases: that move would be the wheel's."""
        self.reader.bench_edited()
        repaint(self.reader.chat)

    def draft_start(self, view):
        """The draft starts after the protected transcript (see subl_chat)."""
        return len(PROTECTED.get(view.buffer_id(), ""))

    def clear(self):
        """Another trip: the links were to other sights."""
        for key in list(self.links):
            self.remove(key)


def carets(view, regions):
    """The selections replaced by a caret at the end of each region."""
    selected = view.sel()
    selected.clear()
    selected.add_all([sublime.Region(r.end()) for r in regions])


def repaint(view):
    """A view without the focus may draw a selection set from code only when the mouse passes
    over it (Jakub): a pixel's move and back makes Sublime draw it now; the same place again is
    skipped as no change."""
    x, y = view.viewport_position()
    view.set_viewport_position((x, y + 1), False)
    sublime.set_timeout(lambda: view.set_viewport_position((x, y), False), 0)
