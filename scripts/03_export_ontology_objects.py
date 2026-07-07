import json
import logging
import sys
from pathlib import Path
from google.cloud import storage

sys.path.append(str(Path(__file__).resolve().parents[1]))
from src.config import ONTOLOGY_EXPORT_SOURCE, ONTOLOGY_EXPORT_PATH,OUTPUT_FILE,BLOB_LIMIT

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


SHAPE_KEYS = {"box2d", "poly2d", "point", "box3d", "poly3d"}

def collect(data: dict, ontology: dict):
    '''Collects object categories, shapes, and attributes from the given "
    data and updates the ontology dictionary.''' 
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
    '''Loads ontology data from local JSON files in the specified directory.'''
    path = Path(directory)
    if not path.is_dir():
        sys.exit(f"Error: directory not found: {directory}")
    ontology = {}
    for json_file in sorted(path.glob("*.json")):
        with open(json_file) as fh:
            collect(json.load(fh), ontology)
        logger.info("Loaded %s", json_file.name)
    return ontology


def load_gcs(gcs_path: str, blob_limit : int = BLOB_LIMIT) -> dict:
    '''Loads ontology data from all .json files under a gs://bucket/prefix path,
    recursing through every folder and sub-folder.'''
    
    if not gcs_path.startswith("gs://"):
        sys.exit(f"Error: expected a gs:// path, got: {gcs_path}")

    bucket_name = gcs_path[len("gs://"):].split("/", 1)[0]
    # Public bucket — use an anonymous client (no credentials required).
    bucket = storage.Client.create_anonymous_client().bucket(bucket_name)

    ontology = {}
    blob_limit = 0
    for blob in bucket.list_blobs():
        if not blob.name.endswith(".json"):
            continue

        if not 'test' in blob.name:
            continue # Skip non-test files
        
        logger.info("Downloading %s", blob.name)

        blob_limit += 1
        if blob_limit > BLOB_LIMIT:
            logger.info("Reached blob limit of %d, stopping download.", blob_limit)
            break
        try:
            collect(json.loads(blob.download_as_text()), ontology)
        except Exception as exc:
            logger.warning("Skipping %s: %s", blob.name, exc)
    return ontology


def main():
    source = ONTOLOGY_EXPORT_SOURCE
    path = ONTOLOGY_EXPORT_PATH

    logger.info("Source: %s  Path: %s", source, path)
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

    with open(OUTPUT_FILE, "w") as fh:
        json.dump(output, fh, indent=2)

    logger.info("Exported %d categories → %s", len(output), OUTPUT_FILE)


if __name__ == "__main__":
    main()
