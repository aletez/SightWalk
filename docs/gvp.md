# Grounded Vetting Protocol, version 0 (draft)

*The protocol SightWalk speaks between a guide agent and a vetting tool. Name chosen by Jakub,
2026-10-20; in Polish, protokół ugruntowanego sprawdzania kodu.*

Status: draft for review. It describes the protocol as the code implements it at commit
`1cbd3ce` (2026-10-20) (`sw/manual.py`, `sw/validator.py`, `sw/marks.py`, `sw/ontology.py`,
`sw/subl_mcp_http.py`, `sw/subl_executor.py`). Nothing here is invented; what the protocol would
still need is marked **Open**. Where this document and the code differ, the code is right and
this document has a bug.

Concept and design: Jakub Kozakoszczak. Code and this draft: written by Claude.

## 1 Purpose and scope

The protocol lets an agent explain code to a person with every claim **grounded**: tied to the
exact lines it is about, in both directions.

- The **guide** ties its words to places. It chooses which code is on screen (a trip of
  sights) and writes answers whose words carry places, lines or characters, some with an icon
  on their line, and jumps between two places. The person sees the words framed and the lines
  marked, never a line number.
- The **user** ties their words to places in the same markup (`<here>`), by linking words to
  code or by selecting it, so "this" and "here" mean exactly those lines, or characters.

In scope: the tools the guide calls, their arguments and replies, the data model of sights,
trips, informators and tours, the place grammar, the inline tags and the rules a conforming tool
enforces. Out of scope: how a tool draws anything (Sublime windows, colours, gutter icons), how
the guide reasons, editing permissions of the agent.

## 2 Roles

- **Guide**: any agent that speaks MCP as a client (Claude Code, which the plugin can start
  itself, or another, a local model included). It should not be the session that wrote the code
  under review.
- **Vetting tool**: the MCP server. It renders trips, places marks, carries the conversation
  (the Vetting Bench), lets the user edit the shown files, and validates every call before
  acting on it. SightWalk (Sublime Text) is the only implementation.
- **User**: the person vetting the code. They talk only to the vetting tool; the tool passes
  their messages to the guide through `wait_for_user`.

The guide drives; the tool never calls the guide. The conversation is a loop: `wait_for_user`,
then any number of `show` / `say`, then `wait_for_user` again.

## 3 Transport

- MCP over Streamable HTTP, JSON replies only: the server opens no event stream (`GET` answers
  405). Bound to `127.0.0.1` on a configured port.
- Every `POST` carries `Authorization: Bearer <token>`; otherwise 401. The token and port live in
  the tool's settings; setup writes them to `~/.sight_walk/config.json` and puts the
  `claude mcp add --transport http` line on the clipboard.
- `initialize` returns a session id in `Mcp-Session-Id`, `capabilities: {"tools": {}}`,
  `serverInfo: {"name": "sight-walk", "version": "1.0"}`, echoes the client's
  `protocolVersion` (default `2025-06-18`), and delivers **the manual** in `instructions`: the
  full text of how to compose trips and answers (`sw/manual.py`, `MANUAL`). The manual is
  normative for the guide; a guide reads it once, at the start of its session.
- Methods: `initialize`, `tools/list`, `tools/call`, `ping`. Others: JSON-RPC error -32601.
  Notifications get 202 and no body. `DELETE` ends a session.
- A tool's result is one text content item holding JSON. A refusal or failure is
  `{"error": "<message>"}` with `isError: true`, not a JSON-RPC error. The message tells the
  guide how to correct the call (section 8).
- A call that needs Sublime's main thread fails after 10 s with an error that says to retry once.

## 4 Data model

From `sw/ontology.py` and DECISIONS.md, "Ontology".

- **Sight**: a range of one file's lines, in order, written `file:begin-end` (1-based,
  inclusive; `file:line` is one line). It holds one function at most, whole or a fragment, and
  of a class no more than the one that function is part of. Top-level script code goes in sights
  of about equal length, each a step.
