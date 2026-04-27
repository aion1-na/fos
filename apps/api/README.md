# API

Owner: Platform API

Test command: `uv run pytest tests/test_api_health.py -v`

Definition of done:

- FastAPI endpoints expose OpenAPI metadata.
- No endpoint hardcodes real credentials.
- Contract-facing responses are versioned.
- Health and feature tests pass.
