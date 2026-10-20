"""The tour map (Jakub, 2026-10-20): what the Map is to a trip, the Tour tab shows for a tour, a
signpost of the main and secret passages between its trips, as in IKEA. Each trip a row of its
sights in a frame with its number and title; a sight named file:function, its height hinting at
its lines, in a hue drawn once for all the tour's sights, neighbours apart; arrows only between
trips, of the informator's transitions. A click on a row opens its trip, so the picture is cut
into one band per trip (see bands). Pure."""

import colorsys

from .callmap import STYLES, quote

GOLDEN = 0.6180339887  # hues this far apart round the circle: neighbours never alike


def colour(k, saturation=0.35, value=0.97):
    """The k-th sight's fill, as #rrggbb."""
    rgb = colorsys.hsv_to_rgb((k * GOLDEN) % 1.0, saturation, value)
    return "#%02x%02x%02x" % tuple(round(c * 255) for c in rgb)


def node(trip, sight):
    return quote("t%d_s%d" % (trip, sight))


def height(lines):
    """A sight's box in inches: taller with more lines, within reason."""
    return round(0.3 + min(lines, 60) / 60.0, 2)


def row(k, title, sights, first):
    """Trip k's frame: its sights side by side, numbered from first for their hues."""
    body = ['  subgraph cluster_%d {' % k, '    label=%s; style=rounded;' % quote(title),
            "    rank=same;"]
    for s, (label, lines) in enumerate(sights):
        body.append('    %s [label=%s, height=%s, fillcolor="%s"];'
                    % (node(k, s), quote(label), height(lines), colour(first + s)))
    return body + ["  }"]


def tour_dot(trips, arrows, style):
    """trips: [(title, [(label, lines)])] in the tour's order; arrows: [((trip, sight), (trip,
    sight), type)] between trips; style: (font, text colour, line colour, background)."""
    font, text, line, background = style
    lines = ["digraph tour {", "  rankdir=TB; compound=true; newrank=true; pad=0;",
             '  graph [fontname=%s, fontcolor="%s", color="%s", bgcolor="%s", labeljust=l];'
             % (quote(font), text, line, background),
             '  node [shape=box, style="rounded,filled", fontname=%s, fontcolor="%s", '
             'color="%s"];' % (quote(font), text, line), '  edge [color="%s"];' % line]
    first = 0
    for k, (title, sights) in enumerate(trips):
        lines += row(k, "%d. %s" % (k + 1, title), sights, first)
        first += len(sights)
    # The rows stacked in the tour's order by edges no one sees.
    lines += ["  %s -> %s [style=invis, weight=100];" % (node(k, 0), node(k + 1, 0))
              for k in range(len(trips) - 1) if trips[k][1] and trips[k + 1][1]]
    for (a, b, kind) in arrows:
        attributes = ", ".join(x for x in (STYLES.get(kind, ""), "constraint=false") if x)
        lines.append("  %s -> %s [%s];" % (node(*a), node(*b), attributes))
    return "\n".join(lines + ["}"])


def cross_arrows(transitions, ids):
    """The informator's transitions between two trips of the tour, as ((trip, sight), (trip,
    sight), type); a place naming a trip alone stands at its first sight."""
    found = set()
    for t in transitions:
        if t.type not in STYLES or not t.source or not t.target:
            continue
        a, b = t.source[0], t.target[0]
        if a in ids and b in ids and a != b:
            found.add(((ids.index(a), t.source[1] if len(t.source) > 1 else 0),
                       (ids.index(b), t.target[1] if len(t.target) > 1 else 0), t.type))
    return sorted(found)


def bands(graph_bb, clusters):
    """graph_bb: (x0, y0, x1, y1) and clusters: {trip: (x0, y0, x1, y1)} in dot's points, y up.
    Returns [(trip, top, bottom)] from the top: each row's band reaches half way to the next."""
    order = sorted(clusters, key=lambda k: -clusters[k][3])
    edges = [graph_bb[3]] + [(clusters[a][1] + clusters[b][3]) / 2
                             for a, b in zip(order, order[1:])] + [graph_bb[1]]
    return [(k, edges[i], edges[i + 1]) for i, k in enumerate(order)]
