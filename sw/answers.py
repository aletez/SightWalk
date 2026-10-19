"""The Answers tab's rows (Jakub): every question of the user's and answer of the guide's on
the bench, in order, by its first words. Pure."""

import re

LABEL = re.compile(r"(?m)^([UA]): ")


def entries(transcript, words=8):
    """[(kind "U" or "A", the label's offset in the transcript, its first words)]."""
    found = []
    for match in LABEL.finditer(transcript):
        rest = transcript[match.end():]
        end = LABEL.search(rest)
        text = " ".join(rest[:end.start() if end else len(rest)].split())
        first = text.split(" ")
        found.append((match.group(1), match.start(),
                      " ".join(first[:words]) + (" …" if len(first) > words else "")))
    return found
