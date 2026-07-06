import json
import sys
import urllib.request
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))
from src.config import ONTOLOGY_EXPORT_SOURCE, ONTOLOGY_EXPORT_PATH


SHAPE_KEYS = {"box2d", "poly2d", "point", "box3d", "poly3d"}
REPORTS_DIR = Path(__file__).resolve().parents[1] / "reports"
OUTPUT_FILE = REPORTS_DIR / "ontology_objects.json"


def collect(data: dict, ontology: dict):
    for frame in data.get("frames", []):
        for obj in frame.get("objects", []):
            category = obj.get("category", "unknown")
            shape = next((k for k in obj if k in SHAPE_KEYS), "unknown")
            attrs = list(obj.get("attributes", {}).keys())
            if category not in ontology:
                ontology[category] = {"shapes": set(), "attributes": set()}
            ontology[category]["shapes"].add(shape)
            ontology[category]["attributes"].update(attrs)


def load_local(directory: str) -> dict:
    path = Path(directory)
    if not path.is_dir():
        sys.exit(f"Error: directory not found: {directory}")
    ontology = {}
    for json_file in sorted(path.glob("*.json")):
        with open(json_file) as fh:
            collect(json.load(fh), ontology)
        print(f"  Loaded {json_file.name}")
    return ontology


def load_gcs(bucket_url: str) -> dict:
    if bucket_url.startswith("gs://"):
        bucket_url = bucket_url.replace("gs://", "https://storage.googleapis.com/", 1)
    without_scheme = bucket_url.replace("https://storage.googleapis.com/", "")
    parts = without_scheme.rstrip("/").split("/", 1)
    bucket = parts[0]
    prefix = (parts[1] + "/") if len(parts) > 1 else ""
    list_url = (
        f"https://storage.googleapis.com/storage/v1/b/{bucket}/o"
        f"?prefix={prefix}&fields=items(name)"
    )
    try:
        with urllib.request.urlopen(list_url) as resp:
            items = json.loads(resp.read()).get("items", [])
    except Exception as exc:
        sys.exit(f"Error listing GCS bucket: {exc}")

    ontology = {}
    for item in items:
        name = item["name"]
        if not name.endswith(".json"):
            continue
        url = f"https://storage.googleapis.com/{bucket}/{name}"
        print(f"  Downloading {name}")
        try:
            with urllib.request.urlopen(url) as resp:
                collect(json.load(resp), ontology)
        except Exception as exc:
            print(f"  Warning: skipping {name}: {exc}")
    return ontology


def main():
    source = ONTOLOGY_EXPORT_SOURCE
    path = ONTOLOGY_EXPORT_PATH

    print(f"\nSource: {source}  Path: {path}\n")
    ontology = load_local(path) if source == "local" else load_gcs(path)

    if not ontology:
        sys.exit("No objects found.")

    output = [
        {
            "category": category,
            "shapes": sorted(data["shapes"]),
            "attributes": sorted(data["attributes"]),
        }
        for category, data in sorted(ontology.items())
    ]

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_FILE, "w") as fh:
        json.dump(output, fh, indent=2)

    print(f"\nExported {len(output)} categories → {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
