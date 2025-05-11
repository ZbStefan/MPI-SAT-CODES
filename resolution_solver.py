import argparse
import time
import tracemalloc
import psutil

def parse_dimacs(path):
    clauses = []
    with open(path, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('c') or line.startswith('p'):
                continue
            lits = list(map(int, line.split()))
            clauses.append(frozenset(lits[:-1]))
    return clauses

class ResolutionSolver:
    def __init__(self, clauses):
        self.clauses_list = list(clauses)
        self.clauses_set = set(clauses)
        self.added_ids = []
        self.stats = {"resolutions": 0}

    def resolve(self, ci, cj):
        resolvents = []
        for lit in ci:
            if -lit in cj:
                new_clause = (ci - {lit}) | (cj - {-lit})
                resolvents.append(frozenset(new_clause))
        return resolvents

    def solve(self):
        all_clauses = self.clauses_list.copy()
        idx = len(all_clauses)

        while True:
            new_res = []
            n = len(all_clauses)
            for i in range(n):
                for j in range(i+1, n):
                    ci, cj = all_clauses[i], all_clauses[j]
                    resolvents = self.resolve(ci, cj)
                    self.stats["resolutions"] += len(resolvents)
                    for res in resolvents:
                        if res not in self.clauses_set:
                            idx += 1
                            all_clauses.append(res)
                            self.clauses_set.add(res)
                            self.added_ids.append(idx)
                            if not res:
                                return True
            if len(all_clauses) == self.clauses_list.__len__() + len(self.added_ids) == idx:
                return False

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Resolution-based SAT Solver')
    parser.add_argument('input', help='DIMACS CNF input file')
    parser.add_argument('-v', '--verbose', action='store_true', help='Show added clause IDs')
    args = parser.parse_args()

    clauses = parse_dimacs(args.input)

    tracemalloc.start()
    proc = psutil.Process()
    start_mem = proc.memory_info().rss
    start_time = time.perf_counter()

    solver = ResolutionSolver(clauses)
    unsat = solver.solve()

    end_time = time.perf_counter()
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    print("===== Solver Statistics =====")
    print(f"Result: {'UNSATISFIABLE' if unsat else 'SATISFIABLE'}\n")
    print(f"Total initial clauses: {len(clauses)}")
    print(f"Total clauses after resolution: {len(solver.clauses_set)}")
    if args.verbose:
        print("Added clause IDs:", ', '.join(map(str, solver.added_ids)))
    print(f"Resolution steps (pairs tried): {solver.stats['resolutions']}")
    print(f"Time: {end_time - start_time:.4f} seconds")
    print(f"Memory used: {(proc.memory_info().rss - start_mem)/(1024**2):.2f} MB")
    print(f"Peak memory: {peak/(1024**2):.2f} MB")

