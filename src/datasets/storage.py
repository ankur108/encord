from uuid import UUID

from encord.orm.storage import CloudSyncedFolderParams
from encord.storage import StorageFolder

from src.config import (
    GCS_INTEGRATION_TITLE,
    GCS_REMOTE_URL,
    STORAGE_FOLDER_DESCRIPTION,
    STORAGE_FOLDER_METADATA,
    STORAGE_FOLDER_NAME,
)
from src.encord_client import user_client


def _get_gcs_integration_uuid() -> UUID:
    integrations = user_client.get_cloud_integrations()
    match = next(
        (i for i in integrations if GCS_INTEGRATION_TITLE.lower() in i.title.lower()),
        None,
    )
    if match is None:
        available = [i.title for i in integrations]
        raise ValueError(
            f"No integration matching '{GCS_INTEGRATION_TITLE}' found. "
            f"Available integrations: {available}"
        )
    return UUID(str(match.id))


def _find_existing_folder() -> StorageFolder | None:
    matches = user_client.list_storage_folders(search=STORAGE_FOLDER_NAME)
    return next(
        (f for f in matches if f.name == STORAGE_FOLDER_NAME),
        None,
    )


def create_cloud_synced_folder() -> tuple[StorageFolder, bool]:
    """Return (folder, created) where created=False if the folder already existed."""
    existing = _find_existing_folder()
    if existing is not None:
        return existing, False

    integration_uuid = _get_gcs_integration_uuid()
    cloud_params = CloudSyncedFolderParams(
        integration_uuid=integration_uuid,
        remote_url=GCS_REMOTE_URL,
    )
    folder = user_client.create_storage_folder(
        name=STORAGE_FOLDER_NAME,
        description=STORAGE_FOLDER_DESCRIPTION,
        client_metadata=STORAGE_FOLDER_METADATA,
        cloud_synced_folder_params=cloud_params,
    )
    return folder, True


def sync_folder(folder: StorageFolder, timeout_seconds: int = 300) -> None:
    job_uuid = folder.sync_private_data_with_cloud_synced_folder_start()
    result = folder.sync_private_data_with_cloud_synced_folder_get_result(
        sync_job_uuid=job_uuid,
        timeout_seconds=timeout_seconds,
    )
    print(f"Sync complete: {result}")
