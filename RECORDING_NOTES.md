Recording walkthrough notes (<=10 minutes)

1) Demo (2 minutes)
- Open http://127.0.0.1:8000/ and upload `Requirements/sample_hris.csv`.
- Show the summary counts, row-level errors, managers table, accepted employees, and cycles.

2) Code walkthrough (5 minutes)
- Open `preview/parser.py` and explain:
  - normalization (_normalize)
  - identity checks (missing / duplicate handling)
  - manager lookup rules and how conflicts are detected
  - building edges and cycle detection (DFS stack-based detection)
- Show `preview/views.py` to trace upload -> parse -> template rendering.
- Show `templates/upload.html` for how results are presented.

3) Tests (2 minutes)
- Open `preview/tests.py` and run tests.
- Explain what each test verifies (normalization, duplicates, cycles, manager conflicts, BOM handling).

4) Improvements & trade-offs (1 minute)
- Mention streaming large files, better UX, more detailed error categories, and stronger type validation.
- Note time spent and AI assistance used.
