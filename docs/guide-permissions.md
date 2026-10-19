# The Vetting guide's permissions: a review (proposal, 2026-10-19)

The guide SightWalk starts runs `claude -p` with `--allowedTools`. Whatever is not allowed is
refused without asking: in `-p` mode Claude Code has nobody to ask. The Permissions tab chooses
that list. Changing it restarts the guide while it waits, with `--resume` on the session id
SightWalk gave it, so the conversation goes on.

## Purposes

Each purpose is the smallest set that serves it. The tab offers them as presets and the single
fields below them.

1. **Vetting (default).** Read, explain, mark. Read, Grep, Glob, sight-walk. Nothing changes on disk.
2. **Checking claims.** "Does this test really pass?" Plus read-only Bash sets: git inspection,
   running tests. The guide can run the code it talks about, which is the point of vetting.
3. **Small fixes.** A typo, a name, a guard the user agrees on. Plus Edit in the chosen folders.
   Every edit shows in the trip (the sights reload), so the user sees it at once.
4. **Copiloting.** Regular work in the walk: write, refactor, test, commit. Plus Write, the
   build and test sets, git committing. Bash "everything" is not needed even here.
5. **Looking things up.** Library docs, an error message. WebFetch and WebSearch. They are
   independent of the others: a network read cannot change the code, but it sends queries out.

## Fields and what each one allows (tooltips)

| Field | Allows | Risk |
|---|---|---|
| Reading (always) | Read, Grep, Glob: any file the user's account can read | reads secrets too, if asked to |
| Editing files: folders … | Edit, Write in those folders only (`Edit(path/**)`) | changes code; git can undo it |
| Bash: git, look | `git status`, `log`, `diff`, `show`, `blame` | none |
| Bash: tests | `python3 -m unittest *`, `pytest *`, `npm test` | runs the project's code |
| Bash: run scripts | `python3 *`, `node *` | runs any code the guide writes |
| Bash: git, commit | `git add *`, `git commit *` | local history; never push |
| Bash: git, push | `git push *` | publishes; cannot be taken back |
| Bash: install | `pip install *`, `npm install *`, `brew install *` | downloads and runs third-party code |
| Bash: everything | `Bash` | anything the user could do in a terminal |
| Web | WebFetch, WebSearch | sends queries and URLs out |

## Which choices are remembered

- **Remembered:** reading, editing folders, git look, tests, web.
- **Remembered with a reminder:** run scripts, git commit, install. The bench's header shows
  them (e.g. "guide may: commit, install") for as long as they are on.
- **Never remembered:** git push and Bash everything. They hold for one guide session; the
  next guide starts without them.

## The guide asks

When the guide needs a tool it lacks, it writes on the bench which field it needs and why. A
[Allow] button under the message turns that field on, and the guide restarts. The guide only
learns about this from the manual and the refusals; there is no code on its side.

## A guide SightWalk did not start

If the user runs `claude` in a terminal, with SightWalk added as its MCP server (the setup
command's line), and asks it to show code, that session drives the trip. Its permissions are
the terminal session's own; the tab says so and changes nothing.
