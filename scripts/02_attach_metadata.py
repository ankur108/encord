import json
import logging
import os
from src.utils.encord_client import user_client
from google.cloud import storage
from src.config import (
    GCS_REMOTE_URL,
    STORAGE_FOLDER_NAME,
)
from encord.storage import StorageItemType
from encord.http.bundle import Bundle

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Attributes to copy from each BDD JSON label onto the Encord image metadata.
_METADATA_ATTRIBUTES = ("weather", "scene", "timeofday")

def get_all_json_names_from_gcs(remote_url: str = GCS_REMOTE_URL) -> dict:
    """Lists the JSON files at a GCS remote URL and returns a dict of their names.
    """
    if not remote_url.startswith("gs://"):
        raise ValueError(f"Expected a gs:// URL, got: {remote_url}")

    bucket_name, _, prefix = remote_url[len("gs://"):].partition("/")

    client = storage.Client()
    bucket = client.bucket(bucket_name)

    prefix = f"{prefix.rstrip('/')}/" if prefix else ""

    logger.info("Listing JSON files under '%s'.", remote_url)
    json_files = {}
    for blob in bucket.list_blobs(prefix=prefix):
        if not blob.name.endswith(".json"):
            continue
        file_name = blob.name.rsplit("/", 1)[-1]
        file_stem = file_name[: -len(".json")]
        json_files[file_stem] = blob.name

    logger.info("Found %d JSON file(s) in GCS.", len(json_files))
    return json_files

def get_image_metadata_from_encord(folder_name: str = STORAGE_FOLDER_NAME) -> list:
    """Lists all image items in the Encord storage folder and returns them as a dict.

    Looks up the storage folder created earlier by name and returns a mapping of
    ``{item_name: StorageItem}`` for every image in the folder.
    """
    storage_folder = next(
        (f for f in user_client.list_storage_folders(search=folder_name)
         if f.name == folder_name),
        None,
    )
    if storage_folder is None:
        raise ValueError(f"Storage folder '{folder_name}' not found.")

    logger.info("Listing image items in storage folder '%s'.", folder_name)
    images = []
    for item in storage_folder.list_items(item_types=[StorageItemType.IMAGE]):
        images.append(item)
    logger.info("Found %d image(s) in Encord folder '%s'.", len(images), folder_name)
    return images



def attach_metadata_to_storage_folder(
    folder_name: str = STORAGE_FOLDER_NAME,
    remote_url: str = GCS_REMOTE_URL,
) -> None:
    """For each image that has a matching JSON label, attach the label's
    ``weather``, ``scene`` and ``timeofday`` attributes to the image's metadata
    in Encord.
    """
    json_files = get_all_json_names_from_gcs(remote_url)
    images = get_image_metadata_from_encord(folder_name)

    bucket_name = remote_url[len("gs://"):].partition("/")[0]
    bucket = storage.Client().bucket(bucket_name)

    updated = 0
    skipped = 0
    with Bundle() as bundle:
        for item in images:
            # Match image to its JSON label by filename stem (e.g. "abc.jpg" -> "abc").
            stem = os.path.splitext(item.name)[0]
            blob_name = json_files.get(stem)
            if blob_name is None:
                logger.debug("No matching JSON for image '%s', skipping.", item.name)
                skipped += 1
                continue

            label = json.loads(bucket.blob(blob_name).download_as_text())
            attributes = label.get("attributes", {})
            new_values = {
                key: attributes[key]
                for key in _METADATA_ATTRIBUTES
                if key in attributes
            }
            if not new_values:
                logger.warning("JSON '%s' has no target attributes, skipping.", blob_name)
                skipped += 1
                continue

            merged = {**(item.client_metadata or {}), **new_values}
            item.update(client_metadata=merged, bundle=bundle)
            logger.info("Attaching metadata to '%s': %s", item.name, new_values)
            updated += 1

    logger.info("Metadata update complete: %d updated, %d skipped.", updated, skipped)

def main():
    try:
        attach_metadata_to_storage_folder()
    except Exception as e:
        logger.error("An error occurred: %s", e)
        raise

if __name__ == "__main__":
    main()


 