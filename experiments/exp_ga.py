import argparse
import random
from pathlib import Path

from algorithms.genetic_algorithm import genetic_algorithm
from core.io import load_problem
from core.neighbors import random_state
from experiments.common import (PROJECT_ROOT, resolve_case, result_row, save_result,
                                summarize_rows, write_csv, write_json)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--case", default="data/case1.json")
    parser.add_argument("--mode", choices=("fee", "urgency", "area"), default="fee")
    parser.add_argument("--output", type=Path, default=PROJECT_ROOT / "output_GA")
    parser.add_argument("--seeds", nargs=3, type=int, default=[0, 1, 2])
    parser.add_argument("--populations", nargs=3, type=int, default=[20, 50, 100])
    parser.add_argument("--generation-counts", nargs=3, type=int, default=[50, 150, 400])
    parser.add_argument("--fixed-generations", type=int, default=200)
    parser.add_argument("--fixed-population", type=int, default=50)
    parser.add_argument("--crossover-rate", type=float, default=0.9)
    parser.add_argument("--mutation-rate", type=float, default=0.2)
    parser.add_argument("--elitism", type=int, default=2)
    parser.add_argument("--no-plots", action="store_true")
    args = parser.parse_args(argv)
    for name, values in (("seeds", args.seeds), ("populations", args.populations),
                         ("generation-counts", args.generation_counts)):
        if len(set(values)) != 3:
            parser.error(f"{name} harus berisi tiga nilai yang berbeda.")
    if min(args.generation_counts + [args.fixed_generations]) <= 0:
        parser.error("Jumlah generasi eksperimen harus positif.")
    if args.elitism < 0 or min(args.populations + [args.fixed_population]) < max(1, args.elitism):
        parser.error("Setiap populasi harus >= 1 dan >= elitism; elitism >= 0.")
    if not 0 <= args.crossover_rate <= 1 or not 0 <= args.mutation_rate <= 1:
        parser.error("Crossover rate dan mutation rate harus berada pada [0, 1].")
    case = resolve_case(args.case)
    try:
        problem = load_problem(case, args.mode)
    except (OSError, ValueError, KeyError, TypeError) as exc:
        parser.error(str(exc))
    args.output.mkdir(parents=True, exist_ok=True)
    # Snapshot input agar hasil eksperimen tetap dapat diaudit ketika case berubah.
    (args.output / "input_case.json").write_bytes(case.read_bytes())
    configs = [("population", f"ga_pop{p}", p, args.fixed_generations) for p in args.populations]
    configs += [("generations", f"ga_gen{g}", args.fixed_population, g) for g in args.generation_counts]
    rows = []
    for group, tag, pop_size, generations in configs:
        params = dict(pop_size=pop_size, generations=generations,
                      crossover_rate=args.crossover_rate, mutation_rate=args.mutation_rate,
                      elitism=args.elitism)
        for seed in args.seeds:
            rng = random.Random(seed)
            initial = random_state(problem, rng)
            result = genetic_algorithm(problem, initial, rng, **params)
            payload = save_result(problem, result, args.output / tag / f"seed_{seed}",
                                  case_path=case, seed=seed, config=tag, params=params,
                                  group=group, plots=not args.no_plots)
            rows.append(result_row(payload))
            # Tulis secara bertahap supaya run yang selesai tidak hilang jika dihentikan.
            write_csv(args.output / "runs.csv", rows)
            print(f"{len(rows):02d}/18 {tag} seed={seed}: value={result.final_value:.2f} "
                  f"valid={payload['feasible']} duration={result.duration:.3f}s", flush=True)
    summary = summarize_rows(rows)
    write_csv(args.output / "summary.csv", summary)
    write_json(args.output / "summary.json", summary)
    print(f"Selesai: {len(rows)} run. Hasil: {args.output.resolve()}")
    return rows


if __name__ == "__main__":
    main()
