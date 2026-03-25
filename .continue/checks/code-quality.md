# Code Quality Check

Run these commands and verify all pass before merging:

## Linting

```bash
uv run ruff check src/
```

Expected: `All checks passed!`

## Type Checking

```bash
uv run mypy src/
```

Expected: `Success: no issues found in N source files`

## Failure Criteria

- Any ruff error → FAIL
- Any mypy error → FAIL
- `error:` or `warning:` in mypy output → FAIL
