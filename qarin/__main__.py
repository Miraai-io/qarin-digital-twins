"""Command line: python -m qarin check | run | score | analyze. Run any command with -h for its options."""
import argparse
import sys
from pathlib import Path

from . import __version__
from .files import check as check_files

ROOT = Path(__file__).resolve().parents[1]
PROFILES = ROOT / "data" / "profiles"


def main(argv=None):
    ap = argparse.ArgumentParser(prog="python -m qarin", description="Qarin - Digital Twins " + __version__)
    sub = ap.add_subparsers(dest="cmd", required=True)

    c = sub.add_parser("check", help="check your items, scales and formats files before a run")
    c.add_argument("--items", required=True); c.add_argument("--scales"); c.add_argument("--formats")

    r = sub.add_parser("run", help="run the twins on your items")
    r.add_argument("--items", required=True); r.add_argument("--formats")
    r.add_argument("--out", required=True, help="results file, e.g. results/my_study.csv")
    r.add_argument("--profiles", default=str(PROFILES), help="a profile file or a folder of them (default: all 100)")
    r.add_argument("--factor-scoped", action="store_true", help="also answer with the factor-scoped profiles (items need a factor)")
    r.add_argument("--workers", type=int, default=4, help="people run in parallel")
    r.add_argument("--dry-run", action="store_true", help="print the first request and stop; sends nothing")

    s = sub.add_parser("score", help="twin scale scores from a results file")
    s.add_argument("--results", required=True); s.add_argument("--scales", required=True)
    s.add_argument("--out", required=True); s.add_argument("--sum", action="store_true", help="sum instead of mean")

    a = sub.add_parser("analyze", help="item and scale statistics, and comparison with the people")
    a.add_argument("--results", required=True); a.add_argument("--scales", required=True)
    a.add_argument("--out", required=True, help="output folder")
    a.add_argument("--human", help="CSV of the people's own scale scores: qarin_id and one column per scale")
    a.add_argument("--draws", type=int, default=10); a.add_argument("--seed", type=int, default=20260930)
    a.add_argument("--sum", action="store_true", help="sum instead of mean")

    args = ap.parse_args(argv)
    if args.cmd == "check":
        errors, warnings = check_files(args.items, args.scales, args.formats)
        for w in warnings: print("warning:", w)
        for e in errors: print("error:", e)
        print("OK: files are ready to run." if not errors else f"{len(errors)} error(s): fix them and check again.")
        sys.exit(1 if errors else 0)
    if args.cmd == "run":
        errors, _ = check_files(args.items, None, args.formats)
        if errors:
            for e in errors: print("error:", e)
            sys.exit(1)
        from .run import dry_run, run
        if args.dry_run:
            dry_run(args.profiles, args.items, args.formats)
        else:
            run(args.profiles, args.items, args.out, args.formats, args.factor_scoped, args.workers)
    if args.cmd == "score":
        from .score import score
        S = score(args.results, args.scales, "sum" if args.sum else "mean")
        Path(args.out).parent.mkdir(parents=True, exist_ok=True)
        S.round(4).to_csv(args.out, index=False); print(f"written {args.out}")
    if args.cmd == "analyze":
        from .analyze import analyze
        print(analyze(args.results, args.scales, args.out, args.draws, args.seed, args.human, "sum" if args.sum else "mean"))


if __name__ == "__main__":
    main()
