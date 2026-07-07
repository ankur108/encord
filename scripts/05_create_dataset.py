import logging
import sys

from encord.storage import StorageItemType

from src.config import (
    DATASET_NAME,
    STORAGE_FOLDER_NAME,
)
from src.dataset_builder import (
    get_or_create_dataset,
    get_storage_folder,
    sync_items_to_dataset,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def sync_dataset_from_storage_folder(
    dataset_name: str = DATASET_NAME,
    folder_name: str = STORAGE_FOLDER_NAME,
) -> str:
    """Ensure a dataset exists and its linked items match the storage folder.

    Creates the dataset only if one with this name is missing; otherwise reuses
    it and syncs the links (adding new image items with metadata and removing
    ones that are no longer present).

    Returns the hash of the dataset.
    """
    folder = get_storage_folder(folder_name)

    logger.info("Collecting image items with metadata from storage folder '%s'.", folder_name)
    item_uuids = []
    skipped = 0
    for item in folder.list_items(item_types=[StorageItemType.IMAGE]):
        # client_metadata is None when never set, {} when set but empty.
        if not item.client_metadata:
            logger.debug("Skipping '%s': no metadata attached.", item.name)
            skipped += 1
            continue
        item_uuids.append(item.uuid)

    logger.info("Found %d image(s) with metadata (%d skipped).", len(item_uuids), skipped)

    if not item_uuids:
        raise ValueError(
            f"No image items with metadata found in storage folder '{folder_name}'."
        )

    dataset_hash = get_or_create_dataset(dataset_name)
    sync_items_to_dataset(dataset_hash, item_uuids)

    return dataset_hash


def main() -> None:
    try:
        sync_dataset_from_storage_folder()
    except Exception as e:
        logger.error("Failed to sync dataset: %s", e)
        sys.exit(1)


if __name__ == "__main__":
    main()
