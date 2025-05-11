import sys
import time
import tracemalloc


decisions = 0
backtracks = 0
unit_props = 0
pure_assigns = 0
step_counter = 0

def parse_dimacs(filename):
    clauses = []
    with open(filename) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('c'):
                continue
            if line.startswith('p cnf'):
                parts = line.split()
                if len(parts) >= 4:
                    _ = int(parts[2])
                continue
            parts = line.split()
            if parts[-1] == '0':
                lits = [int(x) for x in parts[:-1]]
            else:
                lits = [int(x) for x in parts]
            if lits:
                clauses.append(lits)
    return clauses

def simplify_clauses(clauses, lit):
    new_clauses = []
    for clause in clauses:
        if lit in clause:
            continue
        if -lit in clause:
            reduced = [x for x in clause if x != -lit]
            if not reduced:
                return None
            new_clauses.append(reduced)
        else:
            new_clauses.append(clause.copy())
    return new_clauses

def find_unit_clause(clauses):
    for clause in clauses:
        if len(clause) == 1:
            return clause[0]
    return None

def find_pure_literal(clauses):
    counts = {}
    for clause in clauses:
        for lit in clause:
            counts[lit] = counts.get(lit, 0) + 1
    for lit in counts:
        if -lit not in counts:
            return lit
    return None


def dpll(clauses, assignment):
    global decisions, backtracks, unit_props, pure_assigns, step_counter

    while True:
        unit = find_unit_clause(clauses)
        if unit is None:
            break
        unit_props += 1
        step_counter += 1
        print(f"Step {step_counter}")
        assignment[abs(unit)] = (unit > 0)
        clauses = simplify_clauses(clauses, unit)
        if clauses is None:
            return None

    while True:
        pure = find_pure_literal(clauses)
        if pure is None:
            break
        pure_assigns += 1
        step_counter += 1
        print(f"Step {step_counter}")
        assignment[abs(pure)] = (pure > 0)
        clauses = [cl for cl in clauses if pure not in cl]

    if not clauses:
        return assignment
    for clause in clauses:
        if not clause:
            return None

    lit = clauses[0][0]
    decisions += 1
    step_counter += 1
    print(f"Step {step_counter}")
    var = abs(lit)
    val = (lit > 0)

    new_assign = assignment.copy()
    new_assign[var] = val
    new_clauses = simplify_clauses(clauses, lit)
    if new_clauses is not None:
        result = dpll(new_clauses, new_assign)
        if result is not None:
            return result

    backtracks += 1
    step_counter += 1
    print(f"Step {step_counter}")
    new_assign = assignment.copy()
    new_assign[var] = not val
    new_clauses = simplify_clauses(clauses, -lit)
    if new_clauses is not None:
        return dpll(new_clauses, new_assign)

    return None

def solve_cnf(clauses, verbose=False):
    global decisions, backtracks, unit_props, pure_assigns, step_counter
    decisions = backtracks = unit_props = pure_assigns = 0
    step_counter = 0
    result = dpll(clauses, {})
    total_steps = decisions + backtracks + unit_props + pure_assigns

    if result is not None:
        print("s SATISFIABLE")
        if verbose:
            for var in sorted(result):
                lit = var if result[var] else -var
                print(f"v {lit}")
        else:
            print("Solution found (use -v for assignment).")
    else:
        print("s UNSATISFIABLE")

    print(f"decisions = {decisions}, backtracks = {backtracks}, unit_propagations = {unit_props}, pure_literals = {pure_assigns}")
    print(f"total steps = {total_steps}")

if __name__ == "__main__":
    tracemalloc.start()
    start_time = time.time()

    if len(sys.argv) < 2:
        print("Usage: python solver.py <input.cnf> [-v]")
        sys.exit(1)
    filename = sys.argv[1]
    verbose = ("-v" in sys.argv or "--verbose" in sys.argv)
    clauses = parse_dimacs(filename)
    solve_cnf(clauses, verbose)
    end_time = time.time()
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    print("Runtime: {:.4f} seconds".format(end_time - start_time))
    print(f"Peak memory usage: {peak / 10 ** 6:.3f} MB")