- **Trip**: a sequence of sights, read top to bottom, and a network of transitions between them.
  Whatever one `show` opens is a trip. Kind: `run` (default; one run of the program, sights in
  the order control reaches them), `comparison` (fragments side by side), `survey` (all places
  about one thing). Every trip has a name; its id is the name slugged
  (`"One tool call over HTTP"` → `one-tool-call-over-http`).
- **Transition**: `{type, from, to}`, a typed arrow between two places. It reads as a sentence
  true of its source: "*from* calls *to*". Types in a trip:

  | type          | from → to |
  |---------------|-----------|
  | `calls`       | the calling line → the line of the definition it reaches (every one must be named) |
  | `returns`     | a line giving control back → the line of the call it returns to |
  | `leads_to`    | where the story goes on, though no code calls it |
  | `unblocks`    | the source must be understood to understand the target, so it comes first, as one task unblocks another (old files' `101s`, its ends swapped; `underlies` as is) |
  | `passes_data` | a value made at the source is used at the target |
  | `comparable`  | worth comparing; direction means nothing |

  In an informator only: `own_trip` (⟨trip, sight, a definition's line⟩ → ⟨trip⟩: the trip that
  definition has of its own). All transitions are given by the author; a tool may validate them,
  never infer them.
- **Informator**: a network of trips, unordered, covering the whole program's code: every
  function in at least one trip. Places are ⟨⟩, ⟨trip⟩, ⟨trip, sight⟩, ⟨trip, sight, line⟩, a
  trip by its id. It may keep each trip's conversation (transcripts). The ontology does not
  check coverage; SightWalk's `tools/trips.py` does for its own informator.
- **Tour**: one informator's trips in one order. Either laid out from the informator by
  transition types (default `leads_to` and `unblocks`: from each trip nothing leads to, along
  `leads_to` depth first, a trip that unblocks another before it), or chosen and ordered
  by an author under a name.
- **Commit**: a trip and an informator may name the commit their line numbers are counted in.
  Nothing in the live protocol uses it yet (see 9.1).

### 4.1 Files (JSON)

A trip file (`docs/trips/linking-words-to-code.json`, shortened). Places in files are lists of
indices, not names:

```json
{
 "name": "Linking words to code",
 "kind": "run",
 "commit": "9c3c6511ed198c981c38788406842677c7b1336d",
 "sights": ["sw/subl_commands.py:115-122", "sw/subl_links.py:19-30", "..."],
 "transitions": [{"type": "calls", "from": [3, 35], "to": [11, 266]}]
}
```

An informator file names its trips' files (relative to itself), so a trip stays self-contained;
its transitions' places start with a trip id (`docs/informators/sightwalk.json`):

```json
{
 "name": "SightWalk",
 "commit": "9c3c6511ed198c981c38788406842677c7b1336d",
 "trips": ["../trips/plugin-start-and-stop.json", "../trips/setting-up-the-agent-bridge.json"],
 "transitions": [{"type": "leads_to", "from": ["plugin-start-and-stop"],
                  "to": ["setting-up-the-agent-bridge"]}]
}
```

Transcripts sit beside it in `<name>.transcripts.json`, `{trip id: text}`. A tour file
(`docs/tours/how-the-program-talks-to-the-agent.json`): `{"name", "informator": "<file>",
"trips": [trip ids in order]}`.

Schema of a transition in `show` (`sw/manual.py`, `TRANSITION`):

```json
{"type": "object", "required": ["type", "from", "to"], "properties": {
  "type": {"type": "string", "enum": ["calls", "returns", "leads_to", "unblocks", "passes_data", "comparable"]},
  "from": {"type": "string"}, "to": {"type": "string"}}}
```

## 5 Place grammar

Sight names: the sight at index *i* of the trip is a small letter in parentheses, `(a)` … `(z)`,
then `(a2)` … `(z2)`, `(a3)` … (`spec.sight_name`). The user may write `c`, `c)` or `(c)`; the
guide always writes `(c)`. Capitals are reserved for icons, so names and icons never meet.

| form           | meaning                                   | used in |
|----------------|-------------------------------------------|---------|
| `(c)`          | sight (c) alone                           | transitions |
| `(c):34`       | file line 34, which sight (c) must show   | transitions, `<here>` and its sugar |
| `(c):34-36 (d):12` | one or more places, ranges allowed, space-separated | `<here>`, the `here` reply field |
| `(c):34:12`    | a caret: line 34, column 12 (columns from 1) | the `here` reply field without a selection |
| `(c):34:12-16` | characters 12 to 16 of line 34, the end included | `<here>`, the `here` reply field |
| `(c):34:12-36:5` | characters from 34:12 to 36:5          | `<here>`, the `here` reply field |
| `(>):1:10-11`  | the bench's draft (its prompt is `>>>`), its lines from 1; any form above | test commands; reserved for places in the conversation |
| `[2, 34]`, `[2]` | sight index and file line              | trip files |
| `[trip-id, 2, 34]` | ⟨trip, sight, line⟩                   | informator files |

Lines are always **file** lines, not lines within the sight. A place in a mark must lie inside its
sight's range.

## 6 Messages (tools)

Eight tools, all called by the guide; the user acts only through the tool's interface. Every
call is judged by the validator first (section 8) and refused with a message that says how to
correct it.

| tool | parameters | what it does | why it exists |
|------|------------|--------------|---------------|
| `show` | `sights` [spec] (required); `transitions` [{type, from, to}] (required, `[]` when none); `trip` string (required); `root` string | Opens a reader, or replaces the trip in it, with the sights in the given order, scrolled to the top; draws the transitions on the Map. Replies with the sights' names, `{"(a)": spec, …}`. | The guide, not the user, chooses which code answers the question and in what order: the trip is the guide's first claim about the code, and naming its transitions makes that claim checkable (the Map draws exactly them, never guesses). |
| `open_trip` | `file` path (required); `root` string | Opens a trip saved as a file (name, kind, sights, transitions), as an informator keeps it. | Trips prepared once, for documentation or a tour, can be walked again without the guide recomposing them, and stay comparable across sessions. |
| `say` | `text` (required): the answer, with name tags and mark tags (section 7); `status` string | Appends the answer to the bench, frames its marked words, puts icons and arrows on the marked lines, draws its jumps on the Map. Replies `{"ok": true}`. | Answers must be grounded: every claim about code is tied to the exact places it is about, so the user can check it with one click instead of trusting prose. The validator refuses line numbers in prose and an answer about code with no marks. |
| `wait_for_user` | `timeout_s` integer (≤ 50) | Blocks until the user sends a message, then returns it: `text` (with the user's `<here>` links), `visible`, `here`, `selected`, `edited`, `unanswered`; or `{"timeout": true, "next": …}`. | The conversation happens in the tool, not in the agent's terminal; the guide must keep listening, and must not fill silence (it is told to call again at once and say nothing). The reply carries what "this" means, so the guide never guesses. |
| `state` | none | Returns the sights, the visible ones and `here`. | Lets the guide check what the user sees before answering, without waiting for a message. |
| `close` | none | Closes the reader window. | Ends a walk cleanly; the guide can close what it opened. |
| `browse` | `folder` absolute path (required) | Opens a trip with no sights, a file browser of the folder in their place; a file the user opens there becomes the trip's one sight. | When the user does not yet know what to ask about, they can start from the files; the conversation goes on. |
| `settings` | `values` object: `tint` 0–1, `default_conversation_height` 0–1, `bench_side` `left`/`right` | Reads the user's settings, or changes the editable ones. | The user may ask the guide to change the layout in words, without opening settings files. |

The `show` example is the first three sights of `docs/trips/one-tool-call-over-http.json`, with its transitions in the guide's place form; the `say` example is written for it. Schemas as `tools/list` returns them (`sw/manual.py`, `TOOLS`).

### show
`{sights: [spec], transitions: [transition], root?: string, trip: string}`; `sights`,
`transitions` and `trip` required. Opens or replaces the reader,
scrolled to the top. `root` is the base folder of relative paths. Reply:
`{"ok": true, "sights": {"(a)": spec, …}}`.

```json
{"trip": "One tool call over HTTP",
 "sights": ["sw/subl_mcp_http.py:94-105", "sw/subl_mcp_http.py:78-81", "sw/subl_mcp_http.py:65-74"],
 "transitions": [{"type": "calls", "from": "(a):95", "to": "(b):78"},
                 {"type": "calls", "from": "(a):104", "to": "(c):65"}],
 "root": "/Users/user/Repositories/SightWalk"}
```

### open_trip
`{file: string, root?: string}`: opens a trip from its file (4.1) instead of composing it. `root`
defaults to the file's repository. Reply: `{"ok": true, "trip": name, "sights": {…}}`.

### say
`{text: string, status?: string}`. Appends the answer to the bench; `text` carries the inline
tags (section 7). `status`: a few words on the topic, kept in the status line until changed.
The first answer with marks after the user spoke replaces the earlier marks; later ones add.
Reply: `{"ok": true}`. (SightWalk also accepts `message` for `text`.)

```json
{"text": "<func>do_POST</func> first checks the token <calls at=\"(a):95 (b):78\">by calling</calls> <func>authorized</func>, then <calls at=\"(a):104 (c):65\">passes the message</calls> to <func>reply</func>; <here at=\"(b):81\" icon=\"A\">this line</here> compares in constant time.",
 "status": "one tool call over HTTP"}
```

### wait_for_user
`{timeout_s?: integer}`, capped at 50 s. Returns the user's next message:

| field      | always | meaning |
|------------|--------|---------|
| `text`     | yes    | the message; may contain `<here at="…">words</here>` |
| `visible`  | yes    | the specs of the sights on screen |
| `here`     | no     | where "this" points, always in the place grammar: the caret in the sight touched last, `"(c):105:9"`, or, when the message was sent with a selection, the selected places, `"(c):34-36 (d):12:5-9"` (carets count as their lines) |
| `selected` | no     | the text the user selected, when there is one |
| `edited`   | no     | sights whose ranges an edit moved: `"sw/a.py:10-20, now 10-23"` |
| `unanswered` | no   | the previous message is returned again because no `say` answered it |

On timeout: `{"timeout": true, "next": "…"}`; the guide calls again at once and says nothing.
User messages with a fixed meaning, typed on the bench: `Explain next.`,
`Explain previous.`, `Change the metaphor.` (their meaning is in the manual).

### state
No arguments. Returns `visible`, `here`, `selected` as above, and `sights`
(`{"(a)": spec, …}`).

### close
No arguments. Closes the reader window. `{"ok": true}`.

### browse
`{folder: string}` (absolute). Opens a trip with no sights, a file browser in their place; a
file the user opens becomes the trip's one sight, the whole file. `{"ok": true}`.

### settings
`{values?: object}`. Without values, reads; with values, changes them. Returns the editable
settings: `tint` (0–1), `default_conversation_height` (0–1), `bench_side` (`"left"` /
`"right"`). These are presentation and tool-specific (see 9.3).

## 7 Inline tags

Guide and user write one markup (2026-10-20). Tags live in `say`'s text and in the user's
`text`. A tag opens and closes on one line and holds no other mark tag. Unknown tags are refused.

### 7.1 Semantics

| tag | means |
|-----|-------|
| `<here at="(c):34-36 (d):12">this check</here>` | the enclosed words are about exactly those places, whole lines or characters (`(c):34:12-16`). From the user, a link to characters of one line carries them too, `code="token"`, so the guide can check the place by the code. User's tags nest where phrases nest; they never cross. |
| `icon="1"` on `here` | each place's first line gets an icon: one sign for all places, or one per place in order (`icon="A B"`). A sign is a short mark, a digit or letter, an emoji, or a path to an image; a tool draws what it can and may skip the rest. Never with a place naming a sight alone. In SightWalk: a digit `1`–`9` (an ordered relation) or a capital `A`–`Z` (unordered lines). |
| `jump="calls"` on `here` | exactly two places, source then target, joined by a transition of that type (`calls`, `returns`, `leads_to`, `unblocks`, `passes_data`, `comparable`). No `icon`. |
| `<calls at="A B">words</calls>` | sugar for `<here at="A B" jump="calls">words</here>`, one tag per transition type. Empty, `<calls at="A B"></calls>`, it adds only the arrow on the Map: the one markup with no place in the text. |
| `<func>`, `<class>`, `<var>`, `<str>` | the enclosed text is a name of code: function or method; class or type; variable, parameter or attribute; a short string of code. |

Identity: the same tag written again (same places and sign, or same ends) is the same mark;
it makes no second mark, so later words refer back to it.

Answer-level rules: an answer that names code must mark at least one place, unless an earlier
answer to the same message did; no line numbers in prose (lines are named by their icons); a
line holds at most two marks (a jump's end counts as one); sights are named only `(c)`.

### 7.2 Presentation in SightWalk (not part of the protocol)

The user never sees the tags. Words with an icon are framed in its colour (digits orange,
letters blue), its sign written after them; its line gets the icon and an outline. Words with a
place and no icon are framed in the text's colour; a click selects the place, characters
included. A jump's ends get arrows, and the Map draws the answer's jumps beside the trip's
transitions. A line's first mark stands in the gutter,
its second on the scroll strip beside it. Jumps take colours in order green, red, yellow, purple,
brown, both ends and framed words alike; arrows bend towards each other. An eye on the first or
last visible line looks towards a mark off screen. Name tags become invisible operators that give
the name its code colour. `<here>` words are framed. Backticks and `**` are refused because the
bench does not render Markdown.

## 8 Conformance rules

A conforming vetting tool refuses these calls, with a message that says how to correct them
(`sw/validator.py`, plus the parsers it calls). The guide must not need a second try for the
same reason.

| # | tool | rule | message intent |
|---|------|------|----------------|
| 1 | show, open_trip, say | after the user stops an answer, nothing more about it | stop; call `wait_for_user` |
| 2 | show | `trip` is a non-empty name | name the trip |
| 3 | show | `sights` is a list of strings | the list's form |
| 4 | show | `transitions` is a list of `{type, from, to}`; `[]` when none | name every call; the form |
| 5 | show | each sight parses as `file:begin-end`, 1 ≤ begin ≤ end | the spec's form |
| 6 | show | each place parses as `(c)` or `(c):34` | the place's form |
| 7 | show | each type is known and allowed in a trip | the types |
| 8 | show | each place lies in the trip (sight exists, line in its range) | which end, which sight or line |
| 9 | show, open_trip | at least one sight | give one |
| 10 | show, open_trip | each file exists and has the lines; relative paths need `root` | every problem in one message |
| 11 | show, open_trip | a sight holds at most one function and at most one outermost class | which sight holds which; split them |
| 12 | open_trip | the file reads as a trip | the reason |
| 13 | say, state, wait_for_user | a trip is open | call `show` first |
| 14 | state | the reader has finished loading | retry in a moment |
| 15 | say | the user has spoken since the last wait | say nothing; wait |
| 16 | say | no backticks or `**` | use name tags |
| 17 | say | only known tags (name tags, `here`, one per transition type), each closed on its line, none nested; `<icon>` and `<jump>` are gone | the tags |
| 18 | say | marks are well formed: `at` given; `icon` one sign or one per place, never with a sight alone; `jump` with exactly two places and no `icon`; no `(>)`; in SightWalk a sign is `1`–`9` or a letter | the mark's form |
| 19 | say | every marked place lies in a shown sight | which place |
| 20 | say | a line holds at most two marks | drop one, or say it in words |
| 21 | say | no line numbers in prose (`line 12`, `linia 33`, `(l. 42)`, `a.py:32`, `(35)`; any language the pattern covers) | name lines by icons |
| 22 | say | an answer naming code marks a place, unless one already did for this message | mark the places; answer before waiting |
| 23 | close | a reader is open | nothing to close |
| 24 | browse | `folder` is an existing folder | give an absolute path |
| 25 | settings | only editable keys; `bench_side` left/right; others numbers 0–1 | the allowed keys and ranges |
| 26 | any | the tool exists | the tool list |

Rule 22 is detected heuristically (`marks.speaks_of_code`: a name tag, a backticked word,
`a.b:12`, or "line(s) N" in English or Polish). Rule 21 likewise is a pattern, not a parser.

## 9 Open (for v1)

1. **Commit-stable addressing.** Live places are file lines in the working tree; an edit moves
   them (`edited`), and trip files carry a `commit` nothing checks. Needed: `file:line@commit`
   (or a content anchor), a rule for what a tool does when the commit differs, and moving
   transitions across commits.
2. **Capability negotiation.** Today the guide learns everything from one manual. Needed: a
   declared protocol version and capabilities (e.g. editing, browse, informators, max marks per
   line, sight-name alphabet) in `initialize`, so a guide adapts to a tool that offers less.
3. **Semantics vs presentation.** The manual mixes both (gutter, strip, colours, "one and a half
   sights on screen", 25-line functions). Needed: a normative core (7.1, 8) and a separate
   presentation profile per tool; rule 20 (two marks per line) is presentational and may move.
4. **A second implementation** (a VS Code alpha) to prove the core carries over; the pure
   modules (`sw/` without `subl_`) are meant to be reused as they are.
5. **Conformance test suite**: the rules of section 8 as calls and expected refusals, runnable
   against any server (`tools/poke.py` is a start).
6. **Relations from the user.** The markup lets the user write jumps too, but a tool has no way
   yet for a person to make one (linking words makes `here` only).
7. **Versioning.** `serverInfo.version` is `"1.0"` and fixed; the protocol has no version of its
   own. Needed: a version in the manual and in `initialize`, and a policy for changes.
8. **Informators and tours over the wire.** They exist as files; only `open_trip` opens one trip.
   No call opens an informator, follows a tour or reports where in it the user is.
9. **Stop and user-initiated events.** The user stopping an answer is seen only as refusals
   (rule 1); there is no event or reply field for it.
10. **Machine-readable refusals.** Errors are prose; a code per rule (section 8's numbers) would
   let a guide or a test suite tell them apart.

## Name

**Grounded Vetting Protocol** (Jakub, 2026-10-20): "grounded" for words tied to places, the
point of the protocol; "vetting" for its purpose. The acronym GVP is free of the collisions of
GWP (Global Warming Potential) and GCC (the compiler). Polish: **ugruntowanie** for grounding,
the established term (as in *ugruntowanie symboli*, symbol grounding), with **zakotwiczyć** for
the act of tying one word to one place.

Earlier candidates:

- Sightline Protocol: keeps the Sights metaphor and says what it does, a line
  of sight from words to lines.
- Waypoint
- **Grounded Walkthrough Protocol** (Jakub's favourite, for "Grounded"; GWP collides with Global
  Warming Potential), and its kin: Grounded Code Walkthrough, Grounded Explanation Protocol,
  Grounded Vetting Protocol, Grounded Trip Protocol, Grounded Guide Protocol
- Anchored Prose Protocol
- Itinerary Protocol

Avoid "CodeTour": an existing VS Code extension.
