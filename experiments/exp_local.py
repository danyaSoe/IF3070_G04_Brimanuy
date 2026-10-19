from pathlib import Path

from core.io import load_problem
from core.utils import run_n, summarize
from core.viz import draw_state, plot_curves
from algorithms.hill_climbing import *
from algorithms.simulated_annealing import simulated_annealing

PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = PROJECT_ROOT / "out"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
problem = load_problem(PROJECT_ROOT / "data" / "case1.json")
ALGOS = {
    "steepest": (steepest_ascent, {}),
    "sideways": (sideways_move, {"max_sideways": 100}),
    "stochastic": (stochastic_hc, {"max_iter": 20000}),
    "random_restart": (random_restart, {"max_restart": 10}),
    "sa": (simulated_annealing, {}),
}
for name, (fn, kw) in ALGOS.items():
    results = run_n(problem, fn, n=3, **kw)
    summarize(name, results, problem)
    for k, r in enumerate(results):
        draw_state(problem, r.initial_state, f"{name} run{k} INITIAL",
                   save=OUTPUT_DIR / f"{name}_{k}_init.png")
        draw_state(problem, r.final_state, f"{name} run{k} FINAL",
                   save=OUTPUT_DIR / f"{name}_{k}_final.png")
        plot_curves({"objective": r.history}, f"{name} run{k}", "iterasi", "objective",
                    OUTPUT_DIR / f"{name}_{k}_curve.png")
        if name == "sa":
            plot_curves({"e^(ΔE/T)": [p for _, p in r.extras["probs"]]},
                        f"SA run{k}", "iterasi (langkah memburuk)", "e^(ΔE/T)",
                        OUTPUT_DIR / f"sa_{k}_prob.png")
            print("  stuck:", r.extras["stuck"])
