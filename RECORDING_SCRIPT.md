Recording script (suggested narration)

Intro (15s):
- "Hi, this is [Your Name]. I'll demo the HRIS Import Preview I implemented for Diversio."

Demo (1:45):
- Show upload page, upload the sample CSV, explain summary numbers and point to rows with errors.
- Show managers/direct-report counts and roots.

Code walkthrough (4:15):
- Open `preview/parser.py` and explain steps: normalization, identity checks, manager lookup, building edges, cycle detection.
- Explain error codes and how invalid rows are excluded from hierarchy edges.

Tests (2:00):
- Run `python manage.py test preview` and show tests passing. Explain what each test asserts.

Wrap-up (0:45):
- Discuss known limitations, improvements (streaming large files, UI filters), and how AI was used.
- Thank you.
