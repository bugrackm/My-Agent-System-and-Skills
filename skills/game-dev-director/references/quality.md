# Quality Gates

A change is not complete merely because code was produced.

Apply the smallest relevant set of gates:

1. Scope
   - requested behavior implemented;
   - no unrelated changes.

2. Static integrity
   - syntax/type/lint/import/editor-load checks appropriate to stack.

3. Automated behavior
   - relevant unit/integration/headless tests;
   - regression checks for touched systems.

4. Runtime/manual behavior
   Required when behavior depends on:
   - animation/visual layout;
   - input/touch/controller;
   - audio;
   - timing/physics;
   - device/safe-area/orientation;
   - platform host behavior.

5. Diff/review
   - architecture/conventions preserved;
   - no accidental generated/secret files;
   - failure/error paths considered.

6. Durable state
   - CURRENT_TASK/HANDOFF updated;
   - blocker/decision docs updated where relevant.

For games, done also means it feels good, it was tried on a real device, and
(when possible) someone other than the user played it. The user judges feel.

Report what was actually verified. Never imply a manual test happened when it did not.
