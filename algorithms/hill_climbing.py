import time
from core.models import Result
from core.objective import evaluate
from core.neighbors import all_neighbors, random_neighbor, random_state

def steepest_ascent(problem, init, rng=None):
    t0 = time.time()
    cur, cur_v = init[:], evaluate(problem, init)
    hist, it = [cur_v], 0
    while True:
        best, best_v = None, cur_v
        for nb in all_neighbors(problem, cur):
            v = evaluate(problem, nb)
            if v > best_v:
                best, best_v = nb, v
        if best is None:
            break
        cur, cur_v = best, best_v
        it += 1; hist.append(cur_v)
    return Result("steepest", init, cur, cur_v, hist, it, time.time() - t0)

def sideways_move(problem, init, rng, max_sideways=100):
    t0 = time.time()
    cur, cur_v = init[:], evaluate(problem, init)
    hist, it, side = [cur_v], 0, 0
    while True:
        best, best_v = None, cur_v
        eq, n_eq = None, 0
        for nb in all_neighbors(problem, cur):
            v = evaluate(problem, nb)
            if v > best_v:
                best, best_v = nb, v
            elif v == cur_v:
                n_eq += 1
                if rng.random() < 1 / n_eq:
                    eq = nb
        if best is not None:
            cur, cur_v, side = best, best_v, 0
        elif eq is not None and side < max_sideways:
            cur, side = eq, side + 1
        else:
            break
        it += 1; hist.append(cur_v)
    return Result(
        "sideways", init, cur, cur_v, hist, it, time.time() - t0, 
        {"max_sideways": max_sideways, "sideways_used": side}
    )

def stochastic_hc(problem, init, rng, max_iter=20000, patience=2000):
    t0 = time.time()
    cur, cur_v = init[:], evaluate(problem, init)
    hist, no_imp, it = [cur_v], 0, 0
    for it in range(1, max_iter + 1):
        nb = random_neighbor(problem, cur, rng); v = evaluate(problem, nb)
        if v > cur_v:
            cur, cur_v, no_imp = nb, v, 0
        else:
            no_imp += 1
        hist.append(cur_v)
        if no_imp >= patience:
            break
    return Result("stochastic", init, cur, cur_v, hist, it, time.time() - t0)

def random_restart(problem, init, rng, max_restart=10):
    t0 = time.time()
    best, iters, all_hist, state = None, [], [], init
    for r in range(max_restart + 1):          # run ke-0 = initial state
        res = steepest_ascent(problem, state)
        iters.append(res.iterations); all_hist += res.history
        if best is None or res.final_value > best.final_value:
            best = res
        state = random_state(problem, rng)
    return Result(
        "random_restart", init, best.final_state, best.final_value, all_hist,
        sum(iters), time.time() - t0,
        {"restarts": max_restart, "iters_per_restart": iters}
    )
