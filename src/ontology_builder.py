import logging
from encord.objects import Shape, OntologyStructure
from encord.objects.attributes import RadioAttribute, ChecklistAttribute, TextAttribute

logger = logging.getLogger(__name__)

# Attributes whose observed values are purely boolean get a ChecklistAttribute
# (checking the option = True); everything else gets a RadioAttribute.
_BOOL_VALUES = {"True", "False"}


def _add_attributes(obj, attributes: dict[str, list[str]]) -> None:
    for attr_name, values in attributes.items():
        if not values:
            # No known values — create a free-text attribute as a placeholder
            obj.add_attribute(TextAttribute, attr_name)
            continue
        value_set = set(values)
        if value_set <= _BOOL_VALUES:
            # Boolean property → single-option checklist (checked = True)
            checklist = obj.add_attribute(ChecklistAttribute, attr_name)
            checklist.add_option(label="True")
        else:
            radio = obj.add_attribute(RadioAttribute, attr_name)
            for value in sorted(values):
                radio.add_option(label=value)


def create_ontology_with_objects_and_attributes(
    ontology_structure: OntologyStructure,
    object_name: str,
    shape: Shape,
    attributes: dict[str, list[str]] | None = None,
) -> OntologyStructure:
    """
    Add one object class (with its attributes) to an OntologyStructure.

    Args:
        ontology_structure: The structure to mutate in place.
        object_name:        Display name for the object class.
        shape:              Encord Shape enum value.
        attributes:         Mapping of attribute name → list of observed values
                            (as produced by extract_ontology_objects).

    Returns:
        The same ontology_structure (mutated in place).
    """
    obj = ontology_structure.add_object(name=object_name, shape=shape)
    logger.debug("Added object '%s' with shape %s", object_name, shape)

    if attributes:
        _add_attributes(obj, attributes)

    return ontology_structure
