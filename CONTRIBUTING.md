# Contributing

Thanks for your interest in OptiMove! This was built as a university project for the
*Theory of Computation* course. Issues and pull requests are welcome.

## Development setup

```bash
# Backend
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
pytest

# Frontend
cd frontend
npm ci
npm run dev
```

Or run the full stack with `docker compose up --build`.

## Before opening a pull request

CI runs the same checks, so run them locally first:

| Area     | Command                                                                                  |
|----------|------------------------------------------------------------------------------------------|
| Backend  | `cd backend && pytest`                                                                   |
| Frontend | `cd frontend && npm run check:lint && npm run check:format && npm test && npm run build` |
| Format   | `cd frontend && npm run format` (auto-fix)                                               |

## Guidelines

- Keep the SAT encoding groups (A–M) documented: if you add or change a constraint,
  update the docstring of the encoder and the table in [`backend/README.md`](backend/README.md).
- Add a test for every bug fix (see `backend/tests/` and `frontend/tests/`).
- Use clear commit messages in the imperative mood ("Add …", "Fix …").
