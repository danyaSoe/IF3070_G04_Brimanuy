from .models import OUT

MODES = ("fee", "urgency", "area")

def vehicle_score(v, mode):
    if mode == "fee":     return v.fee
    if mode == "urgency": return v.fee * (1 + 1/(1 + v.eta)) # makin kecil ETA, pengali tarif makin besar
    if mode == "area":    return v.fee + 0.5 * v.w * v.l # tarif tambah luas kendaraan
    raise ValueError(mode)

def _pen(problem, mode):
    if mode not in problem._pen:
        problem._pen[mode] = 1 +max(vehicle_score(v,mode) for v in problem.vehicles)
    return problem._pen[mode] # satu satuan pelanggaran lebih mahal daripada nilai kendaraan tertinggi

def evaluate_detail(problem, state):
    P= _pen(problem, problem.mode)
    score, penalty= 0.0, 0.0
    occ = {}
    load = [0]* len(problem.ships)
    for i, (s, x, y, o) in enumerate(state):
        if s == OUT:
            continue
        v = problem.vehicles[i]
        ship = problem.ships[s]

        fw, fl = problem.footprint(i, o)
        if x < 0 or y < 0 or x + fw > ship.w or y + fl > ship.l:
            penalty += P * fw * fl  # keluar batas geladak
        score += vehicle_score(v, problem.mode)

        load[s] += v.weight
        for dx in range(fw):
            for dy in range(fl):
                c = (s, x+dx, y+dy)
                occ[c] = occ.get(c, 0) + 1
                
    penalty += P * sum(n-1 for n in occ.values() if n > 1) # overlap

    for s, ship in enumerate(problem.ships):
        penalty += P * max(0, load[s] - ship.max_capacity) # overweight
    return score, penalty

def evaluate(problem, state):
    s, p = evaluate_detail(problem, state)
    return s-p

def is_feasible(problem, state):
    return evaluate_detail(problem, state)[1] == 0