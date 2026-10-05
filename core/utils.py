import random
from .neighbors import random_state
from .objective import is_feasible

def run_n(problem, algo, n=3, **params):
    results = []
    for seed in range(n):
        rng = random.Random(seed)
        results.append(algo(problem, random_state(problem, rng), rng, **params))
    return results

def summarize(name, results, problem):
    print(f"== {name}")
    for k, r in enumerate(results):
        print(f" run{k}: value={r.final_value:.1f} iter={r.iterations} "
              f"t={r.duration:.2f}s valid={is_feasible(problem, r.final_state)}")