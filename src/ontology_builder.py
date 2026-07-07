import logging
from encord.objects import Shape, OntologyStructure
from encord.objects.attributes import RadioAttribute, ChecklistAttribute, TextAttribute

logger = logging.getLogger(__name__)

# Attributes whose observed values are purely boolean get a ChecklistAttribute
# (checking the option = True); everything else gets a RadioAttribute.
_BOOL_VALUES = {"True", "False"}


def _get_attribute(obj, attr_name: str):
    """Return an existing attribute on obj by name, or None."""
    return next((a for a in obj.attributes if a.name == attr_name), None)


def _add_option_if_missing(attr, label: str) -> None:
    """Add an option to attr only if no option with that label exists."""
    if any(o.label == label for o in attr.options):
        logger.debug("Option '%s' already exists on '%s'; skipping.", label, attr.name)
        return
    attr.add_option(label=label)


def _add_attributes(obj, attributes: dict[str, list[str]]) -> None:
    for attr_name, values in attributes.items():
        value_set = set(values)
        existing = _get_attribute(obj, attr_name)

        if not values:
            # No known values — create a free-text attribute as a placeholder
            if existing is None:
                obj.add_attribute(TextAttribute, attr_name)
            else:
                logger.debug("Attribute '%s' already exists on '%s'; skipping.", attr_name, obj.name)
            continue

        if value_set <= _BOOL_VALUES:
            # Boolean property → single-option checklist (checked = True)
            attr = existing or obj.add_attribute(ChecklistAttribute, attr_name)
            _add_option_if_missing(attr, "True")
        else:
            attr = existing or obj.add_attribute(RadioAttribute, attr_name)
            for value in sorted(values):
                _add_option_if_missing(attr, value)

        if existing is not None:
            logger.debug("Attribute '%s' already exists on '%s'; topped up options only.", attr_name, obj.name)


def create_ontology_with_objects_and_attributes(
    ontology_structure: OntologyStructure,
    object_name: str,
    shape: Shape,
    attributes: dict[str, list[str]] | None = None,
) -> OntologyStructure:
    """
    Add one object class (with its attributes) to an OntologyStructure.

    Idempotent: if an object with the same name and shape already exists it is
    reused rather than duplicated, and existing attributes/options are left in
    place — only missing ones are added.

    Args:
        ontology_structure: The structure to mutate in place.
        object_name:        Display name for the object class.
        shape:              Encord Shape enum value.
        attributes:         Mapping of attribute name → list of observed values
                            (as produced by extract_ontology_objects).

    Returns:
        The same ontology_structure (mutated in place).
    """
    obj = next(
        (o for o in ontology_structure.objects
         if o.name == object_name and o.shape == shape),
        None,
    )
    if obj is None:
        obj = ontology_structure.add_object(name=object_name, shape=shape)
        logger.debug("Added object '%s' with shape %s", object_name, shape)
    else:
        logger.debug(
            "Object '%s' with shape %s already exists; reusing it.", object_name, shape
        )

    if attributes:
        _add_attributes(obj, attributes)

    return ontology_structure
