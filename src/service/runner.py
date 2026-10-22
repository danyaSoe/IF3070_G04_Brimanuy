import random
from dataclasses import asdict
from pathlib import Path

from algorithms.genetic_algorithm import genetic_algorithm
from algorithms.hill_climbing import (
    random_restart,
    sideways_move,
    steepest_ascent,
    stochastic_hc,
)
from algorithms.simulated_annealing import simulated_annealing
from core.io import load_problem
from core.neighbors import random_state
from core.objective import evaluate_detail
from core.io import state_to_dict


ALGORITHMS = {
    "steepest": steepest_ascent,
    "sideways": sideways_move,
    "stochastic": stochastic_hc,
    "random_restart": random_restart,
    "sa": simulated_annealing,
    "ga": genetic_algorithm,
}


def _constraint_summary(problem, state):
    score, penalty = evaluate_detail(problem, state)
    loads = [0] * len(problem.ships)
    for index, (ship_index, *_rest) in enumerate(state):
        if ship_index >= 0:
            loads[ship_index] += problem.vehicles[index].weight
    return {
        "feasible": penalty == 0,
        "penalty": penalty,
        "score_before_penalty": score,
        "ship_loads": loads,
        "capacity_ok": all(
            load <= ship.max_capacity
            for load, ship in zip(loads, problem.ships)
        ),
    }


def run_simulation(case_path, algorithm="ga", mode="fee", seed=0, parameters=None):
    if algorithm not in ALGORITHMS:
        raise ValueError(f"Algoritma tidak dikenal: {algorithm}")
    problem = load_problem(Path(case_path), mode)
    rng = random.Random(seed)
    initial = random_state(problem, rng)
    params = dict(parameters or {})
    result = ALGORITHMS[algorithm](problem, initial, rng, **params)
    return {
        "algorithm": algorithm,
        "mode": mode,
        "seed": seed,
        "initial_state": initial,
        "final_state": result.final_state,
        "final_value": result.final_value,
        "history": result.history,
        "iterations": result.iterations,
        "duration": result.duration,
        "extras": result.extras,
        "vehicles": [asdict(vehicle) for vehicle in problem.vehicles],
        "ships": [asdict(ship) for ship in problem.ships],
        "initial_mapping": state_to_dict(problem, result.initial_state),
        "final_mapping": state_to_dict(problem, result.final_state),
        **_constraint_summary(problem, result.final_state),
    }
