import logging
import sys

from src.config import (
    GCS_INTEGRATION_TITLE,
    GCS_REMOTE_URL,
    STORAGE_FOLDER_DESCRIPTION,
    STORAGE_FOLDER_METADATA,
    STORAGE_FOLDER_NAME,
)
from storage_folder_builder import create_cloud_synced_folder

logging.basicConfig(
    level=logging.INFO,  # or INFO, WARNING, etc.
)
logger = logging.getLogger(__name__)

def main() -> None:
    errors = []
    try:
        create_cloud_synced_folder(
            folder_name=STORAGE_FOLDER_NAME,
            folder_description=STORAGE_FOLDER_DESCRIPTION,
            folder_metadata=STORAGE_FOLDER_METADATA,
            integration_title=GCS_INTEGRATION_TITLE,
            remote_url=GCS_REMOTE_URL + '/10k',
        )
    except Exception as e:
        logger.error("Failed to create folder %r: %s", STORAGE_FOLDER_NAME, e)
        errors.append(STORAGE_FOLDER_NAME)

    if errors:
        logger.error("Failed folders: %s", errors)
        sys.exit(1)


if __name__ == "__main__":
    main()
