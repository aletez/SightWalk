"""The Map tab's graph: the functions the trip's sights show, grouped by file and class, and an
arrow where one calls another (Jakub). A node is a definition: (sight, line). The arrows are the
calls the trip's author names, <sight, line> calls <sight, line>; nothing is guessed (Jakub).
Pure functions, no Sublime API."""

import re

DEF = re.compile(r"^\s*(?:async\s+)?def\s+(\w+)")


class Node:
    """A definition on the map: its key (sight index, line), the function's name, the class
    around it (or ""), its file as shown, its colour and the keys the trip's author says it
    calls."""

    def __init__(self, key, function, owner, file, colour, calls):
        self.key, self.function, self.owner, self.file = key, function, owner, file
        self.colour, self.calls = colour, calls


def first_definition(lines, begin, end):
    """(line, name) of the first function defined in lines begin..end (1-based), or None."""
    for number in range(begin, end + 1):
        found = DEF.match(lines[number - 1]) if number <= len(lines) else None
        if found:
            return number, found.group(1)
    return None


def edges(nodes):
    """(caller key, callee key) for each call the trip's author names."""
    return sorted({(n.key, key) for n in nodes for key in n.calls})


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
    return "\n".join(lines + ["}"])

