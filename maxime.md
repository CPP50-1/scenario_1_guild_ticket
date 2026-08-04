# Ticket #GLD-142 — Filter the roster to show only active members

## Chosen solution

Added `active_characters()` on `Roster`: a generator that only yields
characters with `status == "active"`, following the same style as the existing
`alive_characters()` method.

To implement it, `Character` now has a `status` field with a new
`ChoiceField` descriptor (a subclass of `StringField`) that only accepts
`active`, `benched`, `retired` (default: `active`). An invalid value raises
`InvalidChoiceError`.

## Why

- Same pattern as `alive_characters()`: a filtered generator over the roster.
- Validation lives in the field, consistent with the existing descriptor mechanism.
- `InvalidChoiceError` inherits from `ValidationError`, so a single `except` is
  enough.
- On the SQL side, the `character` table already has `status` with the same
  values and the same default: the Python model now matches the schema.

## Verification

All 48 existing tests pass + 1 new test for the active filter.
