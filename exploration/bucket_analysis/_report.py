"""Build JSON and Markdown reports from analysis results."""

import json
from datetime import datetime, timezone
from pathlib import Path


def _fmt_bytes(n: int | float | None) -> str:
    if n is None:
        return "N/A"
    n = float(n)
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if n < 1024:
            return f"{n:.1f} {unit}"
        n /= 1024
    return f"{n:.1f} PB"


def _pct(part: int, total: int) -> str:
    if not total:
        return "0.0%"
    return f"{part / total * 100:.1f}%"


def build_json_report(content: dict, coverage: dict, categories: dict, meta: dict) -> dict:
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "meta": meta,
        "content": content,
        "annotation_coverage": coverage,
        "category_analysis": categories,
    }


def build_md_report(content: dict, coverage: dict, categories: dict, meta: dict) -> str:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    lines: list[str] = []
    A = lines.append

    A("# GCS Bucket Analysis Report")
    A("")
    A(f"**Generated:** {now}  ")
    A(f"**Folder:** `{meta.get('folder_name')}` (`{meta.get('folder_uuid')}`)  ")
    if meta.get("sampled"):
        A(
            f"> **Note:** Category/attribute analysis is based on a **sample of "
            f"{meta['sample_size']:,}** out of **{meta['total_json_items']:,}** JSON files."
        )
    A("")
    A("---")
    A("")

    # ── 1. Content Overview ───────────────────────────────────────────────────
    A("## 1. Content Overview")
    A("")
    img = content["by_type"].get("image", {})
    txt = content["by_type"].get("json_text", {})
    overall = content["overall_size"]

    A("| Metric | Value |")
    A("|--------|-------|")
    A(f"| Total items | {content['total_items']:,} |")
    A(f"| Total size | {_fmt_bytes(overall['total_bytes'])} |")
    A(f"| Image files | {img.get('count', 0):,} |")
    A(f"| JSON annotation files | {txt.get('count', 0):,} |")
    A("")

    A("### File Type Details")
    A("")
    A("| Type | Count | Total Size | Avg Size | Min Size | Max Size |")
    A("|------|------:|----------:|--------:|--------:|--------:|")
    for type_label, stats in content["by_type"].items():
        A(
            f"| {type_label} | {stats['count']:,} "
            f"| {_fmt_bytes(stats.get('total_bytes'))} "
            f"| {_fmt_bytes(stats.get('avg_bytes'))} "
            f"| {_fmt_bytes(stats.get('min_bytes'))} "
            f"| {_fmt_bytes(stats.get('max_bytes'))} |"
        )
    A("")

    A("### MIME Type Distribution")
    A("")
    A("| MIME Type | Count |")
    A("|-----------|------:|")
    for mime, count in content["by_mime_type"].items():
        A(f"| `{mime}` | {count:,} |")
    A("")

    if content.get("resolution_distribution"):
        A("### Image Resolution Distribution")
        A("")
        A("| Resolution | Count |")
        A("|-----------|------:|")
        for res, count in content["resolution_distribution"].items():
            A(f"| {res} | {count:,} |")
        A("")

    A("---")
    A("")

    # ── 2. Annotation Coverage ────────────────────────────────────────────────
    A("## 2. Annotation Coverage")
    A("")
    total_img = coverage["total_images"]
    with_ann = coverage["with_annotations"]
    without_ann = coverage["without_annotations"]

    A("| Metric | Count | Share |")
    A("|--------|------:|------:|")
    A(f"| Total images | {total_img:,} | 100% |")
    A(f"| **With annotation data** | **{with_ann:,}** | **{_pct(with_ann, total_img)}** |")
    A(f"| Without annotation data | {without_ann:,} | {_pct(without_ann, total_img)} |")
    A("")

    if coverage.get("unannotated_samples"):
        n = len(coverage["unannotated_samples"])
        A(f"<details><summary>Sample unannotated images (first {n})</summary>")
        A("")
        for fname in coverage["unannotated_samples"]:
            A(f"- `{fname}`")
        A("")
        A("</details>")
        A("")

    A("---")
    A("")

    # ── 3. Category Distribution ──────────────────────────────────────────────
    A("## 3. Category Distribution")
    A("")
    cat_data = categories
    total_obj = cat_data["total_objects_parsed"]

    A(f"| Metric | Value |")
    A(f"|--------|-------|")
    A(f"| JSON files analysed | {cat_data['json_files_analysed']:,} |")
    A(f"| Files containing objects | {cat_data['json_files_with_objects']:,} |")
    A(f"| Total objects parsed | {total_obj:,} |")
    A(f"| Distinct categories | {cat_data['distinct_category_count']} |")
    A("")

    if cat_data["categories"]:
        A("| Category | Object Count | Share |")
        A("|----------|-------------:|------:|")
        for cat, count in cat_data["categories"].items():
            A(f"| `{cat}` | {count:,} | {_pct(count, total_obj)} |")
        A("")
    else:
        A("_No category data found._")
        A("")

    A("---")
    A("")

    # ── 4. Frame-Level Attributes ─────────────────────────────────────────────
    A("## 4. Frame-Level Attributes")
    A("")
    frame_attrs = cat_data.get("frame_attribute_types", {})
    files_with_fa = cat_data.get("json_files_with_frame_attributes", 0)
    total_frames = cat_data.get("total_frames_parsed", 0)
    A(f"| Metric | Value |")
    A(f"|--------|-------|")
    A(f"| Files with frame attributes | {files_with_fa:,} |")
    A(f"| Total frames parsed | {total_frames:,} |")
    A(f"| Distinct frame attribute types | {cat_data.get('distinct_frame_attribute_type_count', 0)} |")
    A("")

    if frame_attrs:
        for attr_name, attr_info in frame_attrs.items():
            A(f"### `{attr_name}`")
            A("")
            A(f"Distinct values: **{attr_info['distinct_values']}**")
            A("")
            A("| Value | Count | Share |")
            A("|-------|------:|------:|")
            attr_total = sum(attr_info["value_counts"].values())
            for val, cnt in list(attr_info["value_counts"].items())[:25]:
                A(f"| `{val}` | {cnt:,} | {_pct(cnt, attr_total)} |")
            if attr_info["distinct_values"] > 25:
                A(f"| _(+{attr_info['distinct_values'] - 25} more)_ | | |")
            A("")
    else:
        A("_No frame-level attributes found in this dataset split._")
        A("")

    A("---")
    A("")

    # ── 5. Object-Level Attributes ────────────────────────────────────────────
    A("## 5. Object-Level Attributes")
    A("")
    A(f"**Distinct object attribute types:** {cat_data.get('distinct_object_attribute_type_count', 0)}")
    A("")

    for attr_name, attr_info in cat_data.get("object_attribute_types", cat_data.get("attribute_types", {})).items():
        A(f"### `{attr_name}`")
        A("")
        A(f"Distinct values: **{attr_info['distinct_values']}**")
        A("")
        A("| Value | Count | Share |")
        A("|-------|------:|------:|")
        for val, cnt in list(attr_info["value_counts"].items())[:25]:
            A(f"| `{val}` | {cnt:,} | {_pct(cnt, total_obj)} |")
        if attr_info["distinct_values"] > 25:
            A(f"| _(+{attr_info['distinct_values'] - 25} more)_ | | |")
        A("")

    if not cat_data.get("object_attribute_types") and not cat_data.get("attribute_types"):
        A("_No object-level attribute data found._")
        A("")

    return "\n".join(lines)


def write_reports(report_json: dict, report_md: str, output_dir: Path) -> tuple[Path, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / "bucket_analysis.json"
    md_path = output_dir / "bucket_analysis.md"
    json_path.write_text(json.dumps(report_json, indent=2, default=str))
    md_path.write_text(report_md)
    return json_path, md_path
