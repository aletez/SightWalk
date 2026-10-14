"""SightWalk's ontology (Jakub, see DECISIONS.md): sights, trips, informators and holidays, the
places in them and the transitions between places. Pure, no Sublime API: the Sublime side holds
these objects (composition), it does not inherit from them."""

import re

TYPES = ("calls", "returns", "leads_to", "101s", "passes_data", "comparable", "own_trip")
INFORMATOR_ONLY = ("own_trip",)
KINDS = ("run", "comparison", "survey")


def slug(name):
    """An id from a name: "One tool call over HTTP" → "one-tool-call-over-http"."""
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


class Collection:
    """Members one level down, without order. A place in it is a path of member keys, of any
    length from 0 (the collection itself)."""

    def __init__(self, members):
        self.members = list(members)

    def member(self, key):
        """The member a key names, or None."""
        return None

    def has_place(self, path):
        if not path:
            return True
        found = self.member(path[0])
        if found is None:
            return False
        return len(path) == 1 or (isinstance(found, Collection) and found.has_place(path[1:]))


class Sequence(Collection):
    """A collection whose members come in order: one can walk it. Its members' keys are their
    indices."""

    def __iter__(self):
        return iter(self.members)

    def __len__(self):
        return len(self.members)

    def member(self, key):
        ok = isinstance(key, int) and 0 <= key < len(self.members)
        return self.members[key] if ok else None


class Transition:
    """A typed arrow from a source place to a target place. It reads as a sentence whose
    predicate is true of the source: "source calls target"."""

    def __init__(self, type, source, target):
        self.type, self.source, self.target = type, tuple(source), tuple(target)

    def __eq__(self, other):
        return isinstance(other, Transition) and self.parts() == other.parts()

    def __repr__(self):
        return "Transition%r" % (self.parts(),)

    def parts(self):
        return self.type, self.source, self.target


class Network(Collection):
    """A collection with a bag of transitions between its places. Self-contained: it knows only
    itself and its members. Its lines are those of one commit."""

    def __init__(self, name, members, transitions=(), commit=None):
        super().__init__(members)
        self.name, self.id, self.commit = name, slug(name), commit
        self.transitions = []
        for transition in transitions:
            self.add(transition)

    def add(self, transition):
        """Adds a transition after checking it; ValueError says what is wrong."""
        problem = self.problem(transition)
        if problem:
            raise ValueError("%s: %s" % (self.name, problem))
        self.transitions.append(transition)

    def problem(self, transition):
        if transition.type not in TYPES:
            return "unknown transition type %r (types: %s)" % (transition.type, ", ".join(TYPES))
        if transition.type in INFORMATOR_ONLY and not isinstance(self, Informator):
            return "%s belongs to an informator, not a trip" % transition.type
        for end in ("source", "target"):
            if not self.has_place(getattr(transition, end)):
                return "the %s %r is no place in it" % (end, getattr(transition, end))
        return None


class Sight(Sequence):
    """A range of a file's lines, in order. Its members' keys are the line numbers."""

    def __init__(self, file, begin, end):
        super().__init__(range(begin, end + 1))
        self.file, self.begin, self.end = file, begin, end

    @classmethod
    def parse(cls, spec):
        """A sight from "file:begin-end"."""
        found = re.match(r"^(.+):(\d+)-(\d+)$", spec)
        if not found or int(found.group(2)) > int(found.group(3)):
            raise ValueError("%r is no sight: write file:begin-end" % spec)
        return cls(found.group(1), int(found.group(2)), int(found.group(3)))

    @property
    def spec(self):
        return "%s:%d-%d" % (self.file, self.begin, self.end)

    def member(self, key):
        return key if isinstance(key, int) and self.begin <= key <= self.end else None


class Trip(Sequence, Network):
    """A sequence of sights chosen for one question, and a network of transitions between them:
    a place is ⟨⟩, ⟨sight⟩ or ⟨sight, line⟩, a sight by its index."""

    def __init__(self, name, sights, transitions=(), commit=None, kind="run"):
        if kind not in KINDS:
            raise ValueError("%s: unknown kind %r (kinds: %s)" % (name, kind, ", ".join(KINDS)))
        self.kind = kind
        Network.__init__(self, name, sights, transitions, commit)


class Informator(Network):
    """A network of trips, without order: a place is ⟨⟩, ⟨trip⟩, ⟨trip, sight⟩ or
    ⟨trip, sight, line⟩, a trip by its id."""

    def member(self, key):
        return next((trip for trip in self.members if trip.id == key), None)


class Holiday(Sequence):
    """One informator's trips in one order, laid out by the transition types it follows."""

    def __init__(self, informator, trips, types=("leads_to",)):
        stray = [trip.id for trip in trips if informator.member(trip.id) is not trip]
        if stray:
            raise ValueError("not in %s: %s" % (informator.name, ", ".join(stray)))
        super().__init__(trips)
        self.informator, self.types = informator, tuple(types)
