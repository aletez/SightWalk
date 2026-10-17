"""The user's links between words on the bench and places in the code (Jakub): primary+p joins a
phrase of the draft to one or more selections in the sights, both framed in the text's colour.
Two ways: the phrase selected first, then the code (every selection since), primary+p in the
sights; or the code first, then the phrase, primary+p on the bench (the code's last selection).
The guide gets the phrase as <here at="(c):34-36 (d):12">the phrase</here>."""

import sublime

from .spec import sight_name
from .subl_chat import PROTECTED

SCOPE = "sight_walk.link"  # no scheme names it: frames in the text's colour
FLAGS = sublime.DRAW_NO_FILL


class Links:
    def __init__(self, reader):
        self.reader = reader
        self.phrase = None  # the draft's last selection (a Region of the bench)
        self.picks = []  # [(sight index, Region)]: the code's selections since then
        self.last = None  # the code's last selection or caret, (sight index, Region)
        self.links = []  # [(bench key, [(sight index, Region)])]
        self.sent = 0  # links before this one went out with a message

    def note_bench(self, view):
        """A selection in the draft is the phrase to link; the code's selections count anew."""
        sel = view.sel()
        if len(sel) == 1 and not sel[0].empty() and sel[0].a >= self.draft_start(view):
            self.phrase, self.picks = sel[0], []

    def note_code(self, view, index):
        """A selection in a sight: one more pick (a drag in the same place replaces the last)."""
        if not len(view.sel()):
            return
        region = view.sel()[0]
        self.last = (index, region if not region.empty() else view.line(region))
        if region.empty():
            return
        if self.picks and self.picks[-1][0] == index and self.picks[-1][1].intersects(region):
            self.picks[-1] = (index, region)
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
        key = "sight_walk_link_%d" % len(self.links)
        self.reader.chat.add_regions(key, [phrase], SCOPE, "", FLAGS)
        self.links.append((key, places))
        self.draw_code()

    def draw_code(self):
        """Every linked place framed in its sight."""
        for index, sight in enumerate(self.reader.sights):
            regions = [r for _, places in self.links for i, r in places if i == index]
            sight.view.add_regions("sight_walk_links", regions, SCOPE, "", FLAGS)

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
        if len(sel) != 1 or not sel[0].empty():
            return
        for key, places in self.links:
            found = view.get_regions(key)
            if found and found[0].contains(sel[0].b) and places:
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
            sight.view.erase_regions("sight_walk_links")
