import argparse
import random
from inspect import Parameter, signature
from pathlib import Path

from core.io import load_problem
from core.neighbors import random_state
from core.utils import summarize
from algorithms.hill_climbing import (
    random_restart,
    sideways_move,
    steepest_ascent,
    stochastic_hc,
)
from algorithms.simulated_annealing import simulated_annealing
from experiments.common import (
    PROJECT_ROOT,
    resolve_case,
    result_row,
    save_result,
    summarize_rows,
    write_csv,
    write_json,
)

ALGOS = {
    "steepest": (steepest_ascent, {}),
    "sideways": (sideways_move, {"max_sideways": 100}),
    "stochastic": (stochastic_hc, {"max_iter": 20000}),
    "random_restart": (random_restart, {"max_restart": 10}),
    "sa": (simulated_annealing, {}),
}


def run_local_experiments(case, output_dir, mode="fee", runs=3, no_plots=False):
    case = resolve_case(case)
    output_dir = Path(output_dir)
    problem = load_problem(case, mode)
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "input_case.json").write_bytes(case.read_bytes())
    rows = []
    for name, (fn, kw) in ALGOS.items():
        params = {
            key: parameter.default
            for key, parameter in signature(fn).parameters.items()
            if parameter.default is not Parameter.empty and key != "rng"
        }
        params.update(kw)
        for seed in range(runs):
            rng = random.Random(seed)
            result = fn(problem, random_state(problem, rng), rng, **kw)
            results = [result]
            summarize(f"{name} seed={seed}", results, problem)
            payload = save_result(
                problem, result, output_dir / name / f"seed_{seed}",
                case_path=case, seed=seed, config=name, params=params,
                group="local", plots=not no_plots,
            )
            rows.append(result_row(payload))
            write_csv(output_dir / "runs.csv", rows)
            if name == "sa":
                print("  rejected_worse:", result.extras["rejected_worse"])
                print("  stuck di local optimum:",
                      result.extras["lo_hits"], "/", result.extras["lo_checks"])
    summary = summarize_rows(rows)
    write_csv(output_dir / "summary.csv", summary)
    write_json(output_dir / "summary.json", summary)
    print(f"Selesai: {len(rows)} run. Hasil: {output_dir.resolve()}")
    return rows

def main(argv=None):
    parser = argparse.ArgumentParser(description="Run local-search experiments.")
    parser.add_argument("--case", default="data/case1.json")
    parser.add_argument("--mode", choices=("fee", "urgency", "area"), default="fee")
    parser.add_argument("--output", type=Path, default=PROJECT_ROOT / "output_local")
    parser.add_argument("--runs", type=int, default=3)
    parser.add_argument("--no-plots", action="store_true")
    args = parser.parse_args(argv)
    if args.runs < 1:
        parser.error("--runs harus minimal 1.")
    run_local_experiments(
        Path(args.case), args.output, args.mode, args.runs, args.no_plots
    )


if __name__ == "__main__":
    main()
