import csv
import hashlib
import json
import platform
import statistics
from collections import defaultdict
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path

from core.io import state_to_dict
from core.models import OUT
from core.objective import evaluate, evaluate_detail, vehicle_score

CODE_ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = CODE_ROOT.parent if CODE_ROOT.name == "src" else CODE_ROOT


def resolve_case(path):
    candidate = Path(path)
    return candidate.resolve() if candidate.exists() else (PROJECT_ROOT / candidate).resolve()


def _fractional_bound(items, capacity):
    result = 0.0
    for score, size in sorted(items, key=lambda item: item[0] / item[1], reverse=True):
        used = min(size, max(0, capacity))
        result += score * used / size
        capacity -= used
        if capacity <= 0:
            break
    return result


def objective_upper_bound(problem):
    scores = [vehicle_score(v, problem.mode) for v in problem.vehicles]
    sum_scores = sum(scores)
    weight_bound = _fractional_bound(
        [(score, v.weight) for score, v in zip(scores, problem.vehicles)],
        sum(ship.max_capacity for ship in problem.ships),
    )
    area_bound = _fractional_bound(
        [(score, v.w * v.l) for score, v in zip(scores, problem.vehicles)],
        sum(ship.w * ship.l for ship in problem.ships),
    )
    return min(sum_scores, weight_bound, area_bound)


def write_json(path, payload):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False, allow_nan=False) + "\n",
                    encoding="utf-8")


def write_csv(path, rows):
    if not rows:
        return
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def save_result(problem, result, directory, *, case_path, seed, config, params,
                group="demo", plots=True):
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    score, penalty = evaluate_detail(problem, result.final_state)
    if abs(result.final_value - (score - penalty)) > 1e-7:
        raise ValueError("Result.final_value tidak cocok dengan final_state.")
    case_path = Path(case_path)
    upper_bound = objective_upper_bound(problem)
    loaded = [i for i, p in enumerate(result.final_state) if p[0] != OUT]
    metadata = {
        "case": case_path.name,
        "case_sha256": hashlib.sha256(case_path.read_bytes()).hexdigest(),
        "mode": problem.mode, "seed": seed, "config": config, "group": group,
        "parameters": params, "python": platform.python_version(),
        "platform": platform.platform(), "created_utc": datetime.now(timezone.utc).isoformat(),
        "duration_scope": "algorithm_only_excludes_plotting_and_file_io",
    }
    payload = {
        "schema_version": 1, **asdict(result), "metadata": metadata,
        "initial_mapping": state_to_dict(problem, result.initial_state),
        "final_mapping": state_to_dict(problem, result.final_state),
        "initial_value": evaluate(problem, result.initial_state),
        "final_score_before_penalty": score, "final_penalty": penalty,
        "feasible": penalty == 0,
        "shipping_fee": sum(problem.vehicles[i].fee for i in loaded),
        "loaded_vehicles": len(loaded), "upper_bound": upper_bound,
        "gap_to_bound_pct": (100 * (upper_bound - result.final_value) / upper_bound
                             if upper_bound > 0 and penalty == 0 else None),
    }
    write_json(directory / "result.json", payload)
    avg = result.extras.get("avg_hist")
    write_csv(directory / "history.csv", [
        {"iteration": index, "population_max" if result.name == "ga" else "objective": value,
         **({"population_mean": avg[index]} if avg is not None else {})}
        for index, value in enumerate(result.history)
    ])
    if plots:
        from core.viz import draw_state, plot_curves
        draw_state(problem, result.initial_state, f"{config} | seed={seed} | INITIAL",
                   save=directory / "initial.png")
        draw_state(problem, result.final_state, f"{config} | seed={seed} | FINAL",
                   save=directory / "final.png")
        curves = {"Maksimum populasi" if avg is not None else "Objective": result.history}
        if avg is not None:
            curves["Rata-rata populasi"] = avg
        plot_curves(curves, f"{config} | seed={seed}",
                    "Generasi (0 = populasi awal)" if avg is not None else "Iterasi",
                    "Objective (skor - penalti)", save=directory / "curve.png")
        if result.name == "sa" and result.extras.get("probs"):
            import matplotlib.pyplot as plt
            iterations, probabilities = zip(*result.extras["probs"])
            fig, ax = plt.subplots(figsize=(8, 4))
            ax.plot(iterations, probabilities)
            ax.set(xlabel="Iterasi asli", ylabel="exp(delta / T)", title=f"SA | seed={seed}")
            ax.grid(True)
            fig.savefig(directory / "acceptance.png", dpi=120, bbox_inches="tight")
            plt.close(fig)
    return payload


def result_row(payload):
    metadata = payload["metadata"]
    params = metadata["parameters"]
    return {
        "algorithm": payload["name"], "config": metadata["config"],
        "group": metadata["group"], "case": metadata["case"],
        "case_sha256": metadata["case_sha256"], "mode": metadata["mode"],
        "seed": metadata["seed"], "pop_size": params.get("pop_size", ""),
        "generations": params.get("generations", ""), "initial_value": payload["initial_value"],
        "final_value": payload["final_value"], "shipping_fee": payload["shipping_fee"],
        "feasible": payload["feasible"], "iterations": payload["iterations"],
        "duration_seconds": payload["duration"], "upper_bound": payload["upper_bound"],
        "gap_to_bound_pct": payload["gap_to_bound_pct"],
        "fallback_used": payload["extras"].get("fallback_used", False),
        "parameters": json.dumps(params, sort_keys=True),
    }


def summarize_rows(rows):
    groups = defaultdict(list)
    for row in rows:
        key = (row["algorithm"], row["config"], row["case_sha256"], row["mode"], row["parameters"])
        groups[key].append(row)
    summaries = []
    for key, group in sorted(groups.items()):
        values = [row["final_value"] for row in group]
        feasible_values = [row["final_value"] for row in group if row["feasible"]]
        summaries.append({
            "algorithm": key[0], "config": key[1], "case_sha256": key[2], "mode": key[3],
            "parameters": key[4], "runs": len(group), "feasible_runs": len(feasible_values),
            "mean_value": statistics.mean(values),
            "std_value_sample": statistics.stdev(values) if len(values) > 1 else 0.0,
            "min_value": min(values), "max_value": max(values),
            "mean_feasible_value": statistics.mean(feasible_values) if feasible_values else None,
            "mean_duration_seconds": statistics.mean(row["duration_seconds"] for row in group),
            "fallback_runs": sum(row["fallback_used"] for row in group),
        })
    return summaries