"""Sight specs ("file:begin-end") and how files are named to the user and the agent. No Sublime
API."""

import os

BAD_SPEC = 'Bad sight %r: write "file:begin-end" with 1 <= begin <= end, like "app.py:12-30".'


def parse_spec(spec, root=None):
    path, _, lines = str(spec).rpartition(":")
    begin, _, end = lines.partition("-")
    try:
        begin = int(begin)
        end = int(end) if end else begin
    except ValueError:
        raise ValueError(BAD_SPEC % spec) from None
    if not path or not 1 <= begin <= end:
        raise ValueError(BAD_SPEC % spec)
    path = os.path.expanduser(path)
    if root and not os.path.isabs(path):
        path = os.path.join(os.path.expanduser(root), path)
    return os.path.normpath(path), begin, end


def repo_root(path):
    folder = os.path.dirname(os.path.realpath(path))
    while True:
        if os.path.exists(os.path.join(folder, ".git")):
            return folder
        parent = os.path.dirname(folder)
        if parent == folder:
            return None
        folder = parent


def display_path(path):
    """The path as the agent and the user talk about it: relative to the repository root, or
    from the home folder when the file is in no repository."""
    root = repo_root(path)
    if root:
        return os.path.relpath(os.path.realpath(path), root)
    home = os.path.expanduser("~")
    return "~" + path[len(home):] if path.startswith(home + os.sep) else path


GREEK = ("alpha", "beta", "gamma", "delta", "epsilon", "zeta", "eta", "theta", "iota", "kappa",
         "lambda", "mu", "nu", "xi", "omicron", "pi", "rho", "sigma", "tau", "upsilon", "phi",
         "chi", "psi", "omega")


def sight_name(index):
    """A sight's name in its trip (Jakub): a Greek letter spelled out, in Latin letters, so the
    user can copy or type it; after omega the letters again with a number, "alpha 2"."""
    turn, letter = divmod(index, len(GREEK))
    return GREEK[letter] + (" %d" % (turn + 1) if turn else "")


def sight_index(name):
    """The index a sight's name stands for, or None."""
    parts = str(name).strip().lower().split()
    if not parts or parts[0] not in GREEK or len(parts) > 2:
        return None
    turn = int(parts[1]) - 1 if len(parts) == 2 and parts[1].isdigit() else 0
    return None if turn < 0 or (len(parts) == 2 and turn == 0) else \
        turn * len(GREEK) + GREEK.index(parts[0])


def sight_title(sight, index=None):
    """A sight's header: its name, then its file and lines, as given, without the blank lines
    shown around."""
    begin, end = sight.begin + sight.pad[0], sight.end - sight.pad[1]
    lines = str(begin) if begin == end else "%d-%d" % (begin, end)
    title = "%s:%s" % (display_path(sight.path), lines)
    return title if index is None else "%s · %s" % (sight_name(index), title)


def matches(sight, name):
    # A suffix counts only at a path separator, so "der.py" does not match "reader.py".
    name = os.path.normpath(name)
    return (sight.spec == name
            or sight.path == name
            or sight.path.endswith(os.sep + name))


def indent(line):
    return len(line) - len(line.lstrip())


def opens_block(text, keywords):
    """The line starts one of the keywords' blocks ("async def" counts as def)."""
    words = text.split()
    if words[:1] == ["async"]:
        words = words[1:]
    head = words[0].split("(")[0].rstrip(":") if words else ""
    return head in keywords


def ancestors(lines, begin, keywords):
    """1-based numbers of the lines that open the blocks around line begin, outermost first, by
    indentation: going up, every line indented less than the last found narrows the search, and
    those that start one of the keywords' blocks (setting frozen_parents) are kept (Jakub)."""
    limit = indent(lines[begin - 1])
    found = []
    for number in range(begin - 1, 0, -1):
        text = lines[number - 1]
        if not text.strip() or indent(text) >= limit:
            continue
        limit = indent(text)
        if opens_block(text.strip(), keywords):
            found.append(number)
        if limit == 0:
            break
    return found[::-1]


def breathing(lines, begin, end):
    """The range with the blank line just above and just below it, where there is one: a function
    set apart by blank lines shows them, so it does not look cramped (Jakub)."""
    if begin > 1 and not lines[begin - 2].strip():
        begin -= 1
    if end < len(lines) and not lines[end].strip():
        end += 1
    return begin, end
