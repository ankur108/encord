"""Content and size analysis of storage items."""

from collections import Counter

from encord.storage import StorageItem


def analyse_content(
    image_items: list[StorageItem],
    json_items: list[StorageItem],
) -> dict:
    def _size_stats(items: list[StorageItem]) -> dict:
        sizes = [i.file_size for i in items if i.file_size is not None]
        if not sizes:
            return {"count": len(items), "total_bytes": 0}
        return {
            "count": len(items),
            "total_bytes": sum(sizes),
            "min_bytes": min(sizes),
            "max_bytes": max(sizes),
            "avg_bytes": int(sum(sizes) / len(sizes)),
        }

    all_items = image_items + json_items
    all_sizes = [i.file_size for i in all_items if i.file_size is not None]

    resolutions: Counter = Counter()
    for item in image_items:
        if item.width and item.height:
            resolutions[f"{item.width}x{item.height}"] += 1

    mime_counts: Counter = Counter(i.mime_type for i in all_items if i.mime_type)

    return {
        "total_items": len(all_items),
        "by_type": {
            "image": _size_stats(image_items),
            "json_text": _size_stats(json_items),
        },
        "by_mime_type": dict(mime_counts.most_common()),
        "resolution_distribution": dict(resolutions.most_common()),
        "overall_size": {
            "total_bytes": sum(all_sizes),
            "min_bytes": min(all_sizes) if all_sizes else None,
            "max_bytes": max(all_sizes) if all_sizes else None,
            "avg_bytes": int(sum(all_sizes) / len(all_sizes)) if all_sizes else None,
        },
    }
