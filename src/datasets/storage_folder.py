from uuid import UUID
from encord.orm.storage import CloudSyncedFolderParams, StorageFolder
from encord.orm.storage import SyncPrivateDataWithCloudSyncedFolderStatus
from src.encord_client import user_client


def get_integration_uuid_by_title(title: str) -> UUID:
    """
    Get the UUID of a cloud storage integration by its title.

    Args:
        title (str): The title of the cloud storage integration.

    Returns:
        UUID: The UUID of the cloud storage integration.

    Raises:
        ValueError: If no integration with the given title is found.
    """
    integrations = user_client.get_cloud_integrations()
    for integration in integrations:
        if integration.title == title:
            return UUID(str(integration.id))
    raise ValueError(f"No integration found with title '{title}'")

def create_cloud_synced_folder(folder_name: str, folder_description: str, folder_metadata: dict, integration_title: str, remote_url: str):
    """
    Create a cloud-synced storage folder with the given name.

    Args:
        folder_name (str): The name of the storage folder.
        folder_description (str): The description of the storage folder.
        folder_metadata (dict): The metadata for the storage folder.

    Returns:
        StorageFolder: The retrieved or newly created storage folder.
    """
    # Check if the folder already exists
    existing_folders = user_client.list_storage_folders(search=folder_name)
    for folder in existing_folders:
        if folder_name == folder.name:
            print(f"Folder already exists: name='{folder_name}', uuid={folder.uuid}. Skipping creation.")
            return folder
        
    # If not found, create a new cloud-synced folder
    # Create cloud synced folder params
    cloud_synced_folder_params = CloudSyncedFolderParams(
        integration_uuid=get_integration_uuid_by_title(integration_title),
        remote_url=remote_url,
)
    storage_folder = user_client.create_storage_folder(
        name = folder_name,
        description = folder_description,
        client_metadata = folder_metadata,
        cloud_synced_folder_params = cloud_synced_folder_params,
    )
    sync_folder(storage_folder)

    return storage_folder

def sync_folder(storage_folder: StorageFolder):
    """
    Sync the given storage folder with its associated cloud storage.

    Args:
        folder (StorageFolder): The storage folder to sync.

    Returns:
        SyncPrivateDataWithCloudSyncedFolderStatus: The status of the sync operation.
    """

    # Start sync job

    sync_job_uuid = storage_folder.sync_private_data_with_cloud_synced_folder_start()
    print(f"Started sync job: {sync_job_uuid}")

    # Poll for result
    result = storage_folder.sync_private_data_with_cloud_synced_folder_get_result(
        sync_job_uuid,
        timeout_seconds=300,  # adjust as needed
    )

    print(f"Sync job finished with status: {result.status}")

    # Handle result
    if result.status == SyncPrivateDataWithCloudSyncedFolderStatus.DONE:
        print("Sync completed (server finished the job).")

        any_errors = (
            result.scan_pages_processing_error > 0
            or result.upload_jobs_error > 0
            or result.upload_jobs_units_error > 0
        )

        print("Progress summary:")
        print(
            f"  Bucket listing pages: "
            f"pending={result.scan_pages_processing_pending}, "
            f"done={result.scan_pages_processing_done}, "
            f"error={result.scan_pages_processing_error}, "
            f"cancelled={result.scan_pages_processing_cancelled}"
        )
        print(
            f"  Upload jobs: "
            f"pending={result.upload_jobs_pending}, "
            f"done={result.upload_jobs_done}, "
            f"error={result.upload_jobs_error}"
        )
        print(
            f"  File units: "
            f"pending={result.upload_jobs_units_pending}, "
            f"done={result.upload_jobs_units_done}, "
            f"error={result.upload_jobs_units_error}, "
            f"cancelled={result.upload_jobs_units_cancelled}"
        )

        if any_errors:
            print("Sync finished, but some parts failed. Inspect the *_error counters above.")
        else:
            print("Sync finished successfully with no reported errors.")

    elif result.status == SyncPrivateDataWithCloudSyncedFolderStatus.PENDING:
        print("Sync is still in progress. Try polling again later.")

    elif result.status == SyncPrivateDataWithCloudSyncedFolderStatus.ERROR:
        print("Sync failed (critical error).")

    elif result.status == SyncPrivateDataWithCloudSyncedFolderStatus.CANCELLED:
        print("Sync was cancelled.")

    else:
        print(f"Unexpected status: {result.status!r}")