import unittest

from sw import validator
from sw.validator import Refusal, check
from tests.test_pure import stacked

OPEN = {"trip_open": True, "ready": True, "addressed": True}


class SayTest(unittest.TestCase):
    def test_refusals(self):
        for facts, text in [({}, "Hi"), (dict(OPEN, addressed=False), "Hi"),
                            (dict(OPEN, stopped=True), "Hi"), (OPEN, "`run` does it"),
                            (OPEN, "<func>run</func> does it"),
                            (dict(OPEN, pointed=True), "w linii 33 jest return")]:
            with self.assertRaises(Refusal, msg=text):
                check("say", {"text": text}, facts)

    def test_passes(self):
        check("say", {"text": "Yes."}, OPEN)
        check("say", {"text": "<func>run</func> at 1 reads it."}, dict(OPEN, pointed=True))


class ShowTest(unittest.TestCase):
    def test_files(self):
        args = {"sights": ["a.py:1-5"], "transitions": [], "trip": "T"}
        check("show", args, {"files": [("a.py:1-5", "/r/a.py", 10, 5)]})
        for files in ([("a.py:1-5", "/r/a.py", None, 5)], [("a.py:1-5", "/r/a.py", 3, 5)], []):
            with self.assertRaises(Refusal):
                check("show", args, {"files": files})

    def test_places_by_name(self):
        trip = validator.trip_of({"trip": "T", "sights": ["a.py:1-5", "b.py:1-9"], "transitions": [
            {"type": "calls", "from": "(a):3", "to": "(b):1"},
            {"type": "leads_to", "from": "(a)", "to": [1, 2]}]})
        self.assertEqual([(t.source, t.target) for t in trip.transitions],
                         [((0, 3), (1, 1)), ((0,), (1, 2))])
        for bad in ("x1:3", "(q):1", "(a):x"):
            with self.assertRaises(Refusal, msg=bad):
                validator.trip_of({"trip": "T", "sights": ["a.py:1-5"], "transitions": [
                    {"type": "calls", "from": bad, "to": "(a):1"}]})

    def test_name_and_hint(self):
        with self.assertRaises(Refusal):  # no name
            validator.trip_of({"sights": ["a.py:1-5"], "transitions": []})
        with self.assertRaises(Refusal) as caught:  # an absolute path: no hint about root
            check("show", {"sights": ["/r/a.py:1-5"], "transitions": [], "trip": "T"},
                  {"files": [("/r/a.py:1-5", "/r/a.py", None, 5)]})
        self.assertNotIn("root", str(caught.exception))

    def test_one_unit(self):
        args = {"sights": ["a.py:1-9"], "transitions": [], "trip": "T"}
        files = [("a.py:1-9", "/r/a.py", 20, 9)]
        check("show", args, {"files": files, "functions": [("a.py:1-9", ["m"], ["A"])]})
        with self.assertRaises(Refusal):
            check("show", args, {"files": files, "functions": [("a.py:1-9", ["m"], ["A", "B"])]})

    def test_shape(self):
        for args in ({"sights": "a.py:1-5", "transitions": []}, {"sights": ["a.py:1-5"]},
                     {"sights": ["a.py"], "transitions": []}):
            with self.assertRaises(Refusal):
                validator.trip_of(args)


class MarksAndSettingsTest(unittest.TestCase):
    def test_icon_after_the_word_line(self):
        sights, _ = stacked((1, 3), (10, 11))
        check("say", {"text": 'Ta linia <here at="(a):2" icon="1">1</here> czyta token.'},
              dict(OPEN, sights=sights))

    def test_marks_in_the_answer(self):
        sights, _ = stacked((1, 3), (10, 11))
        facts = dict(OPEN, sights=sights)
        check("say", {"text": '<func>run</func> starts at <here at="(a):2" icon="1">1</here>, '
                              'then <calls at="(a):3 (b):10">calls</calls>.'}, facts)
        for text in ['<func>run</func> at <here at="(a):9" icon="1">1</here>.',  # outside
                     '<func>run</func> at <here at="a.py:2" icon="1">1</here>.',  # no sight's name
                     '<func>run</func> at <here at="(a):2" icon="7a">1</here>.',  # no icon
                     '<func>run</func> <calls at="(b):10">calls</calls>.',
                     '<func>run</func> at <icon at="(a):2">1</icon>.',  # the old markup
                     # three marks on line 3: an icon, a jump's start and another's end
                     '<here at="(a):3" icon="1">1</here> <calls at="(a):3 (b):10">calls</calls> '
                     '<returns at="(b):11 (a):3">back</returns>']:
            with self.assertRaises(Refusal, msg=text):
                check("say", {"text": text}, facts)

    def test_settings(self):
        check("settings", {"values": {"tint": 0.3, "bench_side": "left"}}, {})
        for values in ({"tint": 2}, {"bench_side": "up"}, {"font": 1}):
            with self.assertRaises(Refusal):
                check("settings", {"values": values}, {})


if __name__ == "__main__":
    unittest.main()
