from src.datasets import create_cloud_synced_folder
from src.config import (
    GCS_INTEGRATION_TITLE,
    GCS_REMOTE_URL,
    STORAGE_FOLDER_DESCRIPTION,
    STORAGE_FOLDER_METADATA,
    STORAGE_FOLDER_NAME,
)


def main() -> None:
   image_folder_name = STORAGE_FOLDER_NAME + 'images'
   bucket_path_image = GCS_REMOTE_URL + '/10k'
   create_cloud_synced_folder(image_folder_name, STORAGE_FOLDER_DESCRIPTION, STORAGE_FOLDER_METADATA, GCS_INTEGRATION_TITLE, bucket_path_image)
   

   json_folder_name = STORAGE_FOLDER_NAME + 'json'
   bucket_path_json = GCS_REMOTE_URL + '/100k'
   create_cloud_synced_folder(json_folder_name, STORAGE_FOLDER_DESCRIPTION, STORAGE_FOLDER_METADATA, GCS_INTEGRATION_TITLE, bucket_path_json)


if __name__ == "__main__":
    main()
