"""
CLI for running custom movers problem instances.

Usage examples:

  # 3 floors, 2 people, chair on floor 1, table on floor 2
  python cli.py --floors 3 --persons 2 --items chair:1 table:2

  # 4 floors, 3 people named Joe/Bill/Mia, several items
  python cli.py --floors 4 --persons 3 --names Joe Bill Mia \\
      --items piano:3 sofa:2 lamp:1 box:2

  # Task 1 only (movement, no items): 3 people reach floor 2
  python cli.py --floors 3 --persons 3 --task 1 --goal-floor 2

  # Solve for a specific T instead of finding optimal
  python cli.py --floors 3 --persons 2 --items chair:1 table:2 --fixed-t 5

  # Save DIMACS CNF and the variable mapping (also works for UNSAT results)
  python cli.py --floors 3 --persons 2 --items chair:1 table:2 \\
      --cnf-out problem.cnf --mapping-out problem.json
"""

import argparse
import sys

from pydantic import ValidationError

from app.config import settings
from app.models.problem import ProblemConfig, ItemPlacement
from app.output.mapping import mapping_to_json
from app.solver.runner import solve_optimal, solve_fixed


def parse_item(s: str) -> ItemPlacement:
    """Parse an item specification string in ``name:floor`` format.

    Raises:
        argparse.ArgumentTypeError: If the string is not in ``name:floor``
            format or the floor is not a non-negative integer.
    """
    name, sep, floor_str = s.rpartition(":")
    if not sep or not name:
        raise argparse.ArgumentTypeError(
            f"Item must be name:floor (e.g. chair:1), got '{s}'"
        )
    try:
        floor = int(floor_str)
    except ValueError:
        raise argparse.ArgumentTypeError(f"Floor must be an integer, got '{floor_str}'")
    if floor < 0:
        raise argparse.ArgumentTypeError(f"Floor must be >= 0, got {floor}")
    return ItemPlacement(name=name, initial_floor=floor)


def build_parser() -> argparse.ArgumentParser:
    """Create the argument parser."""
    parser = argparse.ArgumentParser(
        description="Solve a custom movers problem instance using SAT encoding."
    )
    parser.add_argument("--floors", type=int, required=True, help="Number of floors (0 to n-1)")
    parser.add_argument("--persons", type=int, required=True, help="Number of movers")
    parser.add_argument("--names", nargs="*", help="Optional person names (e.g. Joe Bill Mia)")
    parser.add_argument(
        "--items", nargs="*", type=parse_item, default=[],
        help="Items as name:floor pairs (e.g. chair:1 table:2 piano:3)",
    )
    parser.add_argument("--task", type=int, choices=[1, 2], default=None,
                        help="Force task 1 or 2 (auto-detected from items)")
    parser.add_argument("--goal-floor", type=int, default=None,
                        help="Task 1: target floor for all persons (default: 0)")
    parser.add_argument("--fixed-t", type=int, default=None,
                        help="Solve for exactly this T instead of finding optimal")
    parser.add_argument("--max-t", type=int, default=settings.max_time_steps,
                        help=f"Maximum T to try (default: {settings.max_time_steps})")
    parser.add_argument("--cnf-out", type=str, default=None, help="Save DIMACS CNF to this file")
    parser.add_argument("--mapping-out", type=str, default=None,
                        help="Save the variable ID -> name mapping (JSON) to this file")
    return parser


def print_plan(result) -> None:
    """Pretty-print a satisfiable plan."""
    print("=" * 60)
    print("SOLUTION PLAN")
    print("=" * 60)
    for step in result.plan:
        print(f"\n--- t={step.t} ---")
        positions = ", ".join(f"{p}@floor_{f}" for p, f in step.person_positions.items())
        print(f"  Persons: {positions}")
        if step.item_positions:
            items = ", ".join(f"{i}@floor_{f}" for i, f in step.item_positions.items())
            print(f"  Items:   {items}")
        if step.actions:
            print("  Actions:")
            for a in step.actions:
                if a.action == "idle":
                    print(f"    {a.person}: idle at floor {a.from_floor}")
                elif a.action == "carries":
                    print(f"    {a.person}: carries {a.item} from floor {a.from_floor} to floor {a.to_floor}")
                else:
                    print(f"    {a.person}: {a.action} from floor {a.from_floor} to floor {a.to_floor}")
    print()


def main() -> int:
    """Parse CLI arguments, run the SAT solver, and print the solution plan."""
    parser = build_parser()
    args = parser.parse_args()

    task = args.task if args.task is not None else (2 if args.items else 1)

    if args.max_t < 0 or (args.fixed_t is not None and args.fixed_t < 0):
        parser.error("--max-t and --fixed-t must be >= 0")

    try:
        config = ProblemConfig(
            num_floors=args.floors,
            num_persons=args.persons,
            person_names=args.names or None,
            items=args.items if task == 2 else [],
        )
    except ValidationError as exc:
        for err in exc.errors():
            loc = ".".join(str(x) for x in err["loc"]) or "input"
            print(f"Error ({loc}): {err['msg']}", file=sys.stderr)
        return 2

    goal_floors = None
    if task == 1:
        gf = args.goal_floor if args.goal_floor is not None else 0
        if not 0 <= gf < args.floors:
            parser.error(f"--goal-floor must be between 0 and {args.floors - 1}")
        goal_floors = {p: gf for p in range(args.persons)}

    print(f"Floors: {args.floors}  |  Persons: {args.persons}  |  Task: {task}")
    for item in config.items:
        print(f"  {item.name} @ floor {item.initial_floor}")
    if task == 1 and args.goal_floor is not None:
        print(f"  Goal: all persons reach floor {args.goal_floor}")
    print()

    if args.fixed_t is not None:
        print(f"Solving for T={args.fixed_t}...")
        result = solve_fixed(config, task, args.fixed_t, goal_floors)
    else:
        print(f"Finding optimal solution (max T={args.max_t})...")
        result = solve_optimal(config, task, args.max_t, goal_floors)

    s = result.stats
    print()
    if result.satisfiable:
        print(f"SATISFIABLE in {result.num_time_steps} time steps")
    else:
        print(f"UNSATISFIABLE: no plan with T <= {result.num_time_steps}.")
    print(f"  Variables: {s.num_variables}  |  Clauses: {s.num_clauses}  |  "
          f"Time: {s.solve_time_ms}ms  |  Horizons tried: {s.horizons_tried}")
    print()

    if result.satisfiable:
        print_plan(result)

    if args.cnf_out:
        with open(args.cnf_out, "w") as f:
            f.write(result.cnf_dimacs)
        print(f"DIMACS CNF saved to {args.cnf_out}")
    if args.mapping_out:
        with open(args.mapping_out, "w") as f:
            f.write(mapping_to_json(result.variable_mapping))
        print(f"Variable mapping saved to {args.mapping_out}")

    return 0 if result.satisfiable else 1


if __name__ == "__main__":
    sys.exit(main())
