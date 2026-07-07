import json
import logging
import os
from src.utils.encord_client import user_client
from google.cloud import storage
from src.config import (
    GCS_REMOTE_URL,
    STORAGE_FOLDER_NAME,
)
from encord.http.bundle import Bundle
from pathlib import PurePosixPath

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Maps each BDD JSON attribute (source key) to the Encord metadata field name
# required by the customer's schema (target key). The customer mandates exactly:
# weather (str), scene (str), time_of_day (str) — note the underscore.
_METADATA_FIELD_MAP = {
    "weather": "weather",
    "scene": "scene",
    "timeofday": "timeofday",
}
_IMAGE_EXTENSIONS = (".jpg", ".jpeg")


def create_image_metadata_dict(remote_url: str = GCS_REMOTE_URL) -> dict:

    if not remote_url.startswith("gs://"):
        raise ValueError(f"Expected a gs:// URL, got: {remote_url}")

    # 1. Scan GCS once, separating image files from JSON label files.
    bucket_name, _, prefix = remote_url[len("gs://"):].partition("/")
    bucket = storage.Client.create_anonymous_client().bucket(bucket_name)
    prefix = f"{prefix.rstrip('/')}/" if prefix else ""

    json_files = {}
    image_names = []
    for blob in bucket.list_blobs(prefix=prefix):
        file_name = blob.name.rsplit("/", 1)[-1]
        if file_name.endswith(".json"):
            json_files[file_name[: -len(".json")]] = blob.name
        elif file_name.lower().endswith(_IMAGE_EXTENSIONS):
            image_names.append(file_name)
    logger.info("Found %d image(s) and %d JSON file(s) in GCS.",
                len(image_names), len(json_files))

    # 2. For each image with a matching JSON, extract the metadata attributes.
    metadata = {}
    for image_name in image_names:
        # Match image to its JSON by filename stem (e.g. "abc.jpg" -> "abc").
        stem = os.path.splitext(image_name)[0]
        blob_name = json_files.get(stem)
        if blob_name is None:
            logger.debug("No matching JSON for image '%s', skipping.", image_name)
            continue

        label = json.loads(bucket.blob(blob_name).download_as_text())
        attributes = label.get("attributes", {})
        new_values = {
            target: attributes[source]
            for source, target in _METADATA_FIELD_MAP.items()
            if source in attributes
        }
        if not new_values:
            logger.warning("JSON '%s' has no target attributes, skipping.", blob_name)
            continue

        metadata[image_name] = new_values

    logger.info("Built metadata for %d image(s).", len(metadata))
    return metadata

def ensure_metadata_schema() -> None:
    print("\n[1/4] Creating metadata schema...")
    schema = user_client.metadata_schema()

    # Register exactly the fields we write (the target names in the field map),
    # so the schema keys match the stored client_metadata keys.
    for field_name in _METADATA_FIELD_MAP.values():
        if not schema.has_key(field_name):
            schema.add_scalar(field_name, data_type="varchar")
            print(f"  Added: {field_name} (varchar)")
        else:
            print(f"  Already exists: {field_name}")
    schema.save()


def attach_metadata_to_images(metadata: dict, storage_folder_name: str = STORAGE_FOLDER_NAME) -> None:
    # Look up the folder by name. get_storage_folder() requires a UUID, so we
    # search instead and match on the exact name (search is a substring filter).
    storage_folder = next(
        (f for f in user_client.list_storage_folders(search=storage_folder_name)
         if f.name == storage_folder_name),
        None,
    )
    if storage_folder is None:
        raise ValueError(f"Storage folder '{storage_folder_name}' not found.")


    items_by_name = {}
    for item in storage_folder.list_items():
        items_by_name.setdefault(PurePosixPath(item.name).name, []).append(item)

    attached = 0
    with Bundle() as bundle:
        for image_name, meta in metadata.items():
            items = items_by_name.get(image_name)
            if not items:
                logger.warning(
                    "Image '%s' not found in folder '%s', skipping.",
                    image_name, storage_folder_name,
                )
                continue
            for item in items:
                item.update(client_metadata=meta, bundle=bundle)
                logger.info("Updated metadata for '%s': %s", image_name, meta)
                attached += 1

    logger.info("Attached metadata to %d image item(s).", attached)

def main() -> None:
    ensure_metadata_schema()
    metadata = create_image_metadata_dict()
    attach_metadata_to_images(metadata)

if __name__ == "__main__":
    main()

