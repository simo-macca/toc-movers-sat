# OptiMove | SAT Logistics Solver

A full-stack web application and SAT-encoding engine designed to optimally solve the "Movers" logistics problem. Developed for the Theory of Computation course, this project leverages **Boolean Satisfiability (SAT)** to compute the shortest possible plan for transporting movers and items across multiple floors.

## The Problem

Given a building with $N$ floors, $M$ movers, and various items, the goal is to transport everyone and everything to the ground floor (Floor 0) while minimizing the total time steps ($T$).

- **Task 1 (Movement):** Movers start at Floor 0 and must navigate to specific target floors. Movers can ascend, descend, or stay idle.
- **Task 2 (Logistics):** Movers must retrieve items scattered across upper floors. Items can only be carried downwards, one at a time, by a descending mover.

## System Architecture

This repository is organized into a clean, decoupled full-stack architecture:

- **`/backend` (Python / FastAPI):** The computational core. It translates human-readable problem configurations into DIMACS CNF format, invokes the `Glucose3` SAT solver, decodes the satisfying assignments back into a logistics plan, and serves the results via a RESTful API.
  - _Tech Stack:_ FastAPI, Pydantic, PycoSAT (Glucose-3).
- **`/frontend` (Vue 3 / Vite):** The interactive user interface. It provides a state-driven configuration panel, advanced solver options, and a custom-built, animated "elevator-shaft" visualizer to play back the computed logistics timeline.
  - _Tech Stack:_ Vue 3 (Composition API), Tailwind CSS, Vite.

## Quick Start (Docker)

The absolute easiest way to run the entire application, without worrying about Python virtual environments, Node.js versions, or dependency conflicts, is using **Docker Compose**.

### Prerequisites

- [Docker](https://www.docker.com/) and Docker Compose installed on your system.

### Running the Application

1. Clone the repository and navigate to the root folder:

   ```bash
   git clone git@github.com:simo-macca/ToC_movers.git
   cd toc_movers
   ```

2. Build and spin up the containers:

   ```bash
   docker-compose up --build
   ```

3. Open your browser and navigate to:
   - **Frontend UI:** [http://localhost:3000](https://www.google.com/search?q=http://localhost:3000)
   - **Backend API Docs:** [http://localhost:8000/docs](https://www.google.com/search?q=http://localhost:8000/docs)

_To stop the servers, simply press `Ctrl+C` in your terminal._

## Advanced Engine Features

This application exposes powerful SAT-solving capabilities directly through the UI and API:

- **Iterative Deepening (Optimal Solve):** Automatically searches for the absolute minimum number of steps required to complete the task by iteratively increasing the time horizon $T$.
- **Fixed Horizon (Bounded Solve):** Tests if a valid logistics plan exists within an exact, user-specified time limit.
- **Logic Export:** Directly download the raw `DIMACS CNF` constraints and the `Variable Mapping` JSON from the frontend for academic review and debugging.
- **Parametrized Encodings:** Highly dynamic logic generation supporting custom mover names, customizable floor limits, and flexible item placements.

## Native Development Setup (Alternative)

If you prefer to run the applications natively outside of Docker, you can start the services manually.t

### Terminal 1: Start the Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # On Windows use: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Terminal 2: Start the Frontend

```bash
cd frontend
npm install
npm run dev
```

## Test Cases

The following five scenarios exercise the encoder across both tasks of the lab specification. Each one can be reproduced directly from the frontend configuration panel or via the backend API; the optimal time horizon $T^*$ is the value returned by the iterative-deepening solver.

### 1. Task 1 — Three movers climb to the top floor ($T^* = 2$)

The canonical movement-only instance from the lab handout. Joe, Bill, and Mia all start on floor 0 and must reach floor 2 in a building with $m = n = 3$.

- `num_floors = 3`, `num_persons = 3`, `person_names = ["Joe", "Bill", "Mia"]`
- `goal_floors = {Joe: 2, Bill: 2, Mia: 2}`
- Expected: SAT, every mover performs `ascends` at $t = 0$ and $t = 1$.

### 2. Task 2 — Three items from Fig. 1 to the ground floor ($T^* = 4$)

The minimal carrying instance from the handout: flowerpot and table start on floor 2, chair starts on floor 1.

- `num_floors = 3`, `num_persons = 3`, `person_names = ["Joe", "Bill", "Mia"]`
- `items = [(flowerpot, 2), (chair, 1), (table, 2)]`
- Expected: SAT in 4 steps; all persons and items end on floor 0.

### 3. Task 2 — Full Fig. 1 configuration with all five items ($T^* = 6$)

The complete initial configuration depicted in Fig. 1 of the handout: flowerpot, table, and sofa on floor 2; chair and piano on floor 1. Since only three movers are available and each can carry at most one item per descent, the optimal plan requires six steps.

- `num_floors = 3`, `num_persons = 3`
- `items = [(flowerpot, 2), (chair, 1), (table, 2), (piano, 1), (sofa, 2)]`
- Expected: SAT in 6 steps.

### 4. Bounded solve — Infeasible horizon (UNSAT)

A negative test that confirms the encoder correctly rejects under-constrained horizons. Using the configuration from test case 2 with a fixed horizon of $T = 3$, no valid plan exists: two items sit on floor 2, but at most three downward carries can occur in three steps and the movers must first ascend.

- Same configuration as test case 2.
- Solver mode: **Fixed Horizon** with $T = 3$.
- Expected: UNSAT.

### 5. Edge case — Single mover, single item ($T^* = 2$)

The smallest non-trivial Task 2 instance, useful for sanity-checking the carry encoding and for inspecting the DIMACS export without combinatorial noise.

- `num_floors = 2`, `num_persons = 1`, `items = [(box, 1)]`
- Expected: SAT in 2 steps — `ascends` at $t = 0$, then `carries(person_0, box)` at $t = 1$.
