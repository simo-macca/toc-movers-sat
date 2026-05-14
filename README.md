# OptiMove | SAT Logistics Solver 📦🤖

A full-stack web application and SAT-encoding engine designed to optimally solve the "Movers" logistics problem. Developed for the Theory of Computation course, this project leverages **Boolean Satisfiability (SAT)** to compute the shortest possible plan for transporting movers and items across multiple floors.

## 📖 The Problem

Given a building with $N$ floors, $M$ movers, and various items, the goal is to transport everyone and everything to the ground floor (Floor 0) while minimizing the total time steps ($T$).

* **Task 1 (Movement):** Movers start at Floor 0 and must navigate to specific target floors. Movers can ascend, descend, or stay idle.
* **Task 2 (Logistics):** Movers must retrieve items scattered across upper floors. Items can only be carried downwards, one at a time, by a descending mover.

## 🏗️ System Architecture

This repository is organized into a clean, decoupled full-stack architecture:

* **`/backend` (Python / FastAPI):** The computational core. It translates human-readable problem configurations into DIMACS CNF format, invokes the `Glucose3` SAT solver, decodes the satisfying assignments back into a logistics plan, and serves the results via a RESTful API.
  * *Tech Stack:* FastAPI, Pydantic, PycoSAT (Glucose-3).
* **`/frontend` (Vue 3 / Vite):** The interactive user interface. It provides a state-driven configuration panel, advanced solver options, and a custom-built, animated "elevator-shaft" visualizer to play back the computed logistics timeline.
  * *Tech Stack:* Vue 3 (Composition API), Tailwind CSS, Vite.

## 🚀 Quick Start (Docker)

The absolute easiest way to run the entire application, without worrying about Python virtual environments, Node.js versions, or dependency conflicts, is using **Docker Compose**.

### Prerequisites

* [Docker](https://www.docker.com/) and Docker Compose installed on your system.

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

    * **Frontend UI:** [http://localhost:3000](https://www.google.com/search?q=http://localhost:3000)
    * **Backend API Docs:** [http://localhost:8000/docs](https://www.google.com/search?q=http://localhost:8000/docs)

*To stop the servers, simply press `Ctrl+C` in your terminal.*

## ⚙️ Advanced Engine Features

This application exposes powerful SAT-solving capabilities directly through the UI and API:

* **Iterative Deepening (Optimal Solve):** Automatically searches for the absolute minimum number of steps required to complete the task by iteratively increasing the time horizon $T$.
* **Fixed Horizon (Bounded Solve):** Tests if a valid logistics plan exists within an exact, user-specified time limit.
* **Logic Export:** Directly download the raw `DIMACS CNF` constraints and the `Variable Mapping` JSON from the frontend for academic review and debugging.
* **Parametrized Encodings:** Highly dynamic logic generation supporting custom mover names, customizable floor limits, and flexible item placements.

## 👨‍💻 Native Development Setup (Alternative)

If you prefer to run the applications natively outside of Docker, you can start the services manually.

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
