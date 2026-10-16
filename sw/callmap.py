"""The Map tab's graph: the functions the trip's sights show, grouped by file and class, and the
trip's transitions between them, each type drawn its own way, with a legend (Jakub). A node is a
definition: (sight, line). The arrows are the transitions the trip's author names; nothing is
guessed (Jakub). Pure functions, no Sublime API."""

import re

DEF = re.compile(r"^\s*(?:async\s+)?def\s+(\w+)")


# How each transition type is drawn (Jakub): told apart by line and head, as the nodes take
# their files' hues.
STYLES = {
    "calls": "",
    "returns": "style=dashed, arrowhead=vee",
    "leads_to": "penwidth=2.5",
    "101s": "style=dotted, arrowhead=diamond",
    "passes_data": 'color="#2C6ED5", arrowhead=dot',
    "comparable": "style=dotted, dir=none",
}


class Node:
    """A definition on the map: its key (sight index, line), the function's name (or the sight's
    lines, for top-level code), the class around it (or ""), its file as shown, its colour, and
    the sight's name ("beta") on the sight's main node only."""

    def __init__(self, key, function, owner, file, colour, name=""):
        self.key, self.function, self.owner, self.file = key, function, owner, file
        self.colour, self.name = colour, name


def first_definition(lines, begin, end):
    """(line, name) of the first function defined in lines begin..end (1-based), or None."""
    for number in range(begin, end + 1):
        found = DEF.match(lines[number - 1]) if number <= len(lines) else None
        if found:
            return number, found.group(1)
    return None


def node_at(definitions, place):
    """The node a place (sight, line) or (sight,) lies in: the last of the sight's definitions
    {sight: [lines]} at or above the line, else the sight's first."""
    mine = definitions.get(place[0])
    if not mine:
        return None
    above = [d for d in mine if len(place) > 1 and d <= place[1]]
    return place[0], max(above) if above else min(mine)


def edges(definitions, transitions):
    """(from key, to key, type) for every transition between two nodes."""
    found = set()
    for kind, source, target in transitions:
        a, b = node_at(definitions, source), node_at(definitions, target)
        if a and b and a != b and kind in STYLES:
            found.add((a, b, kind))
    return sorted(found)


def node_id(key):
    return quote("s%d_%d" % key)


def quote(text):
    return '"%s"' % text.replace("\\", "\\\\").replace('"', '\\"')


def cluster(name, label, body, indent):
    pad = "  " * indent
    return ["%ssubgraph %s {" % (pad, quote("cluster_" + name)),
            "%s  label=%s;" % (pad, quote(label))] + body + ["%s}" % pad]


def node_line(node, indent, faded):
    return '%s%s [label=%s, fillcolor="%s"];' % ("  " * indent, node_id(node.key),
                                                 node_label(node, faded), node.colour)


def node_label(node, faded):
    """The function, under the sight's name small and faded (Jakub), as an HTML-like label."""
    if not node.name:
        return quote(node.function)
    return '<<font point-size="10" color="%s">%s</font><br/>%s>' % (
        faded, html(node.name), html(node.function))


def html(text):
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def file_block(file, nodes, faded):
    """A file's cluster, with a nested cluster per class."""
    body = [node_line(n, 2, faded) for n in nodes if not n.owner]
    for owner in sorted({n.owner for n in nodes if n.owner}):
        mine = [node_line(n, 3, faded) for n in nodes if n.owner == owner]
        body += cluster(file + "/" + owner, "class " + owner, mine, 2)
    return cluster(file, file, body, 1)


def arrow(a, b, kind):
    attributes = STYLES[kind]
    return "  %s -> %s%s;" % (node_id(a), node_id(b), " [%s]" % attributes if attributes else "")


def legend(kinds):
    """A cluster with one short arrow per transition type drawn, named."""
    body = []
    for kind in reversed(kinds):  # dot stacks them bottom up
        a, b = quote("legend_%s_a" % kind), quote("legend_%s_b" % kind)
        body += ['    %s [shape=plaintext, style="", label=%s];' % (a, quote(kind)),
                 '    %s [shape=point, style=invis, width=0.01];' % b,
                 "    %s -> %s%s;" % (a, b, " [%s]" % STYLES[kind] if STYLES[kind] else "")]
    return cluster("legend", "", body, 1) if body else []


def dot_source(nodes, arrows, style):
    """The graph in Graphviz's dot language. arrows: (from key, to key, type).
    style: (font, text colour, line colour, background)."""
    font, text, line, background = style
    lines = ["digraph map {", "  rankdir=LR;",
             '  graph [fontname=%s, fontcolor="%s", color="%s", bgcolor="%s"];'
             % (quote(font), text, line, background),
             '  node [shape=box, style="rounded,filled", fontname=%s, fontcolor="%s", '
             'color="%s"];' % (quote(font), text, line),
             '  edge [color="%s"];' % line]
    for file in sorted({n.file for n in nodes}):
        lines += file_block(file, [n for n in nodes if n.file == file], line)
    lines += [arrow(a, b, kind) for a, b, kind in arrows]
    lines += legend([k for k in STYLES if any(kind == k for _, _, kind in arrows)])
    return "\n".join(lines + ["}"])

