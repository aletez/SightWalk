import unittest

from sw.ontology import Holiday, Informator, Sight, Transition, Trip, slug


def two_sights():
    return [Sight.parse("sw/a.py:10-20"), Sight.parse("sw/b.py:5-9")]


class SightTest(unittest.TestCase):
    def test_parse_and_spec(self):
        sight = Sight.parse("sw/a.py:10-20")
        self.assertEqual((sight.file, sight.begin, sight.end), ("sw/a.py", 10, 20))
        self.assertEqual(sight.spec, "sw/a.py:10-20")
        self.assertEqual(len(sight), 11)

    def test_one_line(self):
        self.assertEqual(Sight.parse("sw/a.py:7").spec, "sw/a.py:7-7")

    def test_bad_specs(self):
        for spec in ("sw/a.py", "sw/a.py:20-10", "sw/a.py:x-3", "sw/a.py:0-3"):
            with self.assertRaises(ValueError):
                Sight.parse(spec)

    def test_places_are_its_lines(self):
        sight = Sight.parse("sw/a.py:10-20")
        self.assertTrue(sight.has_place(()))
        self.assertTrue(sight.has_place((10,)))
        self.assertFalse(sight.has_place((21,)))
        self.assertFalse(sight.has_place((10, 1)))


class TripTest(unittest.TestCase):
    def test_id_from_name(self):
        self.assertEqual(slug("One tool call over HTTP"), "one-tool-call-over-http")
        self.assertEqual(Trip("A request arrives", two_sights()).id, "a-request-arrives")

    def test_places(self):
        trip = Trip("t", two_sights())
        for place in [(), (0,), (1,), (0, 15), (1, 9)]:
            self.assertTrue(trip.has_place(place), place)
        for place in [(2,), (0, 9), (1, 10), ("0",)]:
            self.assertFalse(trip.has_place(place), place)

    def test_calls_between_its_sights(self):
        call = Transition("calls", (0, 12), (1, 5))
        trip = Trip("t", two_sights(), [call])
        self.assertEqual(trip.transitions, [call])

    def test_refuses_wrong_transitions(self):
        for wrong in [Transition("call", (0, 12), (1, 5)),
                      Transition("calls", (0, 30), (1, 5)),
                      Transition("calls", (0, 12), (2, 5)),
                      Transition("own_trip", (0, 10), ())]:
            with self.assertRaises(ValueError):
                Trip("t", two_sights(), [wrong])

    def test_all_problems_in_one_message(self):
        with self.assertRaises(ValueError) as caught:
            Trip("t", two_sights(), [Transition("calls", (0, 30), (1, 5)),
                                     Transition("calls", (0, 12), (1, 50))])
        self.assertIn("source", str(caught.exception))
        self.assertIn("target", str(caught.exception))

    def test_messages_name_the_wrong_part(self):
        trip = Trip("t", two_sights())
        self.assertEqual(trip.place_problem((0, 99)), "sight 0: line 99 is not in sw/a.py:10-20")
        self.assertEqual(trip.place_problem((2, 5)), "sight 2 is not in the trip (sights 0 to 1)")
        problem = trip.problem(Transition("calls", (0, 12), (1, 50)))
        self.assertEqual(problem, "calls [0, 12] → [1, 50]: the target: sight 1: line 50 is not "
                                  "in sw/b.py:5-9")

    def test_moved_keeps_what_fits(self):
        fits, lost = Transition("calls", (0, 12), (1, 5)), Transition("calls", (0, 19), (1, 9))
        trip = Trip("t", two_sights(), [fits, lost], commit="c", kind="survey")
        moved = trip.moved([Sight.parse("sw/a.py:10-18"), Sight.parse("sw/b.py:5-9")])
        self.assertEqual((moved.name, moved.commit, moved.kind), ("t", "c", "survey"))
        self.assertEqual(moved.transitions, [fits])

    def test_kinds(self):
        self.assertEqual(Trip("t", two_sights(), kind="survey").kind, "survey")
        with self.assertRaises(ValueError):
            Trip("t", two_sights(), kind="tour")

    def test_is_a_sequence_of_sights(self):
        sights = two_sights()
        self.assertEqual(list(Trip("t", sights)), sights)


class InformatorTest(unittest.TestCase):
    def informator(self, transitions=()):
        first = Trip("First", two_sights())
        second = Trip("Second", [Sight.parse("sw/c.py:1-30")])
        return Informator("SightWalk", [first, second], transitions, commit="abc123")

    def test_places_go_through_trips(self):
        informator = self.informator()
        for place in [(), ("first",), ("first", 1), ("second", 0, 30)]:
            self.assertTrue(informator.has_place(place), place)
        for place in [("third",), ("first", 2), ("second", 0, 31), (0,)]:
            self.assertFalse(informator.has_place(place), place)

    def test_transitions_between_trips_and_own_trip(self):
        leads = Transition("leads_to", ("first", 1, 9), ("second", 0, 1))
        own = Transition("own_trip", ("first", 0, 10), ("second",))
        informator = self.informator([leads, own])
        self.assertEqual(informator.transitions, [leads, own])
        self.assertEqual(informator.commit, "abc123")

    def test_refuses_a_place_outside(self):
        with self.assertRaises(ValueError):
            self.informator([Transition("calls", ("first", 0, 12), ("third", 0, 1))])


class HolidayTest(unittest.TestCase):
    def test_trips_of_its_informator_in_order(self):
        first, second = Trip("First", two_sights()), Trip("Second", two_sights())
        informator = Informator("SightWalk", [first, second])
        holiday = Holiday(informator, [second, first])
        self.assertEqual(list(holiday), [second, first])
        self.assertEqual(holiday.types, ("leads_to",))

    def test_refuses_a_stray_trip(self):
        informator = Informator("SightWalk", [Trip("First", two_sights())])
        with self.assertRaises(ValueError):
            Holiday(informator, [Trip("Other", two_sights())])


if __name__ == "__main__":
    unittest.main()
