import sys
import time
import tracemalloc
from collections import defaultdict


resolution_steps = 0
eliminated_vars = 0
step_counter = 0

def read_dimacs(path):
    clauses = set()
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('c') or line.startswith('%') or line.startswith('0'):
                continue
            if line.startswith('p'):

                parts = line.split()
                print(f"Header: variables={parts[2]}, clauses={parts[3]}")
                continue
            parts = [int(x) for x in line.split() if x != '0']
            if parts:
                clauses.add(frozenset(parts))
    print(f"Parsed {len(clauses)} clauses.")
    return clauses

def is_tautology(clause):
    return any(-lit in clause for lit in clause)

def choose_variable(clauses):
    var_count = defaultdict(int)
    for clause in clauses:
        for lit in clause:
            var_count[abs(lit)] += 1
    return max(var_count, key=var_count.get, default=None)

def resolve(c1, c2, var):
    resolvent = (c1 - {var}) | (c2 - {-var})
    if is_tautology(resolvent):
        return None
    return frozenset(resolvent)

def dp_solve(clauses):
    global resolution_steps, eliminated_vars, step_counter

    while True:
        if not clauses:
            return True
        if frozenset() in clauses:
            return False

        var = choose_variable(clauses)
        if var is None:
            return True

        pos_clauses = [c for c in clauses if var in c]
        neg_clauses = [c for c in clauses if -var in c]
        other_clauses = [c for c in clauses if var not in c and -var not in c]

        new_clauses = set()
        if not pos_clauses or not neg_clauses:

            eliminated_vars += 1
            clauses = set(other_clauses)
            continue

        for c1 in pos_clauses:
            for c2 in neg_clauses:
                resolvent = resolve(c1, c2, var)
                if resolvent is not None:
                    new_clauses.add(resolvent)
                    resolution_steps += 1
                step_counter += 1
                if step_counter % 100 == 0:
                    print(f"\rSteps: {step_counter}", end='', flush=True)

        clauses = set(other_clauses) | new_clauses
        eliminated_vars += 1

def main():
    global resolution_steps, eliminated_vars, step_counter

    if len(sys.argv) < 2:
        print("Usage: python dp_solver.py <input.cnf>")
        sys.exit(1)

    filename = sys.argv[1]
    clauses = read_dimacs(filename)

    tracemalloc.start()
    start_time = time.time()

    result = dp_solve(clauses)

    end_time = time.time()
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    print()
    print("s SATISFIABLE" if result else "s UNSATISFIABLE")
    print(f"variables eliminated = {eliminated_vars}")
    print(f"resolution steps = {resolution_steps}")
    print(f"total steps = {step_counter}")
    print(f"runtime (seconds) = {end_time - start_time:.4f}")
    print(f"peak memory usage = {peak / (1024 * 1024):.3f} MB")

if __name__ == "__main__":
    main()
