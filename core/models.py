from dataclasses import dataclass, field

OUT = -1

@dataclass(frozen=True)
class Vehicle:
    id: str
    w: int
    l: int
    fee: int
    weight: int
    eta: int

@dataclass(frozen=True)
class Ship:
    id: str
    w: int
    l: int
    max_capacity: int

class Problem:
    def __init__(self, vehicles, ships, mode="fee"):
        self.vehicles = vehicles
        self.ships = ships
        self.mode = mode
        self._pen = {}

    def footprint(self, i, o):
        v = self.vehicles[i]
        return (v.w, v.l) if o == 0 else (v.l, v.w)

@dataclass
class Result:
    name: str
    initial_state: list
    final_state: list
    final_value: float
    history: list # nilai objective per iterasi (untuk plot)
    iterations: int
    duration: float
    extras: dict = field(default_factory=dict) # restart, sideways, avg GA, dll