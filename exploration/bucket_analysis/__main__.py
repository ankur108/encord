"""
CLI entry point.

Usage:
    # Full analysis (downloads all 100k JSON files, ~3-4 min):
    python -m exploration.bucket_analysis --output-dir reports

    # Quick analysis with a random sample of JSON files:
    python -m exploration.bucket_analysis --output-dir reports --sample 5000

    # Tune parallelism:
    python -m exploration.bucket_analysis --concurrency 100
"""

import argparse
import sys


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="python -m exploration.bucket_analysis",
        description="Analyse the GCS-synced Encord storage folder and write reports.",
    )
    parser.add_argument(
        "--output-dir", "-o",
        default="reports",
        metavar="DIR",
        help="Directory for output files (default: reports/)",
    )
    parser.add_argument(
        "--sample", "-s",
        type=int,
        default=None,
        metavar="N",
        help="Analyse only N randomly sampled JSON files (default: all ~100k)",
    )
    parser.add_argument(
        "--concurrency", "-c",
        type=int,
        default=50,
        metavar="N",
        help="Parallel download threads (default: 50)",
    )
    parser.add_argument(
        "--quiet", "-q",
        action="store_true",
        help="Suppress progress output",
    )
    parser.add_argument(
        "--from-json",
        metavar="FILE",
        default=None,
        help="Regenerate the MD report from an existing JSON report file (no API calls)",
    )
    args = parser.parse_args()

    from exploration.bucket_analysis import analyse, regenerate_md_from_json

    try:
        if args.from_json:
            regenerate_md_from_json(
                json_path=args.from_json,
                output_dir=args.output_dir if args.output_dir != "reports" else None,
                verbose=not args.quiet,
            )
        else:
            analyse(
                output_dir=args.output_dir,
                sample=args.sample,
                concurrency=args.concurrency,
                verbose=not args.quiet,
            )
    except RuntimeError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
