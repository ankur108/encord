import logging
import sys

from src.config import (
    DATASET_NAME,
    ONTOLOGY_NAME,
    PROJECT_DESCRIPTION,
    PROJECT_NAME,
)
from src.utils.encord_client import user_client

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_dataset_hash(dataset_name: str) -> str:
    """Look up an existing dataset by title and return its hash."""
    results = user_client.get_datasets(title_eq=dataset_name)
    if not results:
        raise ValueError(f"Dataset '{dataset_name}' not found.")
    return results[0]["dataset"].dataset_hash


def get_ontology_hash(ontology_name: str) -> str:
    """Look up an existing ontology by title and return its hash."""
    results = user_client.get_ontologies(title_eq=ontology_name)
    if not results:
        raise ValueError(f"Ontology '{ontology_name}' not found.")
    return results[0]["ontology"].ontology_hash


def create_project(
    project_name: str = PROJECT_NAME,
    project_description: str = PROJECT_DESCRIPTION,
    dataset_name: str = DATASET_NAME,
    ontology_name: str = ONTOLOGY_NAME,
) -> str:
    """Create a project attached to the dataset and ontology built earlier.

    Returns the hash of the created project.
    """
    dataset_hash = get_dataset_hash(dataset_name)
    logger.info("Found dataset '%s' (hash: %s).", dataset_name, dataset_hash)

    ontology_hash = get_ontology_hash(ontology_name)
    logger.info("Found ontology '%s' (hash: %s).", ontology_name, ontology_hash)

    logger.info("Creating project '%s'.", project_name)
    project_hash = user_client.create_project(
        project_title=project_name,
        dataset_hashes=[dataset_hash],
        project_description=project_description,
        ontology_hash=ontology_hash,
    )
    logger.info("Created project '%s' (hash: %s).", project_name, project_hash)

    return project_hash


def main() -> None:
    try:
        create_project()
    except Exception as e:
        logger.error("Failed to create project: %s", e)
        sys.exit(1)


if __name__ == "__main__":
    main()
