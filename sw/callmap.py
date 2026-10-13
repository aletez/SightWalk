"""The Map tab's graph: the functions the trip's sights show, grouped by file and class, and an
arrow where one calls another (Jakub). A node is a definition: (sight, line). The arrows come from
the trip's author when the sights name their calls (<sight, line> calls <sight, line>), else they
are read statically with ast. Pure functions, no Sublime API; nothing runs."""

import ast
import re
import textwrap

DEF = re.compile(r"^\s*(?:async\s+)?def\s+(\w+)")


class Node:
    """A definition on the map: its key (sight index, line), the function's name, the class
    around it (or ""), its file as shown, its colour, the names its code calls (on, name), and
    the keys the trip's author says it calls (None when the author said nothing)."""

    def __init__(self, key, function, owner, file, colour, calls, authored=None):
        self.key, self.function, self.owner, self.file = key, function, owner, file
        self.colour, self.calls, self.authored = colour, calls, authored


def first_definition(lines, begin, end):
    """(line, name) of the first function defined in lines begin..end (1-based), or None."""
    for number in range(begin, end + 1):
        found = DEF.match(lines[number - 1]) if number <= len(lines) else None
        if found:
            return number, found.group(1)
    return None


def function_name(lines, begin, end):
    found = first_definition(lines, begin, end)
    return found[1] if found else None


def called_names(text):
    """What the code calls, as (on, name): on is "" for f(...), the name before the dot for
    self.f(...) or Class.f(...), and None when the call is on anything else (obj().f, a[0].f).
    Code that does not parse gives none."""
    try:
        tree = ast.parse(textwrap.dedent(text))
    except SyntaxError:
        return set()
    calls = set()
    for node in ast.walk(tree):
        func = getattr(node, "func", None) if isinstance(node, ast.Call) else None
        if isinstance(func, ast.Name):
            calls.add(("", func.id))
        elif isinstance(func, ast.Attribute):
            on = func.value.id if isinstance(func.value, ast.Name) else None
            calls.add((on, func.attr))
    return calls


def callees(caller, on, name, nodes):
    """The sights a call may reach (Jakub: by class, not by name alone): f() a function outside
    any class, self.f() and cls.f() the caller's own class, Class.f() that class; on another
    object, whose class is not known, any sight's f."""
    named = [n for n in nodes if n.function == name and n.key != caller.key]
    if on == "":
        return [n for n in named if not n.owner]
    if on in ("self", "cls"):
        return [n for n in named if n.owner == caller.owner]
    owned = [n for n in named if n.owner == on]
    return owned or ([] if on in {n.owner for n in nodes} else named)


def in_run_order(caller, found):
    """Of several sights a call may reach, the one the trip shows next after the caller, as the
    guide lays sights out in the order of a run (Jakub); failing that, the nearest before it."""
    after = [n for n in found if n.key > caller.key]
    if after:
        return min(after, key=lambda n: n.key)
    return max(found, key=lambda n: n.key) if found else None


def edges(nodes):
    """(caller key, callee key): as the trip's author names them, else read from the code."""
    pairs = set()
    for n in nodes:
        if n.authored is not None:
            pairs.update((n.key, key) for key in n.authored)
            continue
        for on, name in n.calls:
            callee = in_run_order(n, callees(n, on, name, nodes))
            if callee is not None:
                pairs.add((n.key, callee.key))
    return sorted(pairs)


def authored_calls(definitions, calls):
    """{caller key: [callee keys]} from a sight's calls [(line, (sight, line))]: each call belongs
    to the last of the sight's definitions (lines) at or above it, else to the first."""
    found = {line: [] for line in definitions}
    for line, target in calls:
        above = [d for d in definitions if d <= line]
        found[max(above) if above else min(definitions)].append(target)
    return found


def node_id(key):
    return quote("s%d_%d" % key)


def quote(text):
    return '"%s"' % text.replace("\\", "\\\\").replace('"', '\\"')


def cluster(name, label, body, indent):
    pad = "  " * indent
    return ["%ssubgraph %s {" % (pad, quote("cluster_" + name)),
            "%s  label=%s;" % (pad, quote(label))] + body + ["%s}" % pad]


def node_line(node, indent):
    return '%s%s [label=%s, fillcolor="%s"];' % ("  " * indent, node_id(node.key),
                                                 quote(node.function), node.colour)


def file_block(file, nodes):
    """A file's cluster, with a nested cluster per class."""
    body = [node_line(n, 2) for n in nodes if not n.owner]
    for owner in sorted({n.owner for n in nodes if n.owner}):
        mine = [node_line(n, 3) for n in nodes if n.owner == owner]
        body += cluster(file + "/" + owner, "class " + owner, mine, 2)
    return cluster(file, file, body, 1)


def dot_source(nodes, style):
    """The graph in Graphviz's dot language. style: (font, text colour, line colour)."""
    font, text, line = style
    lines = ["digraph map {", "  rankdir=LR;",
             '  graph [fontname=%s, fontcolor="%s", color="%s"];' % (quote(font), text, line),
             '  node [shape=box, style="rounded,filled", fontname=%s, fontcolor="%s", '
             'color="%s"];' % (quote(font), text, line),
             '  edge [color="%s"];' % line]
    for file in sorted({n.file for n in nodes}):
        lines += file_block(file, [n for n in nodes if n.file == file])
    lines += ["  %s -> %s;" % (node_id(a), node_id(b)) for a, b in edges(nodes)]
    return "\n".join(lines + guess_warning(nodes) + ["}"])


def guess_warning(nodes):
    """Under the map, when some arrows are guessed from the code: the trip named no calls for
    some sights (Jakub)."""
    guessed = [n for n in nodes if n.authored is None]
    if not guessed:
        return []
    text = ("Arrows guessed from names: the trip names no calls" if len(guessed) == len(nodes)
            else "Some arrows guessed from names: the trip names no calls for some sights")
    return ['  label=%s; labelloc="b"; fontcolor="#a0522d";' % quote("⚠ " + text)]
