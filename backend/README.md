# Movers SAT Solver — Backend

A Python/FastAPI backend that solves the **movers problem** using SAT (Boolean satisfiability). Given a building with N floors and M movers, it finds the shortest plan for transporting items from upper floors down to floor 0 — or proves that no plan exists within a given time horizon.

## Problem Description

### Task 1 — Movement Only

All persons start at floor 0 and must reach specified goal floors within T time steps. Each step, a person can **ascend** one floor, **descend** one floor, or stay **idle**.

### Task 2 — Movement + Carrying

Extends Task 1 with items placed on various floors. All persons **and** all items must end at floor 0. Items can only be moved **downward**, one at a time, by a person who is descending. A person carrying an item cannot ascend.

## Architecture

```
backend/
├── app/
│   ├── main.py                  # FastAPI app, CORS, router mounting
│   ├── config.py                # Settings (solver, CORS, max time steps)
│   ├── models/
│   │   └── problem.py           # Pydantic models (input/output contracts)
│   ├── encoding/
│   │   ├── variables.py         # SAT variable definitions (IDPool)
│   │   ├── common_clauses.py    # CNF clause combinators (AMO, ALO, EO)
│   │   ├── task1_encoder.py     # Task 1 CNF encoder (groups A–F)
│   │   └── task2_encoder.py     # Task 2 CNF encoder (groups G–M)
│   ├── solver/
│   │   ├── runner.py            # Solver orchestration (fixed-T + optimal)
│   │   └── decoder.py           # SAT model → human-readable plan
│   ├── output/
│   │   ├── dimacs.py            # DIMACS CNF format serializer
│   │   └── mapping.py           # Variable mapping → JSON
│   └── api/
│       └── routes.py            # REST endpoints
├── cli.py                       # Command-line interface
├── tests/                       # pytest test suite
└── requirements.txt
```

### Pipeline

```
User Input (CLI or API)
        │
        ▼
ProblemConfig (Pydantic model)
        │
        ▼
CNF Encoder (Task 1 or Task 2)
        │
        ▼
SAT Solver (Glucose3 via python-sat)
        │
        ▼
Model Decoder → list[TimeStep]
        │
        ▼
Output (JSON response / DIMACS file / CLI display)
```

## SAT Encoding Reference

The problem is encoded as a CNF (Conjunctive Normal Form) formula using five propositional variable families:

| Variable | Meaning |
|----------|---------|
| `atFloor(person, floor, time)` | Person is at the given floor at the given time |
| `atFloor(item, floor, time)` | Item is at the given floor at the given time |
| `ascends(person, time)` | Person ascends one floor during this time step |
| `descends(person, time)` | Person descends one floor during this time step |
| `carries(person, item, time)` | Person carries item during this time step |

### Constraint Groups

**Task 1 constraints** (defined in `task1_encoder.py`):

| Group | Name | Description |
|-------|------|-------------|
| A | Initial state | All persons start at floor 0 |
| B | Goal state | Persons must be at target floors at time T |
| C | Unique floor | Each person at exactly one floor per time step |
| D | Action mutex | A person cannot ascend and descend simultaneously |
| E | Preconditions | Cannot ascend from top floor or descend from floor 0 |
| F | Effects + frame | Ascend/descend move by one floor; idle preserves position |

**Task 2 constraints** (defined in `task2_encoder.py`, extends A–F):

| Group | Name | Description |
|-------|------|-------------|
| G | Item initial state | Items start at their specified floors |
| H | Item goal state | All items must be at floor 0 at time T |
| I | Item unique floor | Each item at exactly one floor per time step |
| J | Carrying preconditions | Carrier and item must be co-located; carrying requires descending |
| K | Carrying mutex | Each person carries at most one item; each item carried by at most one person |
| L | Ascend precludes carry | A person cannot carry while ascending |
| M | Item successor-state | Carried items descend with their carrier; uncarried items stay put |

## Setup

### Requirements

- Python 3.11+
- pip

### Installation

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Running the API Server

```bash
uvicorn app.main:app --reload
```

The server starts at `http://localhost:8000`. API docs are auto-generated at `/docs` (Swagger UI) and `/redoc`.

### CLI Examples

```bash
# Task 2: 3 floors, 2 movers, 2 items
python cli.py --floors 3 --persons 2 --items chair:1 table:2

# Task 2: named movers, multiple items
python cli.py --floors 4 --persons 3 --names Joe Bill Mia \
    --items piano:3 sofa:2 lamp:1 box:2

# Task 1: 3 movers must reach floor 2
python cli.py --floors 3 --persons 3 --task 1 --goal-floor 2

# Solve at a specific time horizon
python cli.py --floors 3 --persons 2 --items chair:1 table:2 --fixed-t 5

# Save DIMACS CNF to file
python cli.py --floors 3 --persons 2 --items chair:1 table:2 --cnf-out problem.cnf
```

## API Endpoints

All routes are prefixed with `/api`.

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/api/solve` | Find the optimal (minimum-T) solution |
| `POST` | `/api/solve/fixed` | Solve at a specific time horizon T |
| `GET` | `/api/cnf/{solve_id}` | Retrieve DIMACS CNF for a previous solve |
| `GET` | `/api/mapping/{solve_id}` | Retrieve variable mapping for a previous solve |
| `GET` | `/api/health` | Health check |

### Example Request

```bash
curl -X POST http://localhost:8000/api/solve \
  -H "Content-Type: application/json" \
  -d '{
    "task": 2,
    "num_floors": 3,
    "num_persons": 2,
    "items": [
      {"name": "chair", "initial_floor": 1},
      {"name": "table", "initial_floor": 2}
    ]
  }'
```

## Testing

```bash
cd backend
pytest
```

The test suite covers SAT encoding correctness (Task 1 and Task 2), variable pool consistency, API endpoint integration, and edge cases (trivial/unsatisfiable instances).
