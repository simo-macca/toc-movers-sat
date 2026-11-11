"""Invalid input must be rejected instead of producing a wrong SAT/UNSAT answer."""

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from app.encoding.task1_encoder import encode_task1
from app.main import app
from app.models.problem import ItemPlacement, ProblemConfig

client = TestClient(app)

BASE = {"task": 2, "num_floors": 3, "num_persons": 2}


@pytest.mark.parametrize(
    "payload",
    [
        {**BASE, "task": 7},
        {**BASE, "num_persons": -1},
        {**BASE, "num_persons": 0},
        {**BASE, "num_floors": 0},
        {**BASE, "items": [{"name": "x", "initial_floor": 7}]},
        {**BASE, "items": [{"name": "x", "initial_floor": -1}]},
        {**BASE, "items": [{"name": "a", "initial_floor": 1}, {"name": "a", "initial_floor": 2}]},
        {**BASE, "person_names": ["OnlyOne"]},
        {**BASE, "person_names": ["Joe", "Joe"]},
        {**BASE, "task": 1, "goal_floors": {"0": 9}},
        {**BASE, "task": 1, "goal_floors": {"5": 1}},
        {**BASE, "max_steps": -1},
    ],
)
def test_invalid_solve_requests_return_422(payload):
    resp = client.post("/api/solve", json=payload)
    assert resp.status_code == 422, resp.text


def test_fixed_requires_non_negative_time_steps():
    resp = client.post("/api/solve/fixed", json={**BASE, "time_steps": -2})
    assert resp.status_code == 422


def test_task1_ignores_items():
    resp = client.post(
        "/api/solve",
        json={**BASE, "task": 1, "goal_floors": {"0": 1, "1": 1},
              "items": [{"name": "box", "initial_floor": 2}]},
    )
    assert resp.status_code == 200
    assert resp.json()["result"]["num_time_steps"] == 1


def test_problem_config_rejects_out_of_range_item():
    with pytest.raises(ValidationError):
        ProblemConfig(num_floors=2, num_persons=1,
                      items=[ItemPlacement(name="box", initial_floor=2)])


def test_encoder_rejects_out_of_range_goal():
    with pytest.raises(ValueError):
        encode_task1(num_floors=3, num_persons=1, T=2, goal_floors={0: 9})
