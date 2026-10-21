import argparse
import json
import math
import re
import statistics
from collections import defaultdict
from pathlib import Path

from experiments.common import (
    PROJECT_ROOT,
    result_row,
    summarize_rows,
    write_csv,
    write_json,
)


def configuration_key(row):
    return tuple(row[key] for key in (
        "algorithm", "config", "case_sha256", "mode", "parameters"
    ))


def load_rows(inputs):
    files = set()
    for value in inputs:
        path = Path(value)
        if not path.exists():
            raise ValueError(f"Input tidak ditemukan: {path}. Jalankan eksperimen dahulu.")
        found = sorted(path.rglob("result.json")) if path.is_dir() else [path]
        if not found:
            raise ValueError(f"Tidak ada result.json di {path}. Gunakan hasil ekspor common.py.")
        files.update(item.resolve() for item in found)
    rows, seen = [], {}
    for path in sorted(files):
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
            if payload.get("schema_version") != 1:
                raise ValueError("schema_version harus 1")
            if not isinstance(payload.get("feasible"), bool):
                raise ValueError("feasible harus boolean")
            row = result_row(payload)
            for key in ("initial_value", "final_value", "shipping_fee",
                        "duration_seconds", "upper_bound"):
                if not math.isfinite(row[key]):
                    raise ValueError(f"{key} harus berupa angka finite")
            if row["duration_seconds"] < 0:
                raise ValueError("duration_seconds tidak boleh negatif")
            gap = row["gap_to_bound_pct"]
            if gap is not None and not math.isfinite(gap):
                raise ValueError("gap_to_bound_pct harus berupa angka finite atau null")
            identity = configuration_key(row) + (row["seed"],)
            if identity in seen:
                raise ValueError(f"Run dengan konfigurasi dan seed sama sudah ada di {seen[identity]}")
            seen[identity] = path
            row["source_file"] = str(path)
            rows.append(row)
        except (OSError, ValueError, KeyError, TypeError, AttributeError) as exc:
            raise ValueError(f"Hasil tidak valid di {path}: {exc}") from exc
    if not rows:
        raise ValueError("Tidak ada hasil eksperimen untuk dibandingkan.")
    return rows


def summarize_comparison(rows):
    groups = defaultdict(list)
    for row in rows:
        groups[configuration_key(row)].append(row)
    summaries = summarize_rows(rows)
    for summary in summaries:
        group = groups[configuration_key(summary)]
        gaps = [row["gap_to_bound_pct"] for row in group
                if row["feasible"] and row["gap_to_bound_pct"] is not None]
        summary.update({
            "case": group[0]["case"],
            "group": ",".join(sorted({row["group"] for row in group})),
            "seeds": ",".join(str(seed) for seed in sorted(row["seed"] for row in group)),
            "upper_bound": group[0]["upper_bound"],
            "feasible_rate_pct": 100 * summary["feasible_runs"] / summary["runs"],
            "mean_gap_to_bound_pct": statistics.mean(gaps) if gaps else None,
        })
    return summaries


def comparison_groups(summaries):
    groups = defaultdict(list)
    for row in summaries:
        groups[(row["case_sha256"], row["mode"])].append(row)
    return groups


def configuration_label(row):
    label = row["config"]
    if row["algorithm"] == "ga":
        params = json.loads(row["parameters"])
        label += f"\nP={params['pop_size']}, G={params['generations']}"
    return label


