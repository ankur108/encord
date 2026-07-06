import logging
import sys

from encord.orm.dataset import StorageLocation
from encord.storage import StorageItemType

from src.config import (
    DATASET_NAME,
    STORAGE_FOLDER_NAME,
)
from src.utils.encord_client import user_client

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_storage_folder(folder_name: str):
    """Look up the previously created storage folder by name."""
    folder = next(
        (f for f in user_client.list_storage_folders(search=folder_name)
         if f.name == folder_name),
        None,
    )
    if folder is None:
        raise ValueError(f"Storage folder '{folder_name}' not found.")
    return folder


def create_dataset_from_storage_folder(
    dataset_name: str = DATASET_NAME,
    folder_name: str = STORAGE_FOLDER_NAME,
) -> str:
    """Create a dataset and link all image items from the storage folder into it.

    Returns the hash of the created dataset.
    """
    folder = get_storage_folder(folder_name)

    logger.info("Collecting image items from storage folder '%s'.", folder_name)
    item_uuids = [
        item.uuid
        for item in folder.list_items(item_types=[StorageItemType.IMAGE])
    ]
    logger.info("Found %d image item(s) to link.", len(item_uuids))

    if not item_uuids:
        raise ValueError(
            f"No image items found in storage folder '{folder_name}'."
        )

    logger.info("Creating dataset '%s'.", dataset_name)
    create_response = user_client.create_dataset(
        dataset_title=dataset_name,
        dataset_type=StorageLocation.CORD_STORAGE,
        create_backing_folder=False,
    )
    dataset_hash = create_response.dataset_hash
    logger.info("Created dataset '%s' (hash: %s).", dataset_name, dataset_hash)

    dataset = user_client.get_dataset(dataset_hash)

    logger.info("Linking %d item(s) into the dataset.", len(item_uuids))
    dataset.link_items(item_uuids)
    logger.info("Linked %d item(s) into dataset '%s'.", len(item_uuids), dataset_name)

    return dataset_hash


def main() -> None:
    try:
        create_dataset_from_storage_folder()
    except Exception as e:
        logger.error("Failed to create dataset: %s", e)
        sys.exit(1)


if __name__ == "__main__":
    main()
