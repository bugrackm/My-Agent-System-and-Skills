# Project Workflow

## New game

1. **Discovery.** Clarify the core loop and player goal, target platform and
   device, engine, art/audio constraints, and explicit non-goals. Ask only
   questions that change what gets built.
2. **One page** (`templates/ONE_PAGE.md`), including the kill criterion for the
   prototype. Phase 0.
3. **Research** only what is uncertain and cannot be checked locally (engine
   export limits, platform rules). Tell research agents to open the sources.
4. **Prototype** in a 1-2 week timebox: grey boxes, no audio, only the core, on a
   real device. Architecture can stay minimal; throwaway code is fine.
5. **Gate 1 playtest** (`references/playtest.md`). Continue, retry, or kill. Do
   not try to rescue an unfun prototype with art or menus.
6. Only after the gate: architecture and decisions docs as the project needs
   them, then milestones following the build ladder
   (`references/phases-and-ladder.md`). Major architecture choices go to the user
   before irreversible implementation.

Each milestone: scope with acceptance criteria in `CURRENT_TASK.md`, build,
verify (`references/quality.md`), playtest when feel is involved, checkpoint.

## Continuing game

Do not rerun discovery. Recover durable state (global CLAUDE.md order), find
the current phase and the active or next task, read only relevant source, then
propose the next concrete action and where it sits on the ladder. If the
project has no recorded phase, pillars, or "1.0 done" line, propose writing the
one page before new features.
