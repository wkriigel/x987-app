For all x987 tasks:

- Windows PowerShell only. Start with a 1–2 line Plan, then Numbered Steps.
- File edits via Set-Content -Encoding UTF8 or PowerShell -replace regex. Always close here-strings with @' and '@.
- Single-purpose changes ≤50 lines. Branch per change (feat/…, fix/…, chore/…).
- Run order: ruff check ., pytest -q, (python -m x987 only when scraper/pipeline changed or when I ask).
- Do NOT propose or modify lint configs, pre-commit, prettier, or any tooling unless I ask explicitly.
- Lint only changed files; never repo-wide refactors. No style crusades. No sweeping wraps.
- Focus on x987/scrapers/* and tests/* for scraper work; avoid touching unrelated files.
- If a command fails: STOP. Give the smallest fallback or micro-branch plan (no redesigns).
