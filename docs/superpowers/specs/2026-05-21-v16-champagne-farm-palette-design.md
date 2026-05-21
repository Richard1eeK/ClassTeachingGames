# v1.6 Champagne Farm Palette Design

## Goal

Refresh the v1.4 pixel UI palette so it feels lighter, cleaner, and more premium instead of dark, old, or antique.

## Scope

Only colors change in this part:

- update theme color tokens in `game/theme.py`
- recolor or regenerate existing pixel assets under `assets/pixel/`
- keep the current layout, interactions, game flow, typography scale, and component structure unchanged

## Selected Direction

Use **Champagne Farm**: a light luxury farm palette that keeps the cozy classroom-game personality while removing the aged dark-wood feel.

Core palette intent:

- warm cream background instead of saturated dark orange wood
- ivory/champagne panels instead of dark parchment yellow
- champagne gold for emphasis, stars, buttons, and premium edges
- sage green and mist blue as soft secondary accents
- restrained warm brown outlines for pixel readability

## What To Avoid

- dark orange/brown backgrounds that read as old wood
- dirty parchment tones or heavy shadowing
- overly corporate white/blue styling that loses the playful farm-game feel
- neon candy colors that conflict with the light luxury direction
- layout or interaction changes in this version

## Implementation Notes

The existing token names should stay stable where possible so the change remains low-risk. Any PNG updates should preserve the same filenames and dimensions so existing draw code does not need structural changes.

## Verification

- run Python compile check for `main.py` and `game/`
- run the existing headless pygame smoke check if available
- inspect generated/updated assets visually where possible
- Windows exe visual confirmation remains the final check after push
