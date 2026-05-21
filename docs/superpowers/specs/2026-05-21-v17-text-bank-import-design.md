# v1.7 Text Question Bank Import Design

## Goal

Add a small, safe first version of question-bank loading: import plain text items from a numbered `.txt` file into the existing Settings screen item list.

## Scope

v1.7 only supports text items.

Included:

- add an `Import Text` action on the Settings screen
- open a `.txt` file with the existing tkinter file dialog pattern
- parse common teacher-friendly list formats
- append parsed text items to `manual_items`
- keep the Settings screen open so the teacher can review, delete, or manually add more items
- commit and tag the result as `v1.7`

Excluded:

- image folder import
- image references inside the text file
- JSON import UI
- automatic game start after import
- editing an existing row in place
- duplicate detection or automatic cleanup

## Supported File Format

Recommended format:

```text
1. apple
2. banana
3. cat
4. dog
```

Also accepted:

```text
1 apple
1) apple
1、apple
- apple
apple
```

Parsing rules:

- read the file as UTF-8, with a simple fallback for common local encodings if needed
- split by line
- trim whitespace
- skip blank lines
- remove one leading list marker if present: `1.`, `1)`, `1、`, `1 `, `-`, `*`
- keep the remaining text exactly enough for classroom use, after trimming surrounding whitespace
- create each item as `{"type": "text", "content": text, "hint": ""}`
- preserve file order
- do not deduplicate

## User Flow

1. Teacher clicks `Import Text` in `Your Items`.
2. File dialog opens for `.txt` files.
3. Teacher chooses a file.
4. Program parses valid lines and appends them to the current item list.
5. Settings screen stays open.
6. Teacher can delete rows, add more words, adjust cups/rounds/speed, then click `Start Game!` manually.

If the file is empty, cancelled, or has no valid lines, the current list remains unchanged.

## UI Placement

Keep the current Settings layout. The `Your Items` top row should still prioritize manual text entry. Add `Import Text` as a second compact button near the existing `Image` button or in the same right-card action area, without changing game flow.

## Error Handling

No modal error system is required for v1.7. Fail softly:

- cancelled dialog: no change
- unreadable file: no change
- empty file: no change
- invalid lines only: no change

The implementation may store a short import status message for future UI polish, but v1.7 does not require a visible toast.

## Verification

- unit-level parser checks using small temporary text files or direct parser inputs
- `python3 -m compileall main.py game`
- headless Settings screen smoke check with import parser output feeding `manual_items`
- Windows exe final confirmation after push
