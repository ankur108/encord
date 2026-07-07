import logging
from typing import Sequence
from uuid import UUID

from encord.orm.dataset import StorageLocation

from src.utils.encord_client import user_client

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_storage_folder(folder_name: str):
    """Look up an existing storage folder by name."""
    folder = next(
        (f for f in user_client.list_storage_folders(search=folder_name)
         if f.name == folder_name),
        None,
    )
    if folder is None:
        raise ValueError(f"Storage folder '{folder_name}' not found.")
    return folder


def create_dataset(dataset_name: str) -> str:
    """Create an empty CORD-storage dataset and return its hash."""
    logger.info("Creating dataset '%s'.", dataset_name)
    create_response = user_client.create_dataset(
        dataset_title=dataset_name,
        dataset_type=StorageLocation.CORD_STORAGE,
        create_backing_folder=False,
    )
    dataset_hash = create_response.dataset_hash
    logger.info("Created dataset '%s' (hash: %s).", dataset_name, dataset_hash)
    return dataset_hash


def link_items_to_dataset(dataset_hash: str, item_uuids: Sequence[UUID]) -> None:
    """Link the given storage items into an existing dataset.

    Items already present in the dataset are skipped so they are not linked
    twice; only new items are linked.
    """
    dataset = user_client.get_dataset(dataset_hash)

    already_linked = {
        row.backing_item_uuid
        for row in dataset.list_data_rows()
        if row.backing_item_uuid is not None
    }

    new_items = [uuid for uuid in item_uuids if uuid not in already_linked]
    skipped = len(item_uuids) - len(new_items)
    if skipped:
        logger.info(
            "Skipping %d item(s) already linked to dataset '%s'.",
            skipped,
            dataset_hash,
        )

    if not new_items:
        logger.info("No new items to link into dataset '%s'.", dataset_hash)
        return

    logger.info("Linking %d new item(s) into the dataset.", len(new_items))
    dataset.link_items(new_items)
    logger.info("Linked %d item(s) into dataset '%s'.", len(new_items), dataset_hash)
