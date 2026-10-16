"""Sight specs ("file:begin-end") and how files are named to the user and the agent. No Sublime
API."""

import os
import re

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


LETTERS = "abcdefghijklmnopqrstuvwxyz"


def sight_name(index):
    """A sight's name in its trip (Jakub): a small letter in parentheses, "(c)", which the user
    finds by the alphabet and quotes easily ("and (c)?"); after (z) the letters again with a
    number, "(a2)". Icons in the gutter use capitals, so the two never meet."""
    turn, letter = divmod(index, len(LETTERS))
    return "(%s%s)" % (LETTERS[letter], turn + 1 if turn else "")


def sight_index(name):
    """The index a sight's name stands for, "(c)", "c)" or "c", or None."""
    found = re.match(r"^\(?([a-z])(\d*)\)?$", str(name).strip())
    if not found or found.group(2) in ("0", "1") or found.group(2).startswith("0"):
        return None
    turn = int(found.group(2)) - 1 if found.group(2) else 0
    return turn * len(LETTERS) + LETTERS.index(found.group(1))


def sight_title(sight, index=None, width=0):
    """A sight's header: its name, padded to width so the files stand in one column (Jakub), then
    its file and lines, as given, without the blank lines shown around."""
    begin, end = sight.begin + sight.pad[0], sight.end - sight.pad[1]
    lines = str(begin) if begin == end else "%d-%d" % (begin, end)
    title = "%s:%s" % (display_path(sight.path), lines)
    return title if index is None else "%s %s" % (sight_name(index).ljust(width), title)


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


FUNCTION = re.compile(r"^\s*(?:async\s+)?def\s+(\w+)")


def functions_in(lines, begin, end):
    """The functions whose definitions stand in lines begin..end, not counting those defined
    inside another of them: a sight holds one at most (Jakub)."""
    found, open_indent = [], None
    for text in lines[begin - 1:end]:
        if not text.strip():
            continue
        if open_indent is not None and indent(text) <= open_indent:
            open_indent = None
        match = FUNCTION.match(text)
        if match and open_indent is None:
            found.append(match.group(1))
            open_indent = indent(text)
    return found


def elided(lines, begin, end, frozen):
    """(above, below): how many lines of the innermost frozen block are left out between its
    opening line and the range, and after the range up to the block's last line (Jakub: a sight
    may be a fragment of a function)."""
    if not frozen:
        return 0, 0
    opening = frozen[-1]
    above = begin - 1 - opening
    last = end
    for number in range(end + 1, len(lines) + 1):
        text = lines[number - 1]
        if text.strip():
            if indent(text) <= indent(lines[opening - 1]):
                break
            last = number
    return max(above, 0), last - end


def body_indent(lines, frozen):
    """The indentation of the innermost frozen block's body, in characters, or 0."""
    if not frozen:
        return 0
    for text in lines[frozen[-1]:]:
        if text.strip():
            return indent(text)
    return 0


def block_name(lines, frozen):
    """The name the innermost frozen block defines ("run", "Reader"), or ""."""
    found = re.match(r"^\s*(?:async\s+)?(?:def|class)\s+(\w+)", lines[frozen[-1] - 1]) \
        if frozen else None
    return found.group(1) if found else ""


def breathing(lines, begin, end):
    """The range with the blank line just above and just below it, where there is one: a function
    set apart by blank lines shows them, so it does not look cramped (Jakub)."""
    if begin > 1 and not lines[begin - 2].strip():
        begin -= 1
    if end < len(lines) and not lines[end].strip():
        end += 1
    return begin, end
