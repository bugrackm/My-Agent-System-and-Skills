# Project Workflow

## New game

### 1. Discovery
Clarify:
- game loop and player goal;
- target platform/device;
- engine/stack;
- art/audio constraints;
- monetization/platform requirements if any;
- scope and milestone target;
- explicit non-goals.

Ask only questions that materially change implementation.

### 2. Durable brief
Create/update project docs in the existing durable-doc location:
- PROJECT_BRIEF;
- REQUIREMENTS;
- OPEN_QUESTIONS;
- constraints where useful.

### 3. Research
Delegate at most two independent research tracks when useful.
Do not research stable/local facts that can be verified directly.

### 4. Architecture
Main Claude synthesizes:
- RESEARCH;
- ARCHITECTURE;
- DECISIONS;
- IMPLEMENTATION_PLAN.

High-impact choices come to the user before irreversible implementation.

### 5. Implementation
Break work into coherent milestones/tasks.
Use Sonnet for bounded work and Codex for substantial coding.
Keep CURRENT_TASK current.

### 6. Verification
Automated tests/checks plus manual playtest/device verification when needed.

### 7. Checkpoint
Update HANDOFF/CURRENT_TASK and global continuity.
Commit/push only under the git policy.

## Continuing game

Do not re-run discovery from scratch.

Recover durable state first, identify the exact active/next milestone, inspect only
relevant source, then propose the next concrete action.
