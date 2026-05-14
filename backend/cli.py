"""
CLI for running custom movers problem instances.

Usage examples:

  # 3 floors, 2 people, chair on floor 1, table on floor 2
  python cli.py --floors 3 --persons 2 --items chair:1 table:2

  # 4 floors, 3 people named Joe/Bill/Mia, several items
  python cli.py --floors 4 --persons 3 --names Joe Bill Mia \
      --items piano:3 sofa:2 lamp:1 box:2

  # Task 1 only (movement, no items): 3 people reach floor 2
  python cli.py --floors 3 --persons 3 --task 1 --goal-floor 2

  # Solve for a specific T instead of finding optimal
  python cli.py --floors 3 --persons 2 --items chair:1 table:2 --fixed-t 5

  # Save DIMACS CNF to a file
  python cli.py --floors 3 --persons 2 --items chair:1 table:2 --cnf-out problem.cnf
"""

import argparse
import sys

from app.models.problem import ProblemConfig, ItemPlacement
from app.solver.runner import solve_optimal, solve_fixed


def parse_item(s: str) -> ItemPlacement:
    """Parse an item specification string in ``name:floor`` format.

    Args:
        s: Item string (e.g. ``"chair:1"``).

    Returns:
        An ItemPlacement with the parsed name and floor.

    Raises:
        argparse.ArgumentTypeError: If the string is not in
            ``name:floor`` format or the floor is not an integer.
    """
    parts = s.split(":")
    if len(parts) != 2:
        raise argparse.ArgumentTypeError(
            f"Item must be name:floor (e.g. chair:1), got '{s}'"
        )
    name = parts[0]
    try:
        floor = int(parts[1])
    except ValueError:
        raise argparse.ArgumentTypeError(
            f"Floor must be an integer, got '{parts[1]}'"
        )
    return ItemPlacement(name=name, initial_floor=floor)


def main():
    """Parse CLI arguments, run the SAT solver, and print the solution plan."""
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
    parser.add_argument("--task", type=int, choices=[1, 2], default=None, help="Force task 1 or 2 (auto-detected from items)")
    parser.add_argument("--goal-floor", type=int, default=None, help="Task 1: target floor for all persons (default: 0)")
    parser.add_argument("--fixed-t", type=int, default=None, help="Solve for exactly this T instead of finding optimal")
    parser.add_argument("--max-t", type=int, default=20, help="Maximum T to try (default: 20)")
    parser.add_argument("--cnf-out", type=str, default=None, help="Save DIMACS CNF to this file")

    args = parser.parse_args()

    task = args.task
    if task is None:
        task = 2 if args.items else 1

    for item in args.items:
        if item.initial_floor < 0 or item.initial_floor >= args.floors:
            print(f"Error: item '{item.name}' is on floor {item.initial_floor}, "
                  f"but floors range from 0 to {args.floors - 1}")
            sys.exit(1)

    config = ProblemConfig(
        num_floors=args.floors,
        num_persons=args.persons,
        person_names=args.names,
        items=args.items,
    )

    goal_floors = None
    if task == 1:
        gf = args.goal_floor if args.goal_floor is not None else 0
        goal_floors = {p: gf for p in range(args.persons)}

    print(f"Floors: {args.floors}  |  Persons: {args.persons}  |  Task: {task}")
    if args.items:
        for item in args.items:
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

    print()
    if not result.satisfiable:
        print("UNSATISFIABLE — no solution found.")
        if result.stats:
            print(f"  Variables: {result.stats.num_variables}  |  Clauses: {result.stats.num_clauses}")
        sys.exit(1)

    print(f"SATISFIABLE in {result.num_time_steps} time steps")
    print(f"  Variables: {result.stats.num_variables}  |  Clauses: {result.stats.num_clauses}  |  Time: {result.stats.solve_time_ms}ms")
    print()

    person_names = args.names or [f"person_{i}" for i in range(args.persons)]

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
            print(f"  Actions:")
            for a in step.actions:
                if a.action == "idle":
                    print(f"    {a.person}: idle at floor {a.from_floor}")
                elif a.action == "carries":
                    print(f"    {a.person}: carries {a.item} from floor {a.from_floor} to floor {a.to_floor}")
                else:
                    print(f"    {a.person}: {a.action} from floor {a.from_floor} to floor {a.to_floor}")

    print()

    if args.cnf_out and result.cnf_dimacs:
        with open(args.cnf_out, "w") as f:
            f.write(result.cnf_dimacs)
        print(f"DIMACS CNF saved to {args.cnf_out}")
    elif args.cnf_out:
        print("No CNF to save (UNSAT)")


if __name__ == "__main__":
    main()
