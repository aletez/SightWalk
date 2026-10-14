"""SightWalk's ontology (Jakub, see DECISIONS.md): sights, trips, informators and tours, the
places in them and the transitions between places. Pure, no Sublime API: the Sublime side holds
these objects (composition), it does not inherit from them."""

import json
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
        return self.place_problem(path) is None

    def place_problem(self, path):
        """Why path is no place in the collection, or None if it is one."""
        if not path:
            return None
        found = self.member(path[0])
        if found is None:
            return "%s is not in %s" % (self.member_label(path[0]), self.label())
        if len(path) == 1:
            return None
        if not isinstance(found, Collection):
            return "%s has nothing inside" % self.member_label(path[0])
        why = found.place_problem(path[1:])
        return why and "%s: %s" % (self.member_label(path[0]), why)

    def label(self):
        """How a message names the collection."""
        return "it"

    def member_label(self, key):
        return repr(key)


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
        problems = [self.problem(t) for t in transitions]
        if any(problems):
            raise ValueError("%s: %s." % (self.name, "; ".join(p for p in problems if p)))
        self.transitions = list(transitions)

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
            why = self.place_problem(getattr(transition, end))
            if why:
                return "%s %s → %s: the %s: %s" % (
                    transition.type, list(transition.source), list(transition.target), end, why)
        return None


class Sight(Sequence):
    """A range of a file's lines, in order. Its members' keys are the line numbers."""

    def __init__(self, file, begin, end):
        super().__init__(range(begin, end + 1))
        self.file, self.begin, self.end = file, begin, end

    @classmethod
    def parse(cls, spec):
        """A sight from "file:begin-end", or "file:line" for one line."""
        found = re.match(r"^(.+):(\d+)(?:-(\d+))?$", str(spec))
        begin, end = (int(found.group(2)), int(found.group(3) or found.group(2))) if found \
            else (0, 0)
        if not found or not 1 <= begin <= end:
            raise ValueError("%r is no sight: write file:begin-end" % spec)
        return cls(found.group(1), begin, end)

    @property
    def spec(self):
        return "%s:%d-%d" % (self.file, self.begin, self.end)

    def member(self, key):
        return key if isinstance(key, int) and self.begin <= key <= self.end else None

    def label(self):
        return self.spec

    def member_label(self, key):
        return "line %r" % (key,)


class Trip(Sequence, Network):
    """A sequence of sights chosen for one question, and a network of transitions between them:
    a place is ⟨⟩, ⟨sight⟩ or ⟨sight, line⟩, a sight by its index."""

    def __init__(self, name, sights, transitions=(), commit=None, kind="run"):
        if kind not in KINDS:
            raise ValueError("%s: unknown kind %r (kinds: %s)" % (name, kind, ", ".join(KINDS)))
        self.kind = kind
        Network.__init__(self, name, sights, transitions, commit)

    def label(self):
        return "the trip (sights 0 to %d)" % (len(self) - 1)

    def member_label(self, key):
        return "sight %r" % (key,)

    def moved(self, sights):
        """The same trip over sights at new ranges (an edit moved them), keeping the transitions
        that still fit."""
        trip = Trip(self.name, sights, commit=self.commit, kind=self.kind)
        trip.transitions = [t for t in self.transitions if not trip.problem(t)]
        return trip


class Informator(Network):
    """A network of trips, without order: a place is ⟨⟩, ⟨trip⟩, ⟨trip, sight⟩ or
    ⟨trip, sight, line⟩, a trip by its id. It keeps each trip's conversation (transcripts:
    {trip id: text}), so a walk goes on where it stopped (Jakub)."""

    def __init__(self, name, members, transitions=(), commit=None, transcripts=None):
        super().__init__(name, members, transitions, commit)
        self.transcripts = dict(transcripts or {})

    def member(self, key):
        return next((trip for trip in self.members if trip.id == key), None)

    def label(self):
        return "the informator " + self.name

    def member_label(self, key):
        return "trip %r" % (key,)


