# Phases, Gates, and the Build Ladder

Sources: Chandler (The Game Production Handbook), Schell (The Art of Game
Design), Keith (Agile Game Development), Voodoo/Homa/Supercell practice, Derek
Yu ("Finishing a Game"), Griesemer (Halo). Each phase
removes one risk before money and time go into the next, more expensive phase.

## Phases

| # | Phase | Risk it removes | Output | Exit gate | Solo / non-commercial form |
|---|---|---|---|---|---|
| 0 | Idea | "Worth testing?" | One page: vision, pillars, core loop in one sentence | Decide a small fixed prototype budget | Write it in an hour, kill criterion included |
| 1 | Prototype | "Is the core fun?" | Grey-box playable core + written verdict | Others replay on their own; you can say what is fun | 1-2 week timebox, 3-5 outside testers |
| 2 | First playable / vertical slice | "Can it be built, how will the final feel?" | Thin but complete loop, art-style proof, scope estimate | "The whole game will feel like this; the rest is known work" | Thin complete slice + cut list + written scope |
| 3a | Production → alpha | "Can I build all of it?" | All systems in, placeholder content allowed | **Feature freeze** | Self-imposed freeze |
| 3b | Production → beta | | All content, art, audio in | **Content freeze**: bugs and tuning only | Self-imposed freeze |
| 4 | Polish / RC | "Can it ship?" | Release-candidate build | No known blocking bug | Device + browser test, "done" list |
| 5 | Limited release | "Do real players stay?" | Measurement, tuned first minute | Target met, or kill | Share with friends/community, observe |
| 6 | Release + upkeep | Scale, continuity | Updates | Decision to stop | Optional upkeep and an explicit stop point |

Gate outcomes: continue, retry, kill. A gate passes on evidence, never because
the time ran out. Write the kill criterion before the phase starts: killing
early is cheap, finishing a mediocre game is expensive (Supercell killed 30+
games for 5 hits).

Commercial mobile KPIs (D1 retention ~35-40%+, CPI thresholds) are for
publishers; for a non-commercial game drop them and ask "do players like it?"
through observed playtests, return visits, and session length.

## Inside a phase

- Risk first: do whatever could kill the project (fun, performance, unknown
  tech) before known work.
- Timebox every experiment; at the end decide continue / retry / cut.
- Keep main playable at every commit. Build in slices (input + logic + visual +
  sound for one feature), not layers.
- Short loops: 1-2 weeks, ending in a showable build and a short "what I learned".

## Build ladder (small endless vertical mobile/web game)

| Step | What | Done when | Typical mistake |
|---|---|---|---|
| 1 | Input and movement feel, on a real phone | Jumping is fun with plain shapes | Tuning only in the editor; art first |
| 2 | Core mechanic (platforms, camera, wrap) | A run plays start to end | Abilities before the basic jump works |
| 3 | Death and instant restart | Death → new run < 1 s | Slow, clunky restart |
| 4 | Score | Height is visible and you want to beat it | Bloated scoring rules |
| 5 | Procedural generation + difficulty curve | Runs vary, difficulty rises, gaps always reachable | Unfair/unreachable layouts; flat curve |
| 6 | Light juice pass | Shake, a few particles, sounds make actions feel good | Heavy juice hiding a weak core |
| 7 | Plain UI flow | Start, play, game over, retry, pause | Fancy menus before the flow works |
| 8 | Secondary mechanics, **one at a time** | Each one improves the game, or is cut | Adding all at once; never cutting |
| 9 | **Vertical slice + outside playtest** | Strangers play unaided and restart on their own | Testing only yourself |
| 10 | First minute (FTUE) | New player gets the controls in the first run | Text tutorial; designing it too early |
| 11 | Meta: currency, shop, cosmetics | Earning and spending work end to end | Building it before the core is proven |
| 12 | Art style target → production art | Style locked; action set and hitboxes frozen | Rig/animation before the action set is frozen |
| 13 | Audio pass | Final music/SFX replace placeholders | Missing audio hooks found late |
| 14 | Settings and save | Data persists, options work | Fragile save format |
| 15 | Device and performance (really continuous) | Stable frame rate on a low-end phone; safe areas right | Leaving it to the end |
| 16 | Polish and release | Known bugs fixed, cut list applied | New features during polish |

Steps 1-5 find the fun, 6-9 are the first playable and vertical slice, 10+ are
production and polish.

Where sources differ: juice comes as a light pass once the core works and a
heavy pass once the core is accepted. Variety beats repetition: Griesemer's
"30 seconds of fun" (Halo) means a 3-second loop inside a 30-second loop inside
an ever-different 3-minute loop; in an endless game the context (layouts,
enemies, hazards) must keep changing while the core stays.

## Art timing

1. Placeholder: plain shapes or free packs; everything replaceable.
2. Style target: a small art guide (palette, silhouette, proportions,
   resolution, animation approach) and one hero asset tried in the game, on a
   phone, at real size.
3. Production art: only once gameplay, collision shapes, and sizes are frozen.

Art and animation are the most expensive things to redo. Polish feels like
progress but does not test fun; it is the classic way a solo developer stalls.
Pick the cheapest readable animation technique: frame-by-frame sprites for a
small character with few states; a skeletal/cutout rig only when the action
set is frozen and the character or animation count pays for it.

## Prioritization tools

- MoSCoW: Must / Should / Could / Won't. Must = the core experience does not
  exist without it.
- One-question test: "If I remove this, is the core loop still fun?" Yes → not Must.
- Pillars: 3-5 short principles; every feature names the pillar it serves.
- Scope ladder + cut list: ordered by value and cost, with what goes first
  written down before time runs short.

## Common mistakes (most-cited first)

1. Large scope, feature creep. 2. No clear core loop, or fun never proven.
3. No or late playtests. 4. Art, content, or polish before fun. 5. Building
tools/engine/tech instead of the game. 6. Rewriting or switching approach
midway. 7. Perfectionism; avoiding the dull last 10%.

Programmer traps: general systems before the game exists; implementing the
game like a product spec (feel is found through many cheap tries); testing the
logic but never the fun; putting clean structure before fast experiments.
