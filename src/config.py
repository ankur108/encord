import os

# --- Auth ---
PRIVATE_KEY_PATH: str = "./encord-encord_api_keys-private-key.ed25519"


# --- Cloud Storage Folder ---
STORAGE_FOLDER_NAME: str = "enc-techint-datasets-gc"
STORAGE_FOLDER_DESCRIPTION: str = "Cloud-synced GCS folder for techint datasets"
STORAGE_FOLDER_METADATA: dict = {"env": "techint", "provider": "gcp"}

ONTOLOGY_NAME: str = "Techint Ontology"

# --- Dataset ---
DATASET_NAME: str = "Techint Dataset"
DATASET_DESCRIPTION: str = (
    "BDD100K images linked from the cloud-synced storage folder"
)

# --- Project ---
PROJECT_NAME: str = "Techint Project"
PROJECT_DESCRIPTION: str = (
    "BDD100K annotation project using the Techint dataset and ontology"
)

# --- Ontology Export ---
ONTOLOGY_EXPORT_SOURCE: str = "gcs"  # "local" or "gcs"
ONTOLOGY_EXPORT_PATH: str = "gs://enc-techint-datasets/ds-challenge-bddfde26/100k/test/" # ./sample or gs path

# --- GCS Integration ---
# Set ENCORD_GCS_INTEGRATION_TITLE to match the title shown in
# Encord UI > Settings > Integrations for your GCS integration.
GCS_INTEGRATION_TITLE: str = os.environ.get(
    "ENCORD_GCS_INTEGRATION_TITLE", "int-datasets"
)
GCS_REMOTE_URL: str = os.environ.get(
    "ENCORD_GCS_REMOTE_URL", "gs://enc-techint-datasets/ds-challenge-bddfde26"
)
