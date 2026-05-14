"""SAT model decoder: converts a satisfying assignment into a structured plan.

Translates the raw list of true/false variable assignments from the SAT
solver into a chronological sequence of :class:`~app.models.problem.TimeStep`
objects with human-readable positions and actions.
"""

from pysat.formula import IDPool

from app.models.problem import ProblemConfig, StepAction, TimeStep
from app.encoding.variables import (
    at_floor_person,
    at_floor_item,
    ascends,
    descends,
    carries,
)


def _person_name(config: ProblemConfig, p: int) -> str:
    """Return the display name for person index ``p``."""
    if config.person_names and p < len(config.person_names):
        return config.person_names[p]
    return f"person_{p}"


def decode(
    model: list[int],
    pool: IDPool,
    config: ProblemConfig,
    T: int,
    task: int,
) -> list[TimeStep]:
    """Decode a SAT model into a list of time steps.

    For each time step t (0 through T), determines person and item
    positions by checking which ``atFloor`` variables are true, then
    determines actions (ascend, descend, carry, idle) by checking
    the corresponding action variables.  Actions are only populated
    for steps 0 through T-1; the final step is a position snapshot.

    Args:
        model: List of signed integers from the SAT solver. Positive
            values indicate true variables.
        pool: Variable pool used during encoding.
        config: Original problem specification.
        T: Time horizon of the solution.
        task: Task variant (1 or 2).

    Returns:
        Chronologically ordered list of TimeStep objects from t=0 to t=T.
    """
    true_vars = set(model)
    n = config.num_floors
    m = config.num_persons
    item_names = [it.name for it in config.items]
    steps = []

    for t in range(T + 1):
        actions = []
        person_positions: dict[str, int] = {}
        item_positions: dict[str, int] = {}

        for p in range(m):
            pname = _person_name(config, p)
            for f in range(n):
                if at_floor_person(pool, p, f, t) in true_vars:
                    person_positions[pname] = f
                    break

        if task == 2:
            for name in item_names:
                for f in range(n):
                    if at_floor_item(pool, name, f, t) in true_vars:
                        item_positions[name] = f
                        break

        if t < T:
            for p in range(m):
                pname = _person_name(config, p)
                from_floor = person_positions.get(pname, 0)

                if ascends(pool, p, t) in true_vars:
                    actions.append(StepAction(
                        person=pname,
                        action="ascends",
                        from_floor=from_floor,
                        to_floor=from_floor + 1,
                    ))
                elif descends(pool, p, t) in true_vars:
                    carried_item = None
                    if task == 2:
                        for name in item_names:
                            if carries(pool, p, name, t) in true_vars:
                                carried_item = name
                                break

                    actions.append(StepAction(
                        person=pname,
                        action="carries" if carried_item else "descends",
                        from_floor=from_floor,
                        to_floor=from_floor - 1,
                        item=carried_item,
                    ))
                else:
                    actions.append(StepAction(
                        person=pname,
                        action="idle",
                        from_floor=from_floor,
                        to_floor=from_floor,
                    ))

        steps.append(TimeStep(
            t=t,
            actions=actions,
            person_positions=person_positions,
            item_positions=item_positions,
        ))

    return steps
