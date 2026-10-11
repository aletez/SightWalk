"""Questions the code already asks (Jakub): every guard is a question its author once asked, such
as "is this window still valid?" or "is this view None?". Where the same kind of object is used
without that question, a trip shows where the code does ask it. Found in the code itself, on the
dry, without a model. Pure functions, no Sublime API.

A question is (subject, predicate): the subject is the last name of the guarded expression
(self.window and reader.window are both "window"), the predicate how it is asked: whether the
thing still exists (is_valid and the like) or is there at all ("is None"). Only stored
references are checked (self.window, reader.chat): they are what goes stale between calls."""

import ast

NONE = "is None"
ALIVE = ("is_valid", "is_alive", "exists", "is_closed")
MODULES = ("os", "sys", "sublime", "shutil", "time", "json")
HABIT = 2  # a question counts once the code asks it in this many places


def subject(node):
    """The last name of an expression: window for self.window, view for seg.view. None for a
    module's name (os.path), which is no object that could go stale."""
    root = node
    while isinstance(root, ast.Attribute):
        root = root.value
    if isinstance(root, ast.Name) and root.id in MODULES:
        return None
    if isinstance(node, ast.Attribute):
        return node.attr
    if isinstance(node, ast.Name):
        return node.id
    return None


def asked_in(test):
    """The questions in a condition: (subject, predicate) pairs."""
    found = set()
    for node in ast.walk(test):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
            if node.func.attr in ALIVE and subject(node.func.value):
                found.add((subject(node.func.value), node.func.attr))
        elif isinstance(node, ast.Compare) and isinstance(node.ops[0], (ast.Is, ast.IsNot)):
            if isinstance(node.comparators[0], ast.Constant) and node.comparators[0].value is None:
                if subject(node.left):
                    found.add((subject(node.left), NONE))
    return found


def conditions(tree):
    """Every condition in a tree: ifs, whiles, asserts, conditional expressions, comprehension
    filters."""
    for node in ast.walk(tree):
        if isinstance(node, (ast.If, ast.While, ast.IfExp, ast.Assert)):
            yield node.test
        elif isinstance(node, ast.comprehension):
            yield from node.ifs


def functions(tree):
    return [n for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]


def catalogue(sources):
    """{question: [(path, line, function, text)]} for every question the sources, {path: text},
    ask in at least HABIT places: a habit of the code, not a one-off."""
    found = {}
    for path, text in sources.items():
        try:
            tree = ast.parse(text)
        except SyntaxError:
            continue
        lines = text.splitlines()
        for fn in functions(tree):
            for test in conditions(fn):
                for question in asked_in(test):
                    where = (path, test.lineno, fn.name, lines[test.lineno - 1].strip())
                    found.setdefault(question, []).append(where)
    return {q: places for q, places in found.items() if len(places) >= HABIT}


def uses(fn):
    """The first use, per stored subject, of its attribute in a function: {subject: node}. A
    stored subject is itself an attribute (self.window), not a fresh local."""
    first = {}
    for node in ast.walk(fn):
        if isinstance(node, ast.Attribute) and isinstance(node.value, ast.Attribute):
            name = subject(node.value)
            if name not in first or node.lineno < first[name].lineno:
                first[name] = node.value
    return first


def unasked(text, begin, end, known):
    """Places in lines begin..end of text where a stored subject is used without a question the
    code asks about it elsewhere: [(line, start column, end column, [questions])], one per
    function and subject, at the subject's first use."""
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return []
    found = []
    for fn in functions(tree):
        if not begin <= fn.lineno <= end:
            continue
        asked = asked_in(fn)  # anywhere in it, a condition or a returned test
        for name, node in uses(fn).items():
            missing = sorted(q for q in known if q[0] == name and q not in asked)
            if missing:
                found.append((node.lineno, node.col_offset, node.end_col_offset, missing))
    return found
