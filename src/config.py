import os

# --- Auth (used by src/utils/encord_client.py) ---
PRIVATE_KEY_PATH: str = os.environ.get(
    "ENCORD_PRIVATE_KEY_PATH", "./encord-encord_api_keys-private-key.ed25519"
)

# --- Step 01: Create cloud-synced storage folder ---
# GCS integration — set ENCORD_GCS_INTEGRATION_TITLE to match the title shown
# in Encord UI > Settings > Integrations for your GCS integration.
GCS_INTEGRATION_TITLE: str = os.environ.get(
    "ENCORD_GCS_INTEGRATION_TITLE", "int-datasets"
)
GCS_REMOTE_URL: str = os.environ.get(
    "ENCORD_GCS_REMOTE_URL", "gs://enc-techint-datasets/ds-challenge-bddfde26"
)
STORAGE_FOLDER_NAME: str = "enc-techint-datasets-gc"
STORAGE_FOLDER_DESCRIPTION: str = "Cloud-synced GCS folder for techint datasets"
STORAGE_FOLDER_METADATA: dict = {"env": "techint", "provider": "gcp"}

# --- Step 03: Export ontology objects ---
ONTOLOGY_EXPORT_SOURCE: str = "gcs"  # "local" or "gcs"
ONTOLOGY_EXPORT_PATH: str = "gs://enc-techint-datasets/ds-challenge-bddfde26/100k/test/"  # ./sample or gs path
OUTPUT_FILE = "reports/ontology_objects.json"
BLOB_LIMIT = 500  # Max number of blobs to download from GCS

# --- Step 04: Create ontology ---
ONTOLOGY_NAME: str = "Techint Ontology"

# --- Step 05: Create dataset ---
DATASET_NAME: str = "Techint Dataset"

# --- Step 06: Create project ---
PROJECT_NAME: str = "Techint Project"
PROJECT_DESCRIPTION: str = "Autonomous Vehicle Data Annotation"
