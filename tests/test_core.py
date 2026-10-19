import json
import random

from algorithms.genetic_algorithm import genetic_algorithm
from core.io import load_problem
from core.models import Problem, Ship, Vehicle
from core.neighbors import random_state
from core.objective import evaluate_detail, is_feasible
from service.runner import run_simulation


def two_ship_problem():
    vehicles = [
        Vehicle("V0", 2, 2, 10, 3, 1),
        Vehicle("V1", 2, 2, 20, 4, 1),
    ]
    ships = [Ship("S0", 2, 2, 3), Ship("S1", 2, 2, 10)]
    return Problem(vehicles, ships)


def test_multi_ship_capacity_is_checked_per_ship():
    problem = two_ship_problem()
    valid = [(0, 0, 0, 0), (1, 0, 0, 0)]
    invalid = [(0, 0, 0, 0), (0, 0, 0, 0)]
    assert is_feasible(problem, valid)
    assert not is_feasible(problem, invalid)
    assert evaluate_detail(problem, valid)[0] == 30


def test_multi_ship_ga_returns_feasible_solution():
    problem = two_ship_problem()
    rng = random.Random(2)
    result = genetic_algorithm(
        problem, random_state(problem, rng), rng,
        pop_size=6, generations=4, elitism=1,
    )
    assert is_feasible(problem, result.final_state)
    assert any(placement[0] == 1 for placement in result.final_state)


def test_state_serialization_supports_multiple_ships(tmp_path):
    case = tmp_path / "case.json"
    case.write_text(json.dumps({
        "vehicles": [{"id": "V0", "w": 1, "l": 1, "fee": 5, "weight": 1, "eta": 1}],
        "ships": [
            {"id": "S0", "w": 1, "l": 1, "max_capacity": 2},
            {"id": "S1", "w": 1, "l": 1, "max_capacity": 2},
        ],
    }), encoding="utf-8")
    assert len(load_problem(case).ships) == 2


def test_service_returns_multi_ship_summary():
    result = run_simulation("data/case1.json", "ga", seed=0, parameters={
        "pop_size": 4, "generations": 1, "elitism": 1,
    })
    assert result["feasible"]
    assert len(result["ship_loads"]) == 1
