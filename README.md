HRIS Import Preview

Quick start

1. Create a Python virtualenv and activate it.

```bash
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
python manage.py runserver
```

2. Open http://127.0.0.1:8000/ and upload `Requirements/sample_hris.csv` from the Desktop.

Run tests

```bash
python manage.py test
```

Create submission ZIP

```bash
python package_project.py
```

Notes

- Parser logic lives in `preview/parser.py`.
- Tests are in `preview/tests.py`.
- Time spent: started scaffolding now; next steps: refine validation messages and add more tests.
 
Assumptions and limitations

- Small in-memory SQLite DB is used only for Django test harness; no persistence is written for uploads.
- Parser processes the entire CSV in memory; for very large files (100k+) streaming or incremental processing would be recommended.

AI tools used

- Assisted by an LLM-backed coding agent to scaffold the project and suggest parsing approaches; all code was reviewed and adjusted manually.

Recording notes

- See RECORDING_NOTES.md for an outline of the required 10-minute walkthrough.
