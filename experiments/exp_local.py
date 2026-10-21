import argparse
import random
from pathlib import Path

from core.io import load_problem
from core.neighbors import random_state
from core.utils import run_n, summarize
from core.viz import draw_state, plot_curves
from algorithms.hill_climbing import (
    random_restart,
    sideways_move,
    steepest_ascent,
    stochastic_hc,
)
from algorithms.simulated_annealing import simulated_annealing

PROJECT_ROOT = Path(__file__).resolve().parents[1]
ALGOS = {
    "steepest": (steepest_ascent, {}),
    "sideways": (sideways_move, {"max_sideways": 100}),
    "stochastic": (stochastic_hc, {"max_iter": 20000}),
    "random_restart": (random_restart, {"max_restart": 10}),
    "sa": (simulated_annealing, {}),
}


def run_local_experiments(case, output_dir, mode="fee", runs=3, no_plots=False):
    output_dir.mkdir(parents=True, exist_ok=True)
    problem = load_problem(case, mode)
    for name, (fn, kw) in ALGOS.items():
        for seed in range(runs):
            rng = random.Random(seed)
            result = fn(problem, random_state(problem, rng), rng, **kw)
            results = [result]
            summarize(name, results, problem)
            if no_plots:
                continue
            draw_state(problem, result.initial_state, f"{name} run{seed} INITIAL",
                       save=output_dir / f"{name}_{seed}_init.png")
            draw_state(problem, result.final_state, f"{name} run{seed} FINAL",
                       save=output_dir / f"{name}_{seed}_final.png")
            plot_curves({"objective": result.history}, f"{name} run{seed}",
                        "iterasi", "objective",
                        output_dir / f"{name}_{seed}_curve.png")
            if name == "sa" and result.extras["probs"]:
                plot_curves(
                    {"e^(ΔE/T)": [p for _, p in result.extras["probs"]]},
                    f"SA run{seed}", "iterasi (langkah memburuk)",
                    "e^(ΔE/T)", output_dir / f"sa_{seed}_prob.png",
                )
                print("  rejected_worse:", result.extras["rejected_worse"])
                print("  stuck di local optimum:", result.extras["lo_hits"], "/", result.extras["lo_checks"])


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
