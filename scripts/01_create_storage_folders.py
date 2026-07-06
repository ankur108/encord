import logging
import sys

from src.config import (
    GCS_INTEGRATION_TITLE,
    GCS_REMOTE_URL,
    STORAGE_FOLDER_DESCRIPTION,
    STORAGE_FOLDER_METADATA,
    STORAGE_FOLDER_NAME,
)
from src.datasets import create_cloud_synced_folder

logging.basicConfig(
    level=logging.INFO,  # or INFO, WARNING, etc.
)
logger = logging.getLogger(__name__)

# (name_suffix, remote_url_suffix)
FOLDERS = [
    ("images", "/10k"),
    ("json", "/100k"),
]


def main() -> None:
    errors = []
    for name_suffix, url_suffix in FOLDERS:
        folder_name = f"{STORAGE_FOLDER_NAME}{name_suffix}"
        remote_url = f"{GCS_REMOTE_URL}{url_suffix}"
        try:
            create_cloud_synced_folder(
                folder_name=folder_name,
                folder_description=STORAGE_FOLDER_DESCRIPTION,
                folder_metadata=STORAGE_FOLDER_METADATA,
                integration_title=GCS_INTEGRATION_TITLE,
                remote_url=remote_url,
            )
        except Exception as e:
            logger.error("Failed to create folder %r: %s", folder_name, e)
            errors.append(folder_name)

    if errors:
        logger.error("Failed folders: %s", errors)
        sys.exit(1)


if __name__ == "__main__":
    main()
