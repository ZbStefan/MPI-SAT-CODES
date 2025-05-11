import sys
import random
import time
import tracemalloc

MAX_FLIPS = 1000
MAX_RESTARTS = 10

def parse_dimacs(file_path):
    clauses = []
    variables = set()
    with open(file_path, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('c') or line.startswith('p'):
                continue
            lits = list(map(int, line.split()))
            if lits[-1] != 0:
                raise ValueError("Each clause line must end with 0")
            lits = lits[:-1]
            clauses.append(lits)
            for lit in lits:
                variables.add(abs(lit))
    return clauses, sorted(variables)

def generate_random_assignment(variables):
    return {v: random.choice([True, False]) for v in variables}

def count_satisfied_clauses(clauses, assignment):
    total = 0
    for clause in clauses:
        if any((lit > 0 and assignment[abs(lit)]) or
               (lit < 0 and not assignment[abs(lit)]) for lit in clause):
            total += 1
    return total

def gsat(clauses, variables):
    steps = 0
    start = time.time()
    tracemalloc.start()

    for restart in range(1, MAX_RESTARTS + 1):
        assignment = generate_random_assignment(variables)
        sat_count = count_satisfied_clauses(clauses, assignment)
        print(f"\n[Restart {restart}] Initial assignment: {assignment}")
        print(f"             Clauses satisfied: {sat_count}/{len(clauses)}")

        for flip in range(1, MAX_FLIPS + 1):
            steps += 1

            if sat_count == len(clauses):
                runtime = time.time() - start
                _, peak = tracemalloc.get_traced_memory()
                tracemalloc.stop()
                print(f"\n✔ Solution found in {steps} total flips.")
                return True, assignment, steps, runtime, peak

            best_var = None
            best_score = sat_count
            for v in variables:
                assignment[v] = not assignment[v]
                score = count_satisfied_clauses(clauses, assignment)
                assignment[v] = not assignment[v]
                if score > best_score:
                    best_score, best_var = score, v

            if best_var is not None:
                assignment[best_var] = not assignment[best_var]
                sat_count = best_score
                print(f"[Step {steps:4d}] flip x{best_var} → {assignment[best_var]:5}  " +
                      f"now {sat_count}/{len(clauses)} clauses satisfied")
            else:
                print(f"[Step {steps:4d}] no improving flip, staying at {sat_count}/{len(clauses)}")

    runtime = time.time() - start
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    print(f"\n✘ No solution found after {steps} flips.")
    return False, None, steps, runtime, peak

def main():
    if len(sys.argv) != 2:
        print(f"Usage: python {sys.argv[0]} input.cnf", file=sys.stderr)
        sys.exit(1)

    cnf_path = sys.argv[1]
    try:
        clauses, variables = parse_dimacs(cnf_path)
    except Exception as e:
        print(f"Error parsing '{cnf_path}': {e}", file=sys.stderr)
        sys.exit(1)

    sat, assignment, steps, runtime, peak = gsat(clauses, variables)

    print("\n=== Final Summary ===")
    print("SATISFIABLE" if sat else "UNSATISFIABLE")
    print(f"Total flips   : {steps}")
    print(f"Runtime       : {runtime:.6f} seconds")
    print(f"Peak memory   : {peak / 1024:.2f} KB")
    if sat:
        print("Assignment:")
        for v in variables:
            print(f"  x{v} = {'True' if assignment[v] else 'False'}")

if __name__ == "__main__":
    main()
