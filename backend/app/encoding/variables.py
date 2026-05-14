"""Propositional variable definitions for the movers SAT encoding.

Each function registers (or retrieves) a unique integer ID in a PySAT
``IDPool`` for a Boolean proposition.  Five variable families exist:

* **atFloor_person** -- person *p* is at floor *f* at time *t*
* **atFloor_item**   -- item *i* is at floor *f* at time *t*
* **ascends**        -- person *p* ascends one floor during step *t*
* **descends**       -- person *p* descends one floor during step *t*
* **carries**        -- person *p* carries item *i* during step *t*
"""

from pysat.formula import IDPool


def at_floor_person(pool: IDPool, person: int, floor: int, time: int) -> int:
    """Return the variable ID for "person ``person`` is at floor ``floor`` at time ``time``."

    Args:
        pool: Shared variable pool.
        person: Person index.
        floor: Floor index (0-based).
        time: Time step index.

    Returns:
        Unique positive integer variable ID.
    """
    return pool.id(("afp", person, floor, time))


def at_floor_item(pool: IDPool, item: str, floor: int, time: int) -> int:
    """Return the variable ID for "item ``item`` is at floor ``floor`` at time ``time``."

    Args:
        pool: Shared variable pool.
        item: Item name.
        floor: Floor index (0-based).
        time: Time step index.

    Returns:
        Unique positive integer variable ID.
    """
    return pool.id(("afi", item, floor, time))


def ascends(pool: IDPool, person: int, time: int) -> int:
    """Return the variable ID for "person ``person`` ascends one floor during step ``time``."

    Args:
        pool: Shared variable pool.
        person: Person index.
        time: Time step index.

    Returns:
        Unique positive integer variable ID.
    """
    return pool.id(("asc", person, time))


def descends(pool: IDPool, person: int, time: int) -> int:
    """Return the variable ID for "person ``person`` descends one floor during step ``time``."

    Args:
        pool: Shared variable pool.
        person: Person index.
        time: Time step index.

    Returns:
        Unique positive integer variable ID.
    """
    return pool.id(("desc", person, time))


def carries(pool: IDPool, person: int, item: str, time: int) -> int:
    """Return the variable ID for "person ``person`` carries item ``item`` during step ``time``."

    Args:
        pool: Shared variable pool.
        person: Person index.
        item: Item name.
        time: Time step index.

    Returns:
        Unique positive integer variable ID.
    """
    return pool.id(("car", person, item, time))


def build_mapping(pool: IDPool, person_names: list[str]) -> dict[int, str]:
    """Build a human-readable mapping from variable IDs to symbolic names.

    Iterates over every variable registered in ``pool`` and translates
    its internal tuple into a descriptive string such as
    ``"atFloor(Joe, 1, 0)"`` or ``"carries(Bill, chair, 2)"``.

    Args:
        pool: Variable pool containing all registered variables.
        person_names: Display names for persons, indexed by person ID.
            Falls back to ``"person_<idx>"`` when the index is out of range.

    Returns:
        Dictionary mapping each integer variable ID to its symbolic name.
    """
    mapping = {}
    for obj, var_id in pool.obj2id.items():
        kind = obj[0]
        if kind == "afp":
            _, p, f, t = obj
            pname = person_names[p] if p < len(person_names) else f"person_{p}"
            mapping[var_id] = f"atFloor({pname}, {f}, {t})"
        elif kind == "afi":
            _, item, f, t = obj
            mapping[var_id] = f"atFloor({item}, {f}, {t})"
        elif kind == "asc":
            _, p, t = obj
            pname = person_names[p] if p < len(person_names) else f"person_{p}"
            mapping[var_id] = f"ascends({pname}, {t})"
        elif kind == "desc":
            _, p, t = obj
            pname = person_names[p] if p < len(person_names) else f"person_{p}"
            mapping[var_id] = f"descends({pname}, {t})"
        elif kind == "car":
            _, p, item, t = obj
            pname = person_names[p] if p < len(person_names) else f"person_{p}"
            mapping[var_id] = f"carries({pname}, {item}, {t})"
    return mapping
