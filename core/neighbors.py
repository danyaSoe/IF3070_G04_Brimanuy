from .models import OUT

def clamp(problem, i, s, x, y, o):
    if s == OUT:
        return (OUT, 0, 0, o)
    fw, fl = problem.footprint(i, o); ship = problem.ships[s]
    x = min(x, ship.w - fw); y = min(y, ship.l - fl)
    return (s, x, y, o) if (x >= 0 and y >= 0) else (OUT, 0, 0, o)

def random_placement(problem, i, rng, p_out=0.3):
    o = rng.randint(0, 1)
    if rng.random() < p_out:
        return (OUT, 0, 0, o)
    s = rng.randrange(len(problem.ships)); ship = problem.ships[s]
    fw, fl = problem.footprint(i, o)
    if fw > ship.w or fl > ship.l:
        return (OUT, 0, 0, o)
    return (s, rng.randint(0, ship.w - fw), rng.randint(0, ship.l - fl), o)

def random_state(problem, rng):    # initial state random
    return [random_placement(problem, i, rng) for i in range(len(problem.vehicles))]

def random_neighbor(problem, state, rng):   # 1 neighbor acak (SA, stochastic, GA mutasi)
    new = state[:]; n = len(state)
    kind = rng.choice(("move", "swap", "rotate"))
    if kind == "swap" and n >= 2:
        i, j = rng.sample(range(n), 2)
        (si, xi, yi, oi), (sj, xj, yj, oj) = state[i], state[j]
        new[i] = clamp(problem, i, sj, xj, yj, oi)   # tukar posisi, orientasi tetap
        new[j] = clamp(problem, j, si, xi, yi, oj)
    elif kind == "rotate":
        i = rng.randrange(n); s, x, y, o = state[i]
        new[i] = clamp(problem, i, s, x, y, 1 - o)
    else:
        i = rng.randrange(n)
        new[i] = random_placement(problem, i, rng)
    return new

def all_neighbors(problem, state):    # semua neighbor (steepest ascent)
    n = len(state)
    for i in range(n):
        for o in (0, 1):
            fw, fl = problem.footprint(i, o)
            cands = [(OUT, 0, 0, o)]
            for s, ship in enumerate(problem.ships):
                cands += [(s, x, y, o)
                          for x in range(ship.w - fw + 1)
                          for y in range(ship.l - fl + 1)]
            for p in cands:
                if p != state[i]:
                    new = state[:]; new[i] = p
                    yield new
    for i in range(n):
        for j in range(i + 1, n):
            (si, xi, yi, oi), (sj, xj, yj, oj) = state[i], state[j]
            new = state[:]
            new[i] = clamp(problem, i, sj, xj, yj, oi)
            new[j] = clamp(problem, j, si, xi, yi, oj)
            if new != state:
                yield new