class Tour(Sequence):
    """One informator's trips in one order (Polish: turnus): laid out from the informator by the
    transition types it follows, or chosen and ordered by an author under a name (types ())."""

    def __init__(self, informator, trips, types=("leads_to",), name=None):
        stray = [trip.id for trip in trips if informator.member(trip.id) is not trip]
        if stray:
            raise ValueError("not in %s: %s" % (informator.name, ", ".join(stray)))
        super().__init__(trips)
        self.informator, self.types = informator, tuple(types)
        self.name = name or "%s: all trips" % informator.name


def tour(informator, types=("leads_to", "101s")):
    """The informator's trips in one order (Jakub): from each trip nothing leads to, on along
    leads_to, depth first; a trip a 101s transition names comes before the trip that needs it.
    Trips left over follow in the informator's order."""
    nexts, needs = {}, {}
    for t in informator.transitions:
        if t.type in types and t.source and t.target and t.source[0] != t.target[0]:
            table = needs if t.type == "101s" else nexts
            table.setdefault(t.source[0], []).append(t.target[0])
    reached = {target for targets in nexts.values() for target in targets}
    order = []
    for trip in sorted(informator.members, key=lambda trip: trip.id in reached):
        visit(trip.id, nexts, needs, order, set())
    return Tour(informator, [informator.member(key) for key in order], types)


def visit(key, nexts, needs, order, seen):
    if key in order or key in seen:
        return
    seen.add(key)
    for need in needs.get(key, []):
        visit(need, nexts, needs, order, seen)
    order.append(key)
    for target in nexts.get(key, []):
        visit(target, nexts, needs, order, seen)


# Files: a trip and an informator as JSON-ready data. An informator names its trips' files, so
# a trip stays self-contained and can serve several informators.

def transition_data(transition):
    return {"type": transition.type, "from": list(transition.source),
            "to": list(transition.target)}


def transition_from(data):
    return Transition(data.get("type"), data.get("from") or (), data.get("to") or ())


def trip_data(trip):
    return {"name": trip.name, "kind": trip.kind, "commit": trip.commit,
            "sights": [sight.spec for sight in trip],
            "transitions": [transition_data(t) for t in trip.transitions]}


def trip_from(data):
    return Trip(data["name"], [Sight.parse(spec) for spec in data["sights"]],
                [transition_from(t) for t in data.get("transitions", [])],
                data.get("commit"), data.get("kind", "run"))


def informator_data(informator, files):
    """files: {trip id: the trip's file, relative to the informator's}."""
    data = {"name": informator.name, "commit": informator.commit,
            "trips": [files[trip.id] for trip in informator.members],
            "transitions": [transition_data(t) for t in informator.transitions]}
    if informator.transcripts:
        data["transcripts"] = informator.transcripts
    return data


def informator_from(data, read_trip):
    """read_trip(file) gives a trip's data."""
    trips = [trip_from(read_trip(file)) for file in data["trips"]]
    return Informator(data["name"], trips, [transition_from(t) for t in data["transitions"]],
                      data.get("commit"), data.get("transcripts"))


def dumps(data):
    """JSON for a trip's or an informator's file: indented, each place on one line, [3, 42]."""
    text = json.dumps(data, indent=1, ensure_ascii=False)
    return re.sub(r"\[\s*([^\[\]{}\"]*?)\s*\]",
                  lambda m: "[%s]" % re.sub(r",\s+", ", ", m.group(1)), text) + "\n"


def tour_data(tour, informator_file):
    """An author's tour: its name, its informator's file (relative to the tour's) and its
    trips' ids in order."""
    return {"name": tour.name, "informator": informator_file,
            "trips": [trip.id for trip in tour]}


def tour_from(data, informator):
    missing = [key for key in data["trips"] if informator.member(key) is None]
    if missing:
        raise ValueError("%s: no such trips in %s: %s" % (data["name"], informator.name,
                                                         ", ".join(missing)))
    return Tour(informator, [informator.member(key) for key in data["trips"]], (),
                   data["name"])
