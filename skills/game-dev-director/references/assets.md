# Asset Workflow

Treat final visual/audio assets as product decisions, not incidental code output.

## When

Art timing (placeholder → style target → production) and choosing an animation
technique: `references/phases-and-ladder.md` → Art timing.

## Visual assets

When an external/generated asset is needed:
- define purpose and in-game size/context;
- preserve approved proportions/perspective/style when iterating;
- provide a precise generation/edit prompt when the user will generate it elsewhere;
- inspect only the actual local file once the user places it in the project;
- keep source/master assets separate from runtime-optimized exports where appropriate.

Do not claim an asset exists until it is actually available locally.

## Integration

Check:
- dimensions/aspect;
- transparency/background;
- import settings;
- naming;
- runtime scaling;
- filtering/compression;
- light/dark/theme variants if relevant.

## Audio

Check:
- license/provenance when relevant;
- loop vs one-shot;
- volume/mute routing;
- mobile/browser autoplay/platform constraints;
- import/compression behavior.

The user judges subjective visual/audio results in play.
