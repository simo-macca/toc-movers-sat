from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health():
    resp = client.get("/api/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


def test_solve_task1():
    resp = client.post("/api/solve", json={
        "task": 1,
        "num_floors": 3,
        "num_persons": 3,
        "person_names": ["Joe", "Bill", "Mia"],
        "goal_floors": {"0": 2, "1": 2, "2": 2},
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["result"]["satisfiable"] is True
    assert data["result"]["num_time_steps"] == 2
    assert "solve_id" in data


def test_solve_task2():
    resp = client.post("/api/solve", json={
        "task": 2,
        "num_floors": 3,
        "num_persons": 3,
        "person_names": ["Joe", "Bill", "Mia"],
        "items": [
            {"name": "flowerpot", "initial_floor": 2},
            {"name": "chair", "initial_floor": 1},
            {"name": "table", "initial_floor": 2},
        ],
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["result"]["satisfiable"] is True
    assert data["result"]["num_time_steps"] == 4


def test_cnf_endpoint():
    solve_resp = client.post("/api/solve", json={
        "task": 1,
        "num_floors": 2,
        "num_persons": 1,
        "goal_floors": {"0": 1},
    })
    solve_id = solve_resp.json()["solve_id"]

    cnf_resp = client.get(f"/api/cnf/{solve_id}")
    assert cnf_resp.status_code == 200
    assert "p cnf" in cnf_resp.json()["cnf"]


def test_mapping_endpoint():
    solve_resp = client.post("/api/solve", json={
        "task": 1,
        "num_floors": 2,
        "num_persons": 1,
        "goal_floors": {"0": 1},
    })
    solve_id = solve_resp.json()["solve_id"]

    map_resp = client.get(f"/api/mapping/{solve_id}")
    assert map_resp.status_code == 200
    assert len(map_resp.json()["mapping"]) > 0


def test_cnf_not_found():
    resp = client.get("/api/cnf/nonexistent")
    assert resp.status_code == 404
