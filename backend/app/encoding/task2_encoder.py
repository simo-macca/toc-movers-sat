"""SAT encoder for Task 2: person movement with item carrying.

Extends Task 1 by adding item tracking and carrying constraints.
All persons and items must end at floor 0 within time horizon T.
Items can only be moved downward, one at a time, by a descending
person.  The encoding adds constraint groups G--M on top of A--F:

* **G** -- Item initial state
* **H** -- Item goal state (all items at floor 0)
* **I** -- Item location uniqueness (one floor per item per step)
* **J** -- Carrying preconditions (co-location + must descend)
* **K** -- Carrying mutual exclusion (one item/person, one person/item)
* **L** -- Ascending precludes carrying
* **M** -- Item successor-state axioms (carry effects + frame)
"""

from pysat.formula import CNF, IDPool

from app.encoding.variables import (
    at_floor_person,
    at_floor_item,
    ascends,
    descends,
    carries,
)
from app.encoding.common_clauses import exactly_one, at_most_one
from app.encoding.task1_encoder import encode_task1
from app.models.problem import ProblemConfig


def encode_task2(config: ProblemConfig, T: int) -> tuple[CNF, IDPool]:
    """Encode the full movers problem (movement + carrying) into CNF.

    Builds on Task 1 by reusing its movement clauses (groups A--F),
    then adds item tracking and carrying constraints (groups G--M).

    Args:
        config: Problem specification including floors, persons, and items.
        T: Time horizon (the plan spans time steps 0 through T).

    Returns:
        Tuple of (cnf, pool) where ``cnf`` is the complete CNF formula
        and ``pool`` maps symbolic variable tuples to integer IDs.
    """
    n = config.num_floors
    m = config.num_persons
    item_names = [it.name for it in config.items]

    # Start with Task 1 clauses: persons must all end at floor 0
    person_goals = {p: 0 for p in range(m)}
    cnf, pool = encode_task1(n, m, T, person_goals)

    P = range(m)
    F = range(n)

    # --- G. Item initial state ---
    for it in config.items:
        cnf.append([at_floor_item(pool, it.name, it.initial_floor, 0)])
        for f in F:
            if f != it.initial_floor:
                cnf.append([-at_floor_item(pool, it.name, f, 0)])

    # --- H. Item goal state: all items at floor 0 ---
    for name in item_names:
        cnf.append([at_floor_item(pool, name, 0, T)])

    # --- I. Each item at exactly one floor per time step ---
    for name in item_names:
        for t in range(T + 1):
            lits = [at_floor_item(pool, name, f, t) for f in F]
            for clause in exactly_one(lits):
                cnf.append(clause)

    # --- J. Carrying preconditions ---
    for p in P:
        for name in item_names:
            for t in range(T):
                # J1: co-location — carries(p,i,t) & atFloor_person(p,f,t) => atFloor_item(i,f,t)
                for f in F:
                    cnf.append([
                        -carries(pool, p, name, t),
                        -at_floor_person(pool, p, f, t),
                        at_floor_item(pool, name, f, t),
                    ])

                # J2: carrying implies descending
                cnf.append([
                    -carries(pool, p, name, t),
                    descends(pool, p, t),
                ])

    # --- K. Carrying mutual exclusion ---
    for t in range(T):
        # K1: each person carries at most one item
        for p in P:
            carry_lits = [carries(pool, p, name, t) for name in item_names]
            for clause in at_most_one(carry_lits):
                cnf.append(clause)

        # K2: each item carried by at most one person
        for name in item_names:
            carry_lits = [carries(pool, p, name, t) for p in P]
            for clause in at_most_one(carry_lits):
                cnf.append(clause)

    # --- L. Ascending precludes carrying ---
    for p in P:
        for name in item_names:
            for t in range(T):
                cnf.append([-ascends(pool, p, t), -carries(pool, p, name, t)])

    # --- M. Item successor-state axioms ---
    for name in item_names:
        for t in range(T):
            for f in F:
                # M1: carry effect — atFloor_item(i, f+1, t) & carries(p,i,t) => atFloor_item(i, f, t+1)
                if f <= n - 2:
                    for p in P:
                        cnf.append([
                            -at_floor_item(pool, name, f + 1, t),
                            -carries(pool, p, name, t),
                            at_floor_item(pool, name, f, t + 1),
                        ])

                # M2: item frame — stays at f unless some person carries it
                clause = [-at_floor_item(pool, name, f, t)]
                for p in P:
                    clause.append(carries(pool, p, name, t))
                clause.append(at_floor_item(pool, name, f, t + 1))
                cnf.append(clause)

    return cnf, pool
