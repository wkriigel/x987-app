# Options pipeline

- The v2 catalog lives in config under `options_v2.catalog`.
- Each item supports `synonyms` (regex or plain terms).
- Pipeline writes:
    - `top5_options_present` (labels)
    - `top5_options_count`

## Editing the catalog

- Add new synonyms for real world listing phrases.
- Keep labels short; UI shows "Top Options".
