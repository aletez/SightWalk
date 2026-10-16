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
        args = {"sights": ["a.py:1-5"], "transitions": []}
        check("show", args, {"files": [("a.py:1-5", "/r/a.py", 10, 5)]})
        for files in ([("a.py:1-5", "/r/a.py", None, 5)], [("a.py:1-5", "/r/a.py", 3, 5)], []):
            with self.assertRaises(Refusal):
                check("show", args, {"files": files})

    def test_shape(self):
        for args in ({"sights": "a.py:1-5", "transitions": []}, {"sights": ["a.py:1-5"]},
                     {"sights": ["a.py"], "transitions": []}):
            with self.assertRaises(Refusal):
                validator.trip_of(args)


class PointAndSettingsTest(unittest.TestCase):
    def test_point(self):
        sights, _ = stacked((1, 3), (10, 11))
        facts = dict(OPEN, sights=sights)
        check("point", {"marks": [{"at": {"sight": "(b)", "line": 11}, "mark": "1"}]}, facts)
        with self.assertRaises(Refusal):
            check("point", {"marks": [{"at": "a.py:5"}]}, facts)
        with self.assertRaises(Refusal):
            check("point", {"marks": []}, dict(facts, ready=False))

    def test_settings(self):
        check("settings", {"values": {"tint": 0.3, "bench_side": "left"}}, {})
        for values in ({"tint": 2}, {"bench_side": "up"}, {"font": 1}):
            with self.assertRaises(Refusal):
                check("settings", {"values": values}, {})


if __name__ == "__main__":
    unittest.main()
