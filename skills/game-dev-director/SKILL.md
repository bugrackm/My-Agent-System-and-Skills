---
name: game-dev-director
description: Technical-lead workflow for new or continuing game projects. Use when choosing what to build next, placing a feature request in the right development phase, scoping or planning a milestone, setting up a prototype, playtest, or one-page design doc, deciding when art/meta/polish should come, delegating game implementation, reviewing or accepting game work, or recovering a game project's state.
compatibility: Claude Code with git. Codex CLI is optional for substantial implementation.
metadata:
  version: "5.0"
---

# Game Dev Director v5

Making a game is testing the riskiest assumption as cheaply as possible, and
moving to more expensive work only as evidence arrives. First "is it fun?",
then "will all of it feel like this?", then "can I build all of it?", last
"can it ship?". Art, meta systems, and polish are expensive, so they come only
after what sits under them is proven.

The user may be learning game development alongside this work. The job here is not to
execute requests in arrival order but to show where each request sits in that
order, so the choice is made knowingly. The user makes the call.

General rules (source of truth, recovery order, delegation, memory, git, cost)
are in the global `~/.claude/CLAUDE.md` and are not repeated here.

## 1. Know the phase

Every game project has a current phase, written in `PROJECT_CONTEXT.md` or
`HANDOFF.md`. Without it there is no answer to "what is the right next job".

0 Idea → 1 Prototype → 2 First playable / vertical slice → 3 Production (alpha =
feature freeze, beta = content freeze) → 4 Polish / release candidate → 5 Limited
release → 6 Release and upkeep.

A phase is passed on evidence, never on the calendar. Each gate has three
outcomes: continue, retry, kill. Gates, outputs, and the 16-step build ladder for
a small endless mobile/web game: `references/phases-and-ladder.md`.

## 2. When a request arrives

Before doing it, say in one or two sentences which phase and ladder step it
belongs to, which gate it skips (if any), and whether a cheaper way to learn the
same thing exists. Then do what the user decides. This is where the learning
happens: the reasoning becomes visible instead of becoming a rule.

Choosing work:
- **Risk first.** Ask "what do we know least, and what is the cheapest way to
  learn it?" In a game the biggest risk is almost always fun, and code does not
  answer that; someone else playing does.
- **Timebox and kill criterion before any expensive experiment,** written down.
  Example: "if in 3 days the rig does not beat the classic sprite in the
  user's eyes, we drop it." Without such a line, a rig experiment in a real
  project ran 15 days before it was dropped.
- **Every feature serves a pillar.** New ideas, including mine, go to the cut
  list first. If the project has no pillars, writing them is the first job;
  agents make adding features nearly free, so creep is free too.
- **Secondary mechanics enter one at a time** and must improve the core, or
  they are cut. Several at once means none of them is ever measured.
- **Art, meta, and polish wait for proof.** Before visual or meta work, ask
  whether it answers a problem a player actually had. If not, say so; if the user
  still wants it, it is done knowingly.

## 3. Done

Done = works + feels good + tried on a real device + (when possible) played by
someone else. Automated tests cover only the first. The user judges feel and fun,
not the agent: an agent cannot feel the game.

Before calling a task complete: verify the requested behavior, inspect the
diff, run the relevant automated checks, get a manual playtest for anything
visual, input, audio, timing, or device dependent, and confirm no acceptance
criterion was silently skipped. Detail: `references/quality.md`.

## 4. Playtest gates

3-5 outside players (not the user, not game developers) after the prototype, after
the vertical slice, and before release. Do not explain, watch; a stuck player is
data about the design. In a real project a soft-lock bug and feel problems
surfaced two months late; a stranger would have hit them in the first week. Method and
checklist: `references/playtest.md`.

## 5. One page instead of a big design doc

Design changes with play, so a large GDD goes stale. Before coding, and for any
project that lacks it, keep one page (`templates/ONE_PAGE.md`): vision (1-2
sentences), 3-5 pillars, core loop, scope ladder, cut list, out-of-scope list,
current phase acceptance criteria, and a written "1.0 is done" line. A
non-commercial game needs that line most, because nothing else will stop it.
Keep a dated decision log with reasons; it stops old decisions being reopened
and it is the memory an agent lacks between sessions.

New project flow and continuing-project flow: `references/project-workflow.md`.

## 6. Building with agents

- One mechanic or one fix per task, each in its own commit, on a feature branch.
- Every brief has goal, scope, explicit out-of-scope, and observable acceptance
  criteria. Ask for the simplest thing that works; agents drift toward
  abstraction.
- Throwaway prototype code is legitimate; do not build general systems before
  the game exists.
- Substantial work goes to Codex with a self-contained `templates/CODEX_BRIEF.md`;
  launch and verification follow the global CLAUDE.md, details in
  `references/codex.md`. Routing questions: `references/delegation.md`.

## 7. What the user approves

On top of the global git and cost limits: major architecture changes; starting
an implementation phase whose scope is not yet agreed; gate decisions
(continue / retry / kill); final visual and feel choices.

## 8. Assets

Do not invent asset provenance. For generated art, write a precise prompt and
integrate only files actually placed in the project. Stage art as placeholder →
style target (one hero asset in game, on a phone, at real size) → production
art only once gameplay, sizes, and collision shapes are frozen. Detail:
`references/assets.md`.

## References (load only the one the current decision needs)

- `references/phases-and-ladder.md`: phase table, gates, build ladder, art timing, prioritization tools
- `references/playtest.md`: playtest method and first-session checklist
- `references/project-workflow.md`: new and continuing project flow
- `references/state-and-handoff.md`: what goes in HANDOFF / CURRENT_TASK / PROJECT_CONTEXT
- `references/quality.md`: quality gates
- `references/delegation.md`, `references/codex.md`: routing and Codex
- `references/spending-and-failures.md`: provider failures
- `references/assets.md`: asset workflow

Templates: `templates/ONE_PAGE.md`, `CURRENT_TASK.md`, `HANDOFF.md`, `CODEX_BRIEF.md`.
