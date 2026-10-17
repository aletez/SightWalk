"""The user's links between words on the bench and places in the code (Jakub): primary+p joins a
phrase of the draft to one or more selections in the sights, both framed in the text's colour.
Two ways: the phrase selected first, then the code (every selection since), primary+p in the
sights; or the code first, then the phrase, primary+p on the bench (the code's last selection).
The guide gets the phrase as <here at="(c):34-36 (d):12">the phrase</here>."""

import sublime




class Links:
    def __init__(self, reader):
        self.reader = reader
        self.phrase = None  # the draft's last selection (a Region of the bench)
        self.picks = []  # [(sight index, Region)]: the code's selections since then
        self.last = None  # the code's last selection or caret, (sight index, Region)
        self.links = []  # [(bench key, [(sight index, Region)])]
        self.sent = 0  # links before this one went out with a message
        self.quiet = False  # while it sets carets itself

    def note_bench(self, view):
        """A selection in the draft is the phrase to link; the code's selections count anew."""
        sel = view.sel()
        if len(sel) == 1 and not sel[0].empty() and sel[0].a >= self.draft_start(view):
            self.phrase, self.picks = sel[0], []

    def note_code(self, view, index):
        """Selections in a sight, all of them (several at once with primary+click): each is one
        more pick, or replaces a pick it overlaps (a drag growing it)."""
        if not len(view.sel()):
            return
        region = view.sel()[-1]
        self.last = (index, region if not region.empty() else view.line(region))
        for region in [r for r in view.sel() if not r.empty()]:
            same = [k for k, (i, r) in enumerate(self.picks) if i == index and r.intersects(region)]
            if same:
                self.picks[same[0]] = (index, region)
            else:
                self.picks.append((index, region))

    def link_from_code(self):
        """primary+p in the sights: the phrase selected on the bench joins every pick since."""
        if self.phrase is None or not self.picks:
            sublime.status_message("SightWalk: select words on the bench first, then code here.")
            return
        self.add(self.phrase, list(self.picks))
        self.phrase, self.picks = None, []

    def link_from_bench(self, view):
        """primary+p on the bench: the selected words (or the word at the caret) join the code's
        last selection."""
        if self.last is None:
            sublime.status_message("SightWalk: select code in the sights first.")
            return
        region = view.sel()[0] if len(view.sel()) else None
        if region is not None and region.empty():
            region = view.word(region)
        if region is None or region.empty() or region.a < self.draft_start(view):
            return
        self.add(region, [self.last])

    def add(self, phrase, places):
        """A link drawn: its words and its places framed, each link under keys of its own (one
        key for all would merge the frames of links that touch). The selections give way to a
        caret at each region's end, so the user sees it took (Jakub)."""
        key = "sight_walk_link_%d" % len(self.links)
        self.reader.chat.add_regions(key, [phrase], SCOPE, "", FLAGS)
        self.links.append((key, places))
        for index in set(i for i, _ in places):
            mine = [r for i, r in places if i == index]
            self.reader.sights[index].view.add_regions(key, mine, SCOPE, "", FLAGS)
        self.quiet = True  # the carets set here are no click into the link
        try:
            carets(self.reader.chat, [phrase])
            for index in set(i for i, _ in places):
                carets(self.reader.sights[index].view, [r for i, r in places if i == index])
        finally:
            self.quiet = False

    def tagged(self, view):
        """The draft with its links not yet sent as <here> tags, stripped as the bench sends it."""
        start = self.draft_start(view)
        text = view.substr(sublime.Region(start, view.size()))
        spans = []
        for key, places in self.links[self.sent:]:
            found = view.get_regions(key)
            if found and found[0].a >= start:
                spans.append((found[0].a - start, found[0].b - start, self.places(places)))
        for a, b, at in sorted(spans, reverse=True):
            text = text[:a] + '<here at="%s">%s</here>' % (at, text[a:b]) + text[b:]
        self.sent = len(self.links)
        return text.strip()

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
        """A click into linked words on the bench shows their first place in the code."""
        sel = view.sel()
        if self.quiet or len(sel) != 1 or not sel[0].empty():
            return
        for key, places in self.links:
            found = view.get_regions(key)
            if found and found[0].contains(sel[0].b) and places:
                for index in set(i for i, _ in places):  # the linked code selected (Jakub)
                    selected = self.reader.sights[index].view.sel()
                    selected.clear()
                    selected.add_all([r for i, r in places if i == index])
                index, region = places[0]
                self.reader.show_place(index, self.reader.sights[index].view.rowcol(region.a)[0] + 1)
                return

    def draft_start(self, view):
        """The draft starts after the protected transcript (see subl_chat)."""
        return len(PROTECTED.get(view.buffer_id(), ""))

    def clear(self):
        """Another trip: the links were to other sights."""
        for key, _ in self.links:
            self.reader.chat.erase_regions(key)
            for sight in self.reader.sights:
                sight.view.erase_regions(key)


def carets(view, regions):
    """The selections replaced by a caret at the end of each region."""
    selected = view.sel()
    selected.clear()
    selected.add_all([sublime.Region(r.end()) for r in regions])
