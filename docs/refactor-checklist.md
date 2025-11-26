# Refactor checklist (initial)

This file captures issues found by static analysis (ruff) and proposed small refactors. It is automatically populated with the current linter output.

## ruff lint output (run on the project's venv)

All checks passed!

## Suggested small refactors and next steps

- Keep `typo/app.py` modular: consider extracting storage (JSON read/write) into a separate `storage.py` module to make it easier to unit test and to replace with a DB later.
- Add simple input validation for uploads (limit file size, restrict allowed extensions) and test cases for those checks.
- Add a small integration test that asserts `/metrics` and `/health` endpoints return 200 and expected fields (already added earlier, ensure persisted).
- Consider adding type hints to the main `typo` modules (small, incremental) to improve maintainability.

If you want, I can start extracting `storage` or add the upload validation next (low-risk, testable changes).

-- lint output will be added below --

