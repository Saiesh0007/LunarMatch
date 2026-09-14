# Agent Guidelines

## Running Tests

Full suite (may crash on Windows under memory pressure):
```bash
pytest tests/ -q
```

Recommended on Windows (isolates each test file to avoid native access violations):
```bash
python run_tests_isolated.py
```

Smoke test (end-to-end pipeline verification):
```bash
pytest tests/test_canary.py -v
```

