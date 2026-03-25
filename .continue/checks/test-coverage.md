# Test Coverage Check

Run the full test suite with coverage and verify results:

```bash
uv run pytest --cov=src/anti_slop_writer --cov-report=term-missing -q
```

## Pass Criteria

- All tests pass (0 failures, 0 errors)
- Total coverage >= 80%
- `openai_compatible.py` coverage >= 70%
- `rewriter.py` coverage = 100%
- `rule_engine.py` coverage = 100%

## Failure Criteria

- Any test failure → FAIL
- Total coverage < 80% → FAIL
- Skipped tests must have `@pytest.mark.skip(reason=...)` with explanation

## Security

- No API keys or secrets in test output
- No real HTTP calls to external services (all mocked)
