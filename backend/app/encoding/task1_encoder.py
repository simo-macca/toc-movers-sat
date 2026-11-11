"""SAT encoder for Task 1: person movement without items.

All persons start at floor 0 and must reach specified goal floors
within a time horizon T.  The encoding produces constraint groups:

* **A** -- Initial state (all persons at floor 0)
* **B** -- Goal state (persons at target floors at time T)
* **C** -- Unique floor per person per time step
* **D** -- Action mutex (ascend/descend mutually exclusive)
* **E** -- Preconditions (can't ascend from top / descend from floor 0)
* **F** -- Effects and frame axioms (state transitions)
"""

from pysat.formula import CNF, IDPool

from app.encoding.variables import at_floor_person, ascends, descends
from app.encoding.common_clauses import exactly_one


def encode_task1(
    num_floors: int,
    num_persons: int,
    T: int,
    goal_floors: dict[int, int],
    pool: IDPool | None = None,
) -> tuple[CNF, IDPool]:
    """Encode person movement (no items) into CNF.

    Args:
        num_floors: number of floors (0..num_floors-1)
        num_persons: number of movers
        T: time horizon (0..T)
        goal_floors: {person_index: target_floor_at_time_T}
        pool: existing IDPool to reuse (for Task 2 extension)

    Returns:
        (cnf, pool) where cnf contains all clauses and pool maps vars to ints.
    """
    for p, gf in goal_floors.items():
        if not 0 <= p < num_persons:
            raise ValueError(f"goal_floors refers to unknown person {p}")
        if not 0 <= gf < num_floors:
            raise ValueError(f"goal floor {gf} for person {p} is out of range")

    if pool is None:
        pool = IDPool()
    cnf = CNF()

    P = range(num_persons)
    F = range(num_floors)

    # --- A. Initial state: all persons at floor 0 ---
    for p in P:
        cnf.append([at_floor_person(pool, p, 0, 0)])
        for f in range(1, num_floors):
            cnf.append([-at_floor_person(pool, p, f, 0)])

    # --- B. Goal state ---
    for p, gf in goal_floors.items():
        cnf.append([at_floor_person(pool, p, gf, T)])

    # --- C. Unique floor: each person at exactly one floor per step ---
    for p in P:
        for t in range(T + 1):
            lits = [at_floor_person(pool, p, f, t) for f in F]
            for clause in exactly_one(lits):
                cnf.append(clause)

    # --- D. Action mutex: ascend and descend are mutually exclusive ---
    for p in P:
        for t in range(T):
            cnf.append([-ascends(pool, p, t), -descends(pool, p, t)])

    # --- E. Preconditions ---
    for p in P:
        for t in range(T):
            # E1: cannot ascend from top floor
            cnf.append([-ascends(pool, p, t), -at_floor_person(pool, p, num_floors - 1, t)])
            # E2: cannot descend from floor 0
            cnf.append([-descends(pool, p, t), -at_floor_person(pool, p, 0, t)])

    # --- F. Effects and frame axioms ---
    for p in P:
        for t in range(T):
            for f in F:
                # F1: ascend effect — at(p, f-1, t) & ascends(p,t) => at(p, f, t+1)
                if f >= 1:
                    cnf.append([
                        -at_floor_person(pool, p, f - 1, t),
                        -ascends(pool, p, t),
                        at_floor_person(pool, p, f, t + 1),
                    ])

                # F2: descend effect — at(p, f+1, t) & descends(p,t) => at(p, f, t+1)
                if f <= num_floors - 2:
                    cnf.append([
                        -at_floor_person(pool, p, f + 1, t),
                        -descends(pool, p, t),
                        at_floor_person(pool, p, f, t + 1),
                    ])

                # F3: frame axiom — at(p, f, t) & ~ascends & ~descends => at(p, f, t+1)
                cnf.append([
                    -at_floor_person(pool, p, f, t),
                    ascends(pool, p, t),
                    descends(pool, p, t),
                    at_floor_person(pool, p, f, t + 1),
                ])

    return cnf, pool
