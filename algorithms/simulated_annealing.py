import math, time
from core.models import OUT, Result
from core.objective import evaluate, is_feasible
from core.neighbors import random_neighbor, all_neighbors

def is_local_optimum(problem, state, value):
    # True jika tidak ada neighbor yang nilainya lebih baik dari state saat ini.
    return not any(evaluate(problem, nb) > value for nb in all_neighbors(problem, state))

def simulated_annealing(problem, init, rng, T0=60.0, alpha=0.999, T_min=0.01,
                        max_iter=100000, check_every=50):
    t0 = time.time()
    cur, cur_v = init[:], evaluate(problem, init)
    best, best_v = cur, cur_v

    best_feasible = cur[:] if is_feasible(problem, cur) else None
    best_feasible_v = cur_v if best_feasible is not None else -math.inf

    hist, probs, rejected_worse = [cur_v], [], 0
    lo_checks, lo_hits, lo_log, t_check = 0, 0, [], 0.0
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
                rejected_worse += 1
        if accept:
            cur, cur_v = nb, v
            if cur_v > best_v:
                best, best_v = cur, cur_v
            if cur_v > best_feasible_v and is_feasible(problem, cur):
                best_feasible, best_feasible_v = cur[:], cur_v

        hist.append(cur_v)
        # cek local optimum sungguhan tiap check_every iterasi
        if check_every and it % check_every == 0:
            s = time.time()
            lo_checks += 1
            if is_local_optimum(problem, cur, cur_v):
                lo_hits += 1
                lo_log.append((it, cur_v, T)) # (iterasi, nilai, suhu)
            t_check += time.time() - s
        T *= alpha
   
    fallback_used = best_feasible is None
    final = ([(OUT, 0, 0, p[3]) for p in init]
             if fallback_used else best_feasible)
    final_v = evaluate(problem, final)

    duration = time.time() - t0

    return Result(
        "sa", init, final, final_v, hist, it, duration,
        {"probs": probs, "rejected_worse": rejected_worse,
         "lo_checks": lo_checks, "lo_hits": lo_hits, "lo_log": lo_log,
         "check_every": check_every, "T0": T0, "alpha": alpha,
         "best_raw_state": best[:], "best_raw_value": best_v,
         "fallback_used": fallback_used,
         "local_optimum_check_seconds": t_check,
         "search_duration_seconds": max(0.0, duration - t_check)}
    )
