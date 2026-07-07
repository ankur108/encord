import logging

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


def get_existing_project_hash(project_name: str) -> str | None:
    """Look up an existing project by title and return its hash, if any."""
    results = user_client.get_projects(title_eq=project_name)
    if not results:
        return None
    return results[0]["project"].project_hash


def create_project(
    project_name: str,
    project_description: str,
    dataset_name: str,
    ontology_name: str,
) -> str:
    """Create a project attached to an existing dataset and ontology.

    Looks up the dataset and ontology by name, then creates a project that
    links them together. If a project with the same name already exists, it is
    reused instead of creating a duplicate. Returns the project hash.
    """
    existing_project_hash = get_existing_project_hash(project_name)
    if existing_project_hash is not None:
        logger.info(
            "Project '%s' already exists (hash: %s); skipping creation.",
            project_name,
            existing_project_hash,
        )
        return existing_project_hash

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
