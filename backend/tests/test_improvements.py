"""Tests for the lower bound, UNSAT exports, stats, cache and CLI."""

import json
import subprocess
import sys
from pathlib import Path

from fastapi.testclient import TestClient

from app.api.routes import _ResultCache
from app.main import app
from app.models.problem import ItemPlacement, ProblemConfig
from app.solver.runner import horizon_lower_bound, solve_fixed, solve_optimal

client = TestClient(app)
BACKEND = Path(__file__).resolve().parents[1]

FIG1 = ProblemConfig(
    num_floors=3,
    num_persons=3,
    items=[
        ItemPlacement(name="flowerpot", initial_floor=2),
        ItemPlacement(name="chair", initial_floor=1),
        ItemPlacement(name="table", initial_floor=2),
    ],
)


def test_lower_bound_is_valid_and_skips_horizons():
    lb = horizon_lower_bound(FIG1, task=2)
    assert lb == 4
    for T in range(lb):
        assert solve_fixed(FIG1, 2, T).satisfiable is False
    result = solve_optimal(FIG1, task=2)
    assert result.num_time_steps == 4
    assert result.stats.horizons_tried == 1


def test_lower_bound_task1():
    cfg = ProblemConfig(num_floors=4, num_persons=2)
    assert horizon_lower_bound(cfg, 1, {0: 3, 1: 1}) == 3
    assert horizon_lower_bound(cfg, 1, None) == 0


def test_unsat_optimal_reports_real_stats():
    result = solve_optimal(FIG1, task=2, max_T=2)
    assert result.satisfiable is False
    assert result.num_time_steps == 2
    assert result.stats.num_variables > 0
    assert result.cnf_dimacs.startswith("c ")


def test_unsat_cnf_downloadable_via_api():
    resp = client.post("/api/solve/fixed", json={
        "task": 2, "num_floors": 3, "num_persons": 3, "time_steps": 3,
        "items": [{"name": "flowerpot", "initial_floor": 2},
                  {"name": "chair", "initial_floor": 1},
                  {"name": "table", "initial_floor": 2}],
    })
    assert resp.status_code == 200
    body = resp.json()
    assert body["result"]["satisfiable"] is False
    # Large artefacts are not inlined in the response anymore
    assert "cnf_dimacs" not in body["result"]
    assert "variable_mapping" not in body["result"]

    cnf = client.get(f"/api/cnf/{body['solve_id']}")
    assert cnf.status_code == 200
    assert "p cnf" in cnf.json()["cnf"]
    mapping = client.get(f"/api/mapping/{body['solve_id']}")
    assert mapping.status_code == 200


def test_health_reports_configured_solver():
    data = client.get("/api/health").json()
    assert data["solver"] == "glucose3"
    assert "version" in data


def test_result_cache_is_bounded_lru():
    cache = _ResultCache(max_size=2)
    cache.put("a", 1)
    cache.put("b", 2)
    cache.get("a")          # "a" becomes most recently used
    cache.put("c", 3)       # evicts "b"
    assert cache.get("b") is None
    assert cache.get("a") == 1 and cache.get("c") == 3
    assert len(cache) == 2


def _cli(*args, cwd):
    return subprocess.run(
        [sys.executable, str(BACKEND / "cli.py"), *args],
        cwd=cwd, capture_output=True, text=True,
    )


def test_cli_solves_and_exports(tmp_path):
    proc = _cli("--floors", "2", "--persons", "1", "--items", "box:1",
                "--cnf-out", "out.cnf", "--mapping-out", "out.json", cwd=tmp_path)
    assert proc.returncode == 0, proc.stderr
    assert "SATISFIABLE in 2 time steps" in proc.stdout
    assert "p cnf" in (tmp_path / "out.cnf").read_text()
    assert json.loads((tmp_path / "out.json").read_text())


def test_cli_unsat_still_exports_cnf(tmp_path):
    proc = _cli("--floors", "3", "--persons", "3",
                "--items", "flowerpot:2", "chair:1", "table:2",
                "--fixed-t", "3", "--cnf-out", "unsat.cnf", cwd=tmp_path)
    assert proc.returncode == 1
    assert "UNSATISFIABLE" in proc.stdout
    assert (tmp_path / "unsat.cnf").exists()


def test_cli_rejects_invalid_input(tmp_path):
    proc = _cli("--floors", "2", "--persons", "1", "--items", "box:5", cwd=tmp_path)
    assert proc.returncode == 2
    assert "floor" in proc.stderr


def test_solver_timeout_returns_504(monkeypatch):
    from app.config import settings

    monkeypatch.setattr(settings, "solver_timeout_seconds", 0.01)
    resp = client.post("/api/solve", json={
        "task": 2, "num_floors": 6, "num_persons": 2,
        "items": [{"name": f"box{i}", "initial_floor": 5} for i in range(8)],
        "max_steps": 60,
    })
    assert resp.status_code == 504
