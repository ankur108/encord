"""Annotation coverage and category/attribute analysis for BDD100K-style JSON files.

JSON schema (per file):
  {
    "name": "<stem>",           # stem + ".jpg" = image filename
    "frames": [
      {
        "timestamp": <int>,
        "objects": [
          {
            "category": "<str>",
            "id": <int>,
            "attributes": {
              "occluded": <bool>,
              "truncated": <bool>,
              "trafficLightColor": "<str>"
            },
            "box2d": { "x1", "y1", "x2", "y2" }
          }
        ]
      }
    ]
  }
"""

from collections import Counter, defaultdict

from encord.storage import StorageItem


def _iter_objects(data: dict):
    """Yield every object dict from all frames."""
    for frame in data.get("frames", []):
        yield from frame.get("objects", [])


def analyse_coverage(
    image_items: list[StorageItem],
    json_data: list[tuple[str, dict]],
) -> dict:
    """Return annotation coverage stats.

    Image item names may contain a path prefix (e.g. 'folder/split/img.jpg').
    JSON "name" is the bare stem (e.g. 'img').  We match on basename only.
    """
    # Map bare filename → full item name (for reporting)
    basename_to_full: dict[str, str] = {
        item.name.rsplit("/", 1)[-1]: item.name for item in image_items
    }
    image_basenames = set(basename_to_full.keys())

    annotated_basenames: set[str] = set()
    for _item_name, data in json_data:
        stem = data.get("name", "")
        candidate = stem + ".jpg"
        if candidate in image_basenames:
            annotated_basenames.add(candidate)

    unannotated_basenames = image_basenames - annotated_basenames
    total = len(image_basenames)

    unannotated_full = sorted(
        basename_to_full[b] for b in unannotated_basenames
    )

    return {
        "total_images": total,
        "with_annotations": len(annotated_basenames),
        "without_annotations": len(unannotated_basenames),
        "coverage_pct": round(len(annotated_basenames) / total * 100, 2) if total else 0.0,
        "unannotated_samples": unannotated_full[:20],
    }


def analyse_categories(json_data: list[tuple[str, dict]]) -> dict:
    """Return category distribution, frame-level and object-level attribute counts."""
    categories: Counter = Counter()
    frame_attr_values: dict[str, Counter] = defaultdict(Counter)
    obj_attr_values: dict[str, Counter] = defaultdict(Counter)
    total_objects = 0
    total_frames = 0
    files_with_objects = 0
    files_with_frame_attrs = 0

    for _item_name, data in json_data:
        objects = list(_iter_objects(data))
        frames = data.get("frames", [])
        total_frames += len(frames)

        # Scene-level attributes at the top level: {"weather": ..., "scene": ..., "timeofday": ...}
        top_attrs = data.get("attributes", {})
        if top_attrs:
            files_with_frame_attrs += 1
            for attr_key, attr_val in top_attrs.items():
                frame_attr_values[attr_key][str(attr_val)] += 1

        # Object-level attributes (occluded, truncated, trafficLightColor, etc.)
        if objects:
            files_with_objects += 1
        for obj in objects:
            total_objects += 1
            cat = obj.get("category")
            if cat:
                categories[str(cat)] += 1
            for attr_key, attr_val in obj.get("attributes", {}).items():
                obj_attr_values[attr_key][str(attr_val)] += 1

    def _fmt_attr(attr_dict: dict[str, Counter]) -> dict:
        return {
            k: {
                "distinct_values": len(v),
                "value_counts": dict(v.most_common()),
            }
            for k, v in sorted(attr_dict.items())
        }

    return {
        "total_objects_parsed": total_objects,
        "total_frames_parsed": total_frames,
        "json_files_analysed": len(json_data),
        "json_files_with_objects": files_with_objects,
        "json_files_with_frame_attributes": files_with_frame_attrs,
        "distinct_category_count": len(categories),
        "categories": dict(categories.most_common()),
        # Frame-level (scene) attributes
        "distinct_frame_attribute_type_count": len(frame_attr_values),
        "frame_attribute_types": _fmt_attr(frame_attr_values),
        # Object-level attributes
        "distinct_object_attribute_type_count": len(obj_attr_values),
        "object_attribute_types": _fmt_attr(obj_attr_values),
        # Keep legacy key so existing JSON consumers don't break
        "distinct_attribute_type_count": len(obj_attr_values),
        "attribute_types": _fmt_attr(obj_attr_values),
    }
