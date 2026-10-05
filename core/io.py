import json, random
from .models import Vehicle, Ship, Problem, OUT

def load_problem(path, mode="fee"):
    d = json.load(open(path))
    return Problem([Vehicle(**v) for v in d["vehicles"]],
                   [Ship(**s) for s in d["ships"]], mode)

def generate_case(path, n_vehicles=15, n_ships=1, seed=0):
    rng = random.Random(seed)
    vehicles = [dict(id=f"V{i}", w=rng.randint(1, 4), l=rng.randint(1, 5),
                     fee=rng.randint(10, 100), weight=rng.randint(3, 15),
                     eta=rng.randint(0, 7)) for i in range(n_vehicles)]
    ships = [dict(id=f"Ship{k}", w=10, l=20, max_capacity=60 * n_vehicles // 10)
             for k in range(n_ships)]     # kapasitas dibuat ketat supaya jadi constraint aktif
    json.dump({"vehicles": vehicles, "ships": ships}, open(path, "w"), indent=2)

def state_to_dict(problem, state):   # key-value seperti JSON
    return {problem.vehicles[i].id:
            ({"status": "outside", "orientation": "H" if o == 0 else "V"} if s == OUT else
             {"ship": problem.ships[s].id, "x": x, "y": y,
              "orientation": "Horizontal" if o == 0 else "Vertical"})
            for i, (s, x, y, o) in enumerate(state)}