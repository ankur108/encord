import logging
import sys

from src.config import (
    DATASET_NAME,
    ONTOLOGY_NAME,
    PROJECT_DESCRIPTION,
    PROJECT_NAME,
)
from src.project_builder import create_project

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main() -> None:
    try:
        create_project(
            project_name=PROJECT_NAME,
            project_description=PROJECT_DESCRIPTION,
            dataset_name=DATASET_NAME,
            ontology_name=ONTOLOGY_NAME,
        )
    except Exception as e:
        logger.error("Failed to create project: %s", e)
        sys.exit(1)


if __name__ == "__main__":
    main()
