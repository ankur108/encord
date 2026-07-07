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


def find_dataset(dataset_name: str) -> str | None:
    """Return the hash of an existing dataset with this exact title, or None."""
    results = user_client.get_datasets(title_eq=dataset_name)
    if not results:
        return None
    dataset_hash = results[0]["dataset"].dataset_hash
    logger.info("Found existing dataset '%s' (hash: %s).", dataset_name, dataset_hash)
    return dataset_hash


def get_or_create_dataset(dataset_name: str) -> str:
    """Return the hash of the dataset named ``dataset_name``.

    If a dataset with that exact title already exists it is reused; otherwise a
    new empty CORD-storage dataset is created.
    """
    existing = find_dataset(dataset_name)
    if existing is not None:
        return existing

    logger.info("Creating dataset '%s'.", dataset_name)
    create_response = user_client.create_dataset(
        dataset_title=dataset_name,
        dataset_type=StorageLocation.CORD_STORAGE,
        create_backing_folder=False,
    )
    dataset_hash = create_response.dataset_hash
    logger.info("Created dataset '%s' (hash: %s).", dataset_name, dataset_hash)
    return dataset_hash


def sync_items_to_dataset(dataset_hash: str, item_uuids: Sequence[UUID]) -> None:
    """Make the dataset's linked items match ``item_uuids`` exactly.

    New items (not yet linked) are linked in; data rows whose backing storage
    item is no longer in ``item_uuids`` are removed. Items already linked and
    still wanted are left untouched.
    """
    dataset = user_client.get_dataset(dataset_hash)

    desired = set(item_uuids)

    # Map currently-linked storage item UUID -> data_hash (DataRow.uid), so we
    # can both detect what's already linked and remove what's no longer wanted.
    linked_rows = {
        row.backing_item_uuid: row.uid
        for row in dataset.list_data_rows()
        if row.backing_item_uuid is not None
    }
    already_linked = set(linked_rows)

    new_items = [uuid for uuid in desired if uuid not in already_linked]
    stale_hashes = [
        data_hash
        for item_uuid, data_hash in linked_rows.items()
        if item_uuid not in desired
    ]

    if stale_hashes:
        logger.info(
            "Removing %d stale data row(s) from dataset '%s'.",
            len(stale_hashes),
            dataset_hash,
        )
        dataset.delete_data(stale_hashes)

    if new_items:
        logger.info("Linking %d new item(s) into the dataset.", len(new_items))
        dataset.link_items(new_items)
        logger.info(
            "Linked %d item(s) into dataset '%s'.", len(new_items), dataset_hash
        )

    if not new_items and not stale_hashes:
        logger.info("Dataset '%s' already up to date; nothing to change.", dataset_hash)
