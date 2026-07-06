import json
import logging
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from encord.objects import OntologyStructure, Shape

from src.config import ONTOLOGY_NAME
from utils.encord_client import user_client
from ontology_builder import create_ontology_with_objects_and_attributes

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

REPORTS_DIR = Path(__file__).resolve().parents[1] / "reports"
ONTOLOGY_OBJECTS_FILE = REPORTS_DIR / "ontology_objects.json"

# Maps BDD100K shape keys to Encord Shape enum values
SHAPE_MAP: dict[str, Shape] = {
    "box2d": Shape.BOUNDING_BOX,
    "poly2d": Shape.POLYGON,
    "point": Shape.POINT,
    "polyline": Shape.POLYLINE,
}


def load_ontology_objects(path: Path) -> list[dict]:
    if not path.exists():
        sys.exit(f"Error: ontology objects file not found: {path}")
    with open(path) as fh:
        return json.load(fh)


def build_structure(objects: list[dict]) -> OntologyStructure:
    structure = OntologyStructure()
    skipped = []

    for entry in objects:
        category: str = entry["category"]
        shapes: list[str] = entry.get("shapes", [])
        attr_names: list[str] = entry.get("attributes", [])

        if not shapes:
            logger.warning("Skipping '%s': no shapes defined", category)
            skipped.append(category)
            continue

        # Use the first shape; warn if the entry has multiple
        raw_shape = shapes[0]
        if len(shapes) > 1:
            logger.warning(
                "'%s' has multiple shapes %s — using first: '%s'",
                category,
                shapes,
                raw_shape,
            )

        encord_shape = SHAPE_MAP.get(raw_shape)
        if encord_shape is None:
            logger.warning(
                "Skipping '%s': unrecognised shape '%s'", category, raw_shape
            )
            skipped.append(category)
            continue

        # Convert list of attribute names to the dict format the builder expects.
        # Values are unknown at this stage, so each maps to an empty list which
        # causes the builder to create a TextAttribute placeholder.
        attributes: dict[str, list[str]] = {name: [] for name in attr_names}

        create_ontology_with_objects_and_attributes(
            ontology_structure=structure,
            object_name=category,
            shape=encord_shape,
            attributes=attributes if attributes else None,
        )
        logger.info("Added object '%s' (%s)", category, raw_shape)

    if skipped:
        logger.warning("Skipped %d categories: %s", len(skipped), skipped)

    return structure


def main() -> None:
    objects = load_ontology_objects(ONTOLOGY_OBJECTS_FILE)
    logger.info("Loaded %d categories from %s", len(objects), ONTOLOGY_OBJECTS_FILE)

    structure = build_structure(objects)
    logger.info(
        "Built ontology structure with %d objects", len(structure.objects)
    )

    ontology = user_client.create_ontology(
        title=ONTOLOGY_NAME,
        description="Auto-generated from BDD100K sample annotations",
        structure=structure,
    )
    logger.info(
        "Created ontology '%s' (hash: %s)", ONTOLOGY_NAME, ontology.ontology_hash
    )


if __name__ == "__main__":
    main()
