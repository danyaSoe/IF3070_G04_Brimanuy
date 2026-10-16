import math
import time

from core.models import OUT, Result
from core.neighbors import random_neighbor, random_state
from core.objective import evaluate, evaluate_detail


def roulette_select(pop, fits, rng):
    if not pop or len(pop) != len(fits):
        raise ValueError("Populasi tidak boleh kosong dan harus seukuran fitness.")
    if not all(math.isfinite(f) for f in fits):
        raise ValueError("Fitness harus berupa angka finite.")

    minimum = min(fits)
    weights = [f - minimum + 1.0 for f in fits]
    total = math.fsum(weights)

    if not math.isfinite(total):
        raise ValueError("Rentang fitness terlalu besar untuk roulette wheel.")

    point, cumulative = rng.random() * total, 0.0

    for individual, weight in zip(pop, weights):
        cumulative += weight
        if point < cumulative:
            return individual

    return pop[-1]


def crossover(a, b, rng):
    if len(a) != len(b):
        raise ValueError("Panjang kedua kromosom harus sama.")
    if len(a) < 2:
        return a[:], b[:]

    cut = rng.randint(1, len(a) - 1)
    return a[:cut] + b[cut:], b[:cut] + a[cut:]


def _validate(
    problem, init, pop_size, generations, crossover_rate, mutation_rate, elitism
):
    for name, value, minimum in (
        ("pop_size", pop_size, 1),
        ("generations", generations, 0),
        ("elitism", elitism, 0),
    ):
        if isinstance(value, bool) or not isinstance(value, int) or value < minimum:
            raise ValueError(f"{name} harus integer >= {minimum}.")

    if elitism > pop_size:
        raise ValueError("elitism tidak boleh melebihi pop_size.")

    for name, rate in (
        ("crossover_rate", crossover_rate),
        ("mutation_rate", mutation_rate),
    ):
        if (
            not isinstance(rate, (int, float))
            or not math.isfinite(rate)
            or not 0 <= rate <= 1
        ):
            raise ValueError(f"{name} harus berada pada rentang [0, 1].")

    if len(init) != len(problem.vehicles):
        raise ValueError("State harus memuat satu placement untuk setiap kendaraan.")

    for placement in init:
        if len(placement) != 4 or any(type(v) is not int for v in placement):
            raise ValueError("Placement harus (ship, x, y, o) berisi empat integer.")

        s, x, y, o = placement

        if s < OUT or s >= len(problem.ships) or o not in (0, 1):
            raise ValueError("Indeks kapal atau orientasi pada state tidak valid.")


def genetic_algorithm(
    problem,
    init,
    rng,
    pop_size=50,
    generations=200,
    crossover_rate=0.9,
    mutation_rate=0.2,
    elitism=2,
):
    _validate(
        problem, init, pop_size, generations, crossover_rate, mutation_rate, elitism
    )

    started = time.perf_counter()
    initial = [tuple(p) for p in init]
    pop = [initial[:]] + [
        random_state(problem, rng) for _ in range(pop_size - 1)
    ]
    initial_population = [individual[:] for individual in pop]

    max_hist, avg_hist, feasible_hist = [], [], []
    best_feasible, best_feasible_value = None, -math.inf
    best_raw, best_raw_value, best_raw_generation = None, -math.inf, 0
    best_feasible_generation = None

    for generation in range(generations + 1):
        details = [evaluate_detail(problem, individual) for individual in pop]
        fits = [score - penalty for score, penalty in details]

        max_hist.append(max(fits))
        avg_hist.append(math.fsum(fits) / len(fits))
        feasible_hist.append(
            sum(penalty == 0 for _, penalty in details) / len(pop)
        )

        for individual, fitness, (_, penalty) in zip(pop, fits, details):
            if fitness > best_raw_value:
                best_raw, best_raw_value = individual[:], fitness
                best_raw_generation = generation

            if penalty == 0 and fitness > best_feasible_value:
                best_feasible, best_feasible_value = individual[:], fitness
                best_feasible_generation = generation

        if generation == generations:
            break

        ranked = sorted(
            range(pop_size),
            key=lambda index: fits[index],
            reverse=True,
        )
        children = [pop[index][:] for index in ranked[:elitism]]

        while len(children) < pop_size:
            a = roulette_select(pop, fits, rng)
            b = roulette_select(pop, fits, rng)

            pair = (
                crossover(a, b, rng)
                if rng.random() < crossover_rate
                else (a[:], b[:])
            )

            for child in pair:
                if len(children) == pop_size:
                    break

                if child and rng.random() < mutation_rate:
                    child = random_neighbor(problem, child, rng)

                children.append(child)

        pop = children

    fallback_used = best_feasible is None
    final = (
        [(OUT, 0, 0, p[3]) for p in initial]
        if fallback_used
        else best_feasible
    )
    final_value = evaluate(problem, final)

    extras = {
        "avg_hist": avg_hist,
        "feasible_fraction_hist": feasible_hist,
        "pop_size": pop_size,
        "generations": generations,
        "crossover_rate": crossover_rate,
        "mutation_rate": mutation_rate,
        "elitism": elitism,
        "initial_population": initial_population,
        "best_raw_state": best_raw,
        "best_raw_value": best_raw_value,
        "best_raw_generation": best_raw_generation,
        "best_feasible_generation": best_feasible_generation,
        "fallback_used": fallback_used,
        "output_source": (
            "all_out_fallback"
            if fallback_used
            else "best_feasible_archive"
        ),
        "fitness_evaluations": pop_size * (generations + 1),
    }

    return Result(
        "ga",
        initial,
        final[:],
        final_value,
        max_hist,
        generations,
        time.perf_counter() - started,
        extras,
    )