def save_plots(summaries, output_dir):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    for (case_hash, mode), group in sorted(comparison_groups(summaries).items()):
        stem = re.sub(r"[^A-Za-z0-9_-]", "_", Path(group[0]["case"]).stem)
        safe_mode = re.sub(r"[^A-Za-z0-9_-]", "_", mode)
        directory = output_dir / f"{stem}_{case_hash[:12]}_{safe_mode}"
        directory.mkdir(parents=True, exist_ok=True)
        title = f"{group[0]['case']} | mode={mode} | {case_hash[:12]}"
        labels = [configuration_label(row) for row in group]
        positions = list(range(len(group)))
        fig, axes = plt.subplots(3, 1, figsize=(max(10, len(group) * 1.1), 12))
        axes[0].bar(positions, [row["mean_value"] for row in group],
                    yerr=[row["std_value_sample"] for row in group],
                    capsize=4, color="#2563eb")
        axes[0].set_ylabel("Rata-rata objective akhir ± SD sampel")
        axes[1].bar(positions, [row["mean_duration_seconds"] for row in group],
                    color="#0d9488")
        axes[1].set_ylabel("Rata-rata durasi algoritma (detik)")
        axes[2].bar(positions, [row["feasible_rate_pct"] for row in group],
                    color="#7c3aed")
        axes[2].set(ylabel="Run feasible (%)", ylim=(0, 115))
        for index, row in enumerate(group):
            axes[2].text(index, row["feasible_rate_pct"] + 2,
                         f"{row['feasible_runs']}/{row['runs']}", ha="center")
        for ax in axes:
            ax.set_xticks(positions, labels, rotation=35, ha="right")
            ax.grid(axis="y", alpha=0.25)
            ax.set_axisbelow(True)
        fig.suptitle(title)
        fig.tight_layout()
        fig.savefig(directory / "comparison.png", dpi=150, bbox_inches="tight")
        plt.close(fig)

        for experiment, variable, xlabel in (
            ("population", "pop_size", "Jumlah populasi"),
            ("generations", "generations", "Jumlah generasi"),
        ):
            series = defaultdict(list)
            for row in group:
                if row["algorithm"] == "ga" and row["group"] == experiment:
                    fixed = json.loads(row["parameters"])
                    value = fixed.pop(variable)
                    series[json.dumps(fixed, sort_keys=True)].append((value, row))
            if not series:
                continue
            fig, axes = plt.subplots(2, 1, figsize=(9, 8), sharex=True)
            for fixed, points in sorted(series.items()):
                points.sort(key=lambda item: item[0])
                xs, values = zip(*points)
                label = ", ".join(f"{key}={value}" for key, value in json.loads(fixed).items())
                axes[0].errorbar(xs, [row["mean_value"] for row in values],
                                 yerr=[row["std_value_sample"] for row in values],
                                 marker="o", capsize=4, label=label)
                axes[1].plot(xs, [row["mean_duration_seconds"] for row in values],
                             marker="o", label=label)
            axes[0].set_ylabel("Rata-rata objective akhir ± SD sampel")
            axes[1].set(xlabel=xlabel, ylabel="Rata-rata durasi (detik)")
            axes[0].legend(fontsize=8, loc="best")
            for ax in axes:
                ax.grid(alpha=0.25)
            fig.suptitle(title)
            fig.tight_layout()
            fig.savefig(directory / f"ga_{experiment}.png", dpi=150, bbox_inches="tight")
            plt.close(fig)


def write_report(path, summaries):
    lines = [
        "# Perbandingan hasil eksperimen", "",
        "Statistik dipisahkan menurut dataset, mode, algoritma, konfigurasi, dan parameter.",
        "Objective merupakan skor dikurangi penalti. Perhatikan jumlah run feasible dan fallback.",
        "Gap dihitung terhadap upper bound, bukan global optimum yang telah dibuktikan.",
        "SD menggunakan standar deviasi sampel; satu run belum cukup untuk menilai konsistensi.",
        "Durasi hanya mencakup algoritma, tidak termasuk pembuatan grafik dan penulisan file.", "",
    ]
    for (case_hash, mode), group in sorted(comparison_groups(summaries).items()):
        case = group[0]["case"].replace("|", "\\|")
        lines.extend([
            f"## {case} — mode {mode}", "", f"Dataset SHA-256: `{case_hash}`", "",
            "| Algoritma | Konfigurasi | Run | Rata-rata | SD sampel | Min | Maks | Durasi rata-rata (s) | Feasible | Fallback | Gap ke bound (%) |",
            "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
        ])
        for row in group:
            gap = row["mean_gap_to_bound_pct"]
            gap_text = f"{gap:.2f}" if gap is not None else "—"
            config = row["config"].replace("|", "\\|")
            lines.append(
                f"| {row['algorithm']} | {config} | {row['runs']} | {row['mean_value']:.2f} "
                f"| {row['std_value_sample']:.2f} | {row['min_value']:.2f} | {row['max_value']:.2f} "
                f"| {row['mean_duration_seconds']:.4f} | {row['feasible_runs']}/{row['runs']} "
                f"| {row['fallback_runs']} | {gap_text} |"
            )
        lines.extend(["", "Parameter dan seed:", ""])
        for row in group:
            lines.append(f"- `{row['config']}`: `{row['parameters']}`; seed: {row['seeds']}.")
        lines.append("")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main(argv=None):
    parser = argparse.ArgumentParser(description="Bandingkan hasil HC, SA, dan GA yang sudah disimpan.")
    parser.add_argument("--inputs", nargs="+", type=Path,
                        default=[PROJECT_ROOT / "output_local", PROJECT_ROOT / "output_GA"])
    parser.add_argument("--output", type=Path, default=PROJECT_ROOT / "output" / "comparison")
    parser.add_argument("--no-plots", action="store_true")
    args = parser.parse_args(argv)
    try:
        rows = load_rows(args.inputs)
        summaries = summarize_comparison(rows)
    except (OSError, ValueError, KeyError, TypeError) as exc:
        parser.error(str(exc))
    args.output.mkdir(parents=True, exist_ok=True)
    write_csv(args.output / "runs.csv", rows)
    write_csv(args.output / "summary.csv", summaries)
    write_json(args.output / "summary.json", summaries)
    write_report(args.output / "comparison.md", summaries)
    if not args.no_plots:
        save_plots(summaries, args.output)
    print(f"Selesai: {len(rows)} run, {len(summaries)} konfigurasi. Hasil: {args.output.resolve()}")
    return summaries


if __name__ == "__main__":
    main()
