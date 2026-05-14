from pysat.formula import IDPool

from app.encoding.variables import (
    at_floor_person,
    at_floor_item,
    ascends,
    descends,
    carries,
    build_mapping,
)


def test_idpool_consistency():
    pool = IDPool()
    v1 = at_floor_person(pool, 0, 1, 2)
    v2 = at_floor_person(pool, 0, 1, 2)
    assert v1 == v2

    v3 = at_floor_person(pool, 0, 2, 2)
    assert v1 != v3


def test_different_variable_families():
    pool = IDPool()
    v1 = at_floor_person(pool, 0, 0, 0)
    v2 = at_floor_item(pool, "chair", 0, 0)
    v3 = ascends(pool, 0, 0)
    v4 = descends(pool, 0, 0)
    v5 = carries(pool, 0, "chair", 0)
    all_ids = {v1, v2, v3, v4, v5}
    assert len(all_ids) == 5


def test_build_mapping():
    pool = IDPool()
    at_floor_person(pool, 0, 1, 0)
    ascends(pool, 0, 0)
    carries(pool, 1, "table", 2)

    mapping = build_mapping(pool, ["Joe", "Bill", "Mia"])
    values = list(mapping.values())
    assert "atFloor(Joe, 1, 0)" in values
    assert "ascends(Joe, 0)" in values
    assert "carries(Bill, table, 2)" in values
