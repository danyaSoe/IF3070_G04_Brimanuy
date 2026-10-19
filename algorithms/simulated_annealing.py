import math, time
from core.models import Result
from core.objective import evaluate
from core.neighbors import random_neighbor

def simulated_annealing(problem, init, rng, T0=60.0, alpha=0.999, T_min=0.01, max_iter=100000):
    t0 = time.time()
    cur, cur_v = init[:], evaluate(problem, init)
    best, best_v = cur, cur_v
    hist, probs, stuck = [cur_v], [], 0
    T, it = T0, 0
    while T > T_min and it < max_iter:
        it += 1
        nb = random_neighbor(problem, cur, rng); v = evaluate(problem, nb)
        d = v - cur_v
        if d > 0:
            accept = True
        else:
            p = math.exp(d / T)
            probs.append((it, p))
            accept = rng.random() < p
            if not accept:
                stuck += 1
        if accept:
            cur, cur_v = nb, v
        if cur_v > best_v:
            best, best_v = cur, cur_v
        hist.append(cur_v); T *= alpha
    return Result(
        "sa", init, best, best_v, hist, it, time.time() - t0,
        {"probs": probs, "stuck": stuck, "T0": T0, "alpha": alpha}
    )