# v1.9 Multi-Answer Normal Mode Design

## Goal

Add a new difficulty/play mode where each round can hide 1-5 correct answers under cups. The number of cups must be at least the number of correct answers plus 2, and can be set higher by the teacher.

## Scope

v1.9 implements one rule set only: **Normal multi-answer mode**.

Included:

- Settings screen has two sliders: `Answers` and `Cups`
- `Answers` supports 1-5
- `Cups` automatically moves to at least `Answers + 2`, but can be adjusted higher
- Settings screen keeps `Rounds` and `Speed` sliders below those two controls
- each round randomly selects N distinct target items and N distinct target cups
- player gets exactly N clicks when there are N answers
- after N selections, the round is scored
- all selected cups correct → +1 point
- any selected cup wrong → 0 points and reveal all correct cups
- settings page, game flow, scoreboard flow, replay/adjust behavior continue to work

Excluded:

- separate Strict mode where one wrong click fails immediately
- independently adjustable cup count
- partial scoring for selecting some correct answers
- per-answer scoring
- row-level editing of imported items

## Settings UI

Use four sliders in the left settings card:

1. `Answers` — range 1-5
2. `Cups` — range starts at `Answers + 2`, up to the configured max
3. `Rounds`
4. `Speed`

When the teacher increases `Answers`, `Cups` immediately moves up if needed so it is never below `Answers + 2`. The teacher can still move `Cups` higher afterward.

A short helper line under `Answers` should explain:

```text
Cups need at least N; you can add more.
```

## Game Rules

For `answer_count = N`:

1. prepare N target items from the available item list
2. prepare N target cups from the current cups
3. show the N targets during the intro phase
4. hide one target under each target cup
5. shuffle as usual
6. enter guessing state
7. allow the player to select up to N distinct cups
8. once N cups are selected, enter reveal/scoring
9. score +1 if selected cups exactly match target cups, otherwise 0
10. reveal all target cups before moving to the next round

If the item list has fewer than N unique items, reuse available items as needed rather than blocking the game. This keeps classroom flow simple.

## Intro Display

For v1.9, the intro can show multiple target cards together in the center. It does not need separate fly-in animations per target. The important requirement is that students can clearly see all targets before shuffling.

## Feedback Copy

Examples:

- Intro caption: `Memorize these!`
- Guessing prompt: `Pick 2 cups hiding the targets`
- Progress hint: `1 / 2 selected`
- Correct: `Correct! You found them all!`
- Wrong: `Not quite — here are the answers.`

## Verification

- parser/import behavior from v1.7/v1.8 should still work
- settings smoke for all answer counts 1/2/3
- game smoke for 1 answer, 2 answers, 3 answers
- click simulation for all-correct and one-wrong selections
- `python3 -m compileall main.py game`
- Windows exe confirmation after push
