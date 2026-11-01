---
name: game-dev-director
description: Technical-lead workflow for new or continuing game projects. Use when choosing what to build next, scoping or planning a feature or milestone, setting up a prototype or playtest, deciding when art/meta/polish should come, implementing or reviewing game work (including Godot web export issues), or recovering a game project's state.
compatibility: Claude Code with git. Codex CLI is optional.
metadata:
  version: "6.1"
---

# Game Dev Director v6.1

These notes are judgment aids for game work, not checklists. General rules
(role, source of truth, delegation, git, cost, memory, verification reporting) live in the
global `~/.claude/CLAUDE.md` and are not repeated here.

## How games get made (use as a map)

Cheapest risk first: "is it fun?" → "will all of it feel like this?" → "can I
build all of it?" → "can it ship?". Art, meta, and heavy polish are expensive to
redo, so they pay off most once the core is proven. When a request clearly
skips something that would change its value (e.g. production art before the
action set is settled), say so in a sentence and continue with what the user
decides. Don't add ceremony to ordinary requests.

Phases, gates, build ladder, art timing: `references/phases-and-ladder.md`.

Useful habits, not mandates:
- For big uncertain experiments (a rig, a new art pipeline), agree on a rough
  timebox and what would make us drop it. A rig experiment in a real project
  ran 15 days without one.
- Measure secondary mechanics: adding several at once makes it hard to tell
  which one helped.
- Prefer playtest evidence over guesses when choosing what to fix.

## Doing the work

- Fix root causes. Refactor when it makes the change clean; don't stack hacks
  to keep a diff small. Keep unrelated behavior intact.
- Work in slices that touch input + logic + visuals + sound as needed, so the
  result can be played and judged.
- Throwaway prototype code is fine; general systems before the game needs them are not.
- Codex (`references/codex.md`) is an option for large, well-specified,
  self-contained work.

## Gotchas (Godot 4 web export)

Checked against Godot 4.6-4.7 docs, source and issue tracker (2026-11). Each one
breaks a reasonable assumption:
- `Input.get_accelerometer()` returns `Vector3.ZERO` on web (and on Android unless
  `input_devices/sensors/enable_accelerometer` is on). Browser tilt needs a JS
  `devicemotion` bridge into `Input.set_accelerometer()` plus an iOS permission
  tap over HTTPS (bridge untested), or a non-tilt control.
- Web audio defaults to "Sample" playback: no bus effects and no procedural
  audio generation (so no `AudioStreamGenerator`). Render procedural SFX
  offline to WAV; "Stream" mode allows effects at the cost of latency and
  possible crackling (that docs page is marked experimental).
- `AudioStreamRandomizer` with one stream always plays that stream; give it 3+
  variants. It may also skip the Sample path on web (source reading, untested);
  randomizing `pitch_scale` in code is likely safer. Test in a real browser.
- iOS Safari + Sample mode has an open crash report (godot#116750: crash after
  10-30 min of repeated `play()`, reported on 4.5.1, unconfirmed on 4.7); check
  its status before shipping long iOS sessions.

Check first (documented risk, not measured in practice):
- Web uses the Compatibility renderer, which has no shader precompile: the first
  use of an effect can hitch, so show effects once during loading.
- Physics ticks at 60 Hz by default; on 120 Hz phones physics-driven motion can judder.
  2D physics interpolation smooths it (slight latency; reset after teleports).

Project-specific quirks belong in that project's CLAUDE.md, not here.

## Done

Works, verified with the relevant automated/headless checks, diff reviewed, and
for anything about feel, input, audio, timing, visuals, or device behavior,
the user has played it. An agent cannot judge feel.

## Playtests

The maker cannot see the game's problems. 3-5 outside players after the
prototype, after the vertical slice, and before release; watch, don't explain.
Method: `references/playtest.md`.

## Design doc

One page beats a big GDD (`templates/ONE_PAGE.md`): vision, pillars, core loop,
cut list, "1.0 is done" line. Keep a dated decision log with reasons so old
decisions are not reopened without new evidence.

## The user decides

Large new features or direction changes (agree scope briefly first), major
architecture changes, continue/drop calls on experiments, final visual and feel
choices. Small fixes and improvements inside an agreed task go ahead.

## Assets

Never invent asset provenance; integrate only files actually in the project.
Details: `references/assets.md`.

## Files

- `references/phases-and-ladder.md`, `references/playtest.md`, `references/assets.md`, `references/codex.md`
- `templates/ONE_PAGE.md`, `CURRENT_TASK.md`, `HANDOFF.md`, `CODEX_BRIEF.md`
