import argparse
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Brimanuy cargo-deck local search simulator."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    local = subparsers.add_parser("local", help="Run local-search experiments.")
    local.add_argument("--case", default="src/data/case1.json")
    local.add_argument("--mode", choices=("fee", "urgency", "area"), default="fee")
    local.add_argument("--output", type=Path, default=PROJECT_ROOT / "output" / "output_local")
    local.add_argument("--runs", type=int, default=3)
    local.add_argument("--no-plots", action="store_true")

    ga = subparsers.add_parser("ga", help="Run the GA experiment matrix.")
    ga.add_argument("--case", default="src/data/case1.json")
    ga.add_argument("--mode", choices=("fee", "urgency", "area"), default="fee")
    ga.add_argument("--output", type=Path, default=PROJECT_ROOT / "output" / "output_GA")
    ga.add_argument("--no-plots", action="store_true")

    web = subparsers.add_parser("web", help="Start the FastAPI web application.")
    web.add_argument("--host", default="127.0.0.1")
    web.add_argument("--port", type=int, default=8000)
    args, remaining = parser.parse_known_args(argv)

    if args.command == "local":
        from experiments.exp_local import main as local_main
        local_args = [
            "--case", args.case, "--mode", args.mode,
            "--output", str(args.output), "--runs", str(args.runs),
        ]
        if args.no_plots:
            local_args.append("--no-plots")
        return local_main(local_args)
    if args.command == "ga":
        from experiments.exp_ga import main as ga_main
        ga_args = [
            "--case", args.case, "--mode", args.mode,
            "--output", str(args.output),
        ]
        if args.no_plots:
            ga_args.append("--no-plots")
        ga_args.extend(remaining)
        return ga_main(ga_args)

    if remaining:
        parser.error(f"Argumen web tidak dikenal: {' '.join(remaining)}")
    import uvicorn
    uvicorn.run("web.app:app", host=args.host, port=args.port, reload=False)


if __name__ == "__main__":
    main()