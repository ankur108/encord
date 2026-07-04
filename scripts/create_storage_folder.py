"""
Run from repo root:
    python -m scripts.create_storage_folder
"""
from src.datasets import create_cloud_synced_folder, sync_folder


def main() -> None:
    folder, created = create_cloud_synced_folder()
    if created:
        print(f"Folder created: name='{folder.name}', uuid={folder.uuid}")
        print("Starting sync with GCS bucket...")
        sync_folder(folder)
        print("Cloud synced folder created")
    else:
        print(f"Folder already exists: name='{folder.name}', uuid={folder.uuid}. Skipping creation.")


if __name__ == "__main__":
    main()
