from dataclasses import dataclass, field

@dataclass(frozen=True)
class Vehicle:
    id:str
    w:int
    l:int
    shippingFee: int
    weight:int
    eta: int
    orientation: bool

@dataclass(frozen=True)
class Ship:
    w:int
    l:int
    maxCapacity:int

class Problem:
    def __init__(self, vehicles, ships, mode="fee"):
        self.vehicles = vehicles
        self.ships = ships
        self.mode= mode
        self._pen= {}

    def footprint(self, i, o):
        v= self.vehicles[i]
        if o==0:
            return (v.w,v.l)
        else:
            return (v.l,v.w)

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