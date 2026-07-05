"""
GCS bucket analysis package.

Quick start:
    from exploration.bucket_analysis import analyse
    analyse(output_dir="reports", sample=5000)

    # Regenerate MD from an existing JSON report (no API calls):
    from exploration.bucket_analysis import regenerate_md_from_json
    regenerate_md_from_json("reports/bucket_analysis.json")

CLI:
    python -m exploration.bucket_analysis --help
    python -m exploration.bucket_analysis --from-json reports/bucket_analysis.json
"""

import json
import sys
from pathlib import Path
from typing import Optional

from src.config import STORAGE_FOLDER_NAME
from src.datasets.storage import _find_existing_folder

from ._annotations import analyse_categories, analyse_coverage
from ._content import analyse_content
from ._fetcher import download_json_contents, fetch_storage_items
from ._report import build_json_report, build_md_report, write_reports


def analyse(
    output_dir: str | Path = "reports",
    sample: Optional[int] = None,
    concurrency: int = 50,
    verbose: bool = True,
) -> tuple[dict, str]:
    """
    Run the full bucket analysis and write reports to output_dir.

    Args:
        output_dir: Directory for output files (created if absent).
        sample:     Analyse only N randomly sampled JSON files (None = all).
        concurrency: Parallel download threads for JSON content.
        verbose:    Print progress to stderr.

    Returns:
        (json_report_dict, markdown_report_str)
    """
    folder = _find_existing_folder()
    if folder is None:
        raise RuntimeError(
            f"Storage folder '{STORAGE_FOLDER_NAME}' not found. "
            "Run `python -m scripts.create_storage_folder` first."
        )

    image_items, json_items = fetch_storage_items(folder, verbose=verbose)
    json_data = download_json_contents(
        json_items, concurrency=concurrency, sample=sample, verbose=verbose
    )

    if verbose:
        print("Computing analysis...", file=sys.stderr, flush=True)

    content = analyse_content(image_items, json_items)
    coverage = analyse_coverage(image_items, json_data)
    categories = analyse_categories(json_data)

    meta = {
        "folder_name": folder.name,
        "folder_uuid": str(folder.uuid),
        "sampled": sample is not None and sample < len(json_items),
        "sample_size": min(sample, len(json_items)) if sample else len(json_items),
        "total_json_items": len(json_items),
    }

    report_json = build_json_report(content, coverage, categories, meta)
    report_md = build_md_report(content, coverage, categories, meta)

    json_path, md_path = write_reports(report_json, report_md, Path(output_dir))
    if verbose:
        print(f"Reports written:", file=sys.stderr)
        print(f"  {json_path}", file=sys.stderr)
        print(f"  {md_path}", file=sys.stderr)

    return report_json, report_md


def regenerate_md_from_json(
    json_path: str | Path,
    output_dir: str | Path | None = None,
    verbose: bool = True,
) -> str:
    """
    Regenerate the markdown report from an existing JSON report file.
    No API calls — reads the JSON and rewrites bucket_analysis.md.

    Args:
        json_path:  Path to an existing bucket_analysis.json file.
        output_dir: Where to write the updated .md (defaults to same dir as json_path).
        verbose:    Print progress to stderr.

    Returns:
        The markdown report string.
    """
    json_path = Path(json_path)
    report = json.loads(json_path.read_text())

    content = report["content"]
    coverage = report["annotation_coverage"]
    categories = report["category_analysis"]
    meta = report.get("meta", {})

    report_md = build_md_report(content, coverage, categories, meta)

    out_dir = Path(output_dir) if output_dir else json_path.parent
    md_path = out_dir / "bucket_analysis.md"
    md_path.write_text(report_md)

    if verbose:
        print(f"MD report written to: {md_path}", file=sys.stderr)

    return report_md
