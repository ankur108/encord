import os

# --- Auth ---
PRIVATE_KEY_PATH: str = "./encord-encord_api_keys-private-key.ed25519"


# --- Cloud Storage Folder ---
STORAGE_FOLDER_NAME: str = "enc-techint-datasets-gc"
STORAGE_FOLDER_DESCRIPTION: str = "Cloud-synced GCS folder for techint datasets"
STORAGE_FOLDER_METADATA: dict = {"env": "techint", "provider": "gcp"}

# --- GCS Integration ---
# Set ENCORD_GCS_INTEGRATION_TITLE to match the title shown in
# Encord UI > Settings > Integrations for your GCS integration.
GCS_INTEGRATION_TITLE: str = os.environ.get(
    "ENCORD_GCS_INTEGRATION_TITLE", "int-datasets"
)
GCS_REMOTE_URL: str = os.environ.get(
    "ENCORD_GCS_REMOTE_URL", "gs://enc-techint-datasets/ds-challenge-bddfde26"
)
