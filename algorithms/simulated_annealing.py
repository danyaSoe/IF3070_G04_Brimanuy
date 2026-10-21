import math, time
from core.models import Result
from core.objective import evaluate
from core.neighbors import random_neighbor, all_neighbors


def is_local_optimum(problem, state, value):
    # True jika tidak ada neighbor yang nilainya lebih baik dari state saat ini.
    return not any(evaluate(problem, nb) > value for nb in all_neighbors(problem, state))


def simulated_annealing(problem, init, rng, T0=60.0, alpha=0.999, T_min=0.01,
                        max_iter=100000, check_every=50):
    t0 = time.time()
    cur, cur_v = init[:], evaluate(problem, init)
    best, best_v = cur, cur_v
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
        hist.append(cur_v)

        # cek local optimum sungguhan tiap check_every iterasi
        if check_every and it % check_every == 0:
            s = time.time()
            lo_checks += 1
            if is_local_optimum(problem, cur, cur_v):
                lo_hits += 1
                lo_log.append((it, cur_v, T))   # (iterasi, nilai, suhu)
            t_check += time.time() - s

        T *= alpha
    # durasi tidak menghitung waktu pengecekan local optimum
    duration = time.time() - t0 - t_check
    return Result(
        "sa", init, best, best_v, hist, it, duration,
        {"probs": probs, "rejected_worse": rejected_worse,
         "lo_checks": lo_checks, "lo_hits": lo_hits, "lo_log": lo_log,
         "check_every": check_every, "T0": T0, "alpha": alpha}
    )