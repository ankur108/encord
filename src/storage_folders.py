import logging
from uuid import UUID

from encord.orm.storage import (
    CloudSyncedFolderParams,
    StorageFolder,
    SyncPrivateDataWithCloudSyncedFolderStatus,
)

from src.utils.encord_client import user_client

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

_DEFAULT_SYNC_TIMEOUT_SECONDS = 300


def _get_integration_uuid_by_title(title: str) -> UUID:
    for integration in user_client.get_cloud_integrations():
        if integration.title == title:
            return UUID(str(integration.id))
    raise ValueError(f"No cloud integration found with title '{title}'")


def create_cloud_synced_folder(
    folder_name: str,
    folder_description: str,
    folder_metadata: dict,
    integration_title: str,
    remote_url: str,
) -> StorageFolder:
    """Create a cloud-synced folder, or return it if it already exists."""
    for folder in user_client.list_storage_folders(search=folder_name):
        if folder.name == folder_name:
            logger.info("Folder '%s' already exists, skipping.", folder_name)
            return folder

    params = CloudSyncedFolderParams(
        integration_uuid=_get_integration_uuid_by_title(integration_title),
        remote_url=remote_url,
    )
    folder = user_client.create_storage_folder(
        name=folder_name,
        description=folder_description,
        client_metadata=folder_metadata,
        cloud_synced_folder_params=params,
    )
    logger.info("Created folder '%s'.", folder_name)
    sync_folder(folder)
    return folder


def sync_folder(folder: StorageFolder, timeout_seconds: int = _DEFAULT_SYNC_TIMEOUT_SECONDS) -> None:
    """Trigger a sync and wait for it to complete."""
    job_uuid = folder.sync_private_data_with_cloud_synced_folder_start()
    logger.info("Sync started (job=%s).", job_uuid)

    result = folder.sync_private_data_with_cloud_synced_folder_get_result(
        job_uuid,
        timeout_seconds=timeout_seconds,
    )

    status = result.status
    if status == SyncPrivateDataWithCloudSyncedFolderStatus.DONE:
        logger.info("Sync completed successfully.")
    elif status == SyncPrivateDataWithCloudSyncedFolderStatus.PENDING:
        logger.warning("Sync timed out after %ds — still running.", timeout_seconds)
    elif status == SyncPrivateDataWithCloudSyncedFolderStatus.ERROR:
        raise RuntimeError(f"Sync job {job_uuid} failed.")
    elif status == SyncPrivateDataWithCloudSyncedFolderStatus.CANCELLED:
        raise RuntimeError(f"Sync job {job_uuid} was cancelled.")
    else:
        raise RuntimeError(f"Unexpected sync status: {status!r}")
