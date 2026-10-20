"""A trip window's history, stepped through with ◀ and ▶ as in a browser (Jakub, 2026-10-20).
Each entry is a normal trip with its own conversation: its transcript and its answers' marks, as
they were when the user left it. Adventures take no place here."""


class History:
    def __init__(self):
        self.entries = []  # dicts: trip, root, transcript, marks
        self.at = -1

    def current(self):
        return self.entries[self.at] if 0 <= self.at < len(self.entries) else None

    def keep(self, transcript, marks):
        """The conversation of the trip shown, as the user leaves it."""
        entry = self.current()
        if entry is not None:
            entry["transcript"], entry["marks"] = transcript, marks

    def visit(self, trip, root, transcript=""):
        """A new trip after the one shown: the trips ahead of it are dropped, as in a browser."""
        del self.entries[self.at + 1:]
        self.entries.append({"trip": trip, "root": root, "transcript": transcript, "marks": None})
        self.at = len(self.entries) - 1
        return self.current()

    def can(self, step):
        return 0 <= self.at + step < len(self.entries)

    def go(self, step):
        """The entry step away (-1 back, 1 forward), or None when there is none."""
        if not self.can(step):
            return None
        self.at += step
        return self.current()


def last_exchange(transcript):
    """The user's last message and what followed it: the question a new trip's conversation
    starts from (Jakub)."""
    start = transcript.rfind("\n\nU: ")
    if start >= 0:
        return transcript[start + 2:]
    return transcript if transcript.startswith("U: ") else ""
