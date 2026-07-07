---
name: ontology-upsert-api
description: Exact encord SDK (v0.1.195) methods/attributes for finding an ontology by title and overwriting its structure (upsert pattern)
metadata:
  type: reference
---

Verified by reading installed `encord==0.1.195` source directly (not docs) at
`/opt/homebrew/lib/python3.14/site-packages/encord/`.

## Finding ontologies by title

`EncordUserClient.get_ontologies()` (in `user_client.py`) signature:

```python
def get_ontologies(
    self,
    title_eq: Optional[str] = None,
    title_like: Optional[str] = None,   # SQL LIKE syntax
    desc_eq: Optional[str] = None,
    desc_like: Optional[str] = None,
    created_before/created_after/edited_before/edited_after: Optional[Union[str, datetime]] = None,
    include_org_access: bool = False,
) -> List[Dict]
```

Returns a `List[Dict]`, each item `{"ontology": Ontology, "user_role": OntologyUserRole | None}`.
There is no dedicated `find_ontology_by_title` — use `title_eq=ONTOLOGY_NAME` for exact match.

There's also `user_client.get_ontology(ontology_hash: str) -> Ontology` for lookup by hash (not title).

## Ontology.structure has NO public setter

In `encord/ontology.py`, the public `Ontology` class defines `structure` as a **getter-only**
property (`title` and `description` have setters, `structure` does not):

```python
@property
def structure(self) -> OntologyStructure:
    return self._ontology_instance.structure
```

So `ontology.structure = new_structure` does **not** work at the public API level (no setter
exists; would silently fail or raise depending on dataclass frozen-ness — don't attempt it).

The object returned IS the live, mutable internal `OntologyStructure` (a plain `@dataclass` in
`encord/objects/ontology_structure.py` with public mutable fields `objects: List[Object]`,
`classifications: List[Classification]`, `skeleton_templates: Dict[str, SkeletonTemplate]`).
Correct overwrite pattern is to reassign those three fields in place on the existing structure,
then call `.save()`:

```python
ontology.structure.objects = new_structure.objects
ontology.structure.classifications = new_structure.classifications
ontology.structure.skeleton_templates = new_structure.skeleton_templates
ontology.save()
```

`Ontology.save()` (in `encord/ontology.py`) PUTs `title`, `description`, and
`structure.to_dict()` to `ontologies/{ontology_hash}`. It raises `ValueError` if the structure
contains a Classification with no attributes (same validation as `create_ontology`).

## Upsert pattern

```python
existing = user_client.get_ontologies(title_eq=ONTOLOGY_NAME)
if existing:
    ontology = existing[0]["ontology"]
    ontology.structure.objects = structure.objects
    ontology.structure.classifications = structure.classifications
    ontology.structure.skeleton_templates = structure.skeleton_templates
    ontology.description = "..."  # has a public setter, optional
    ontology.save()
else:
    ontology = user_client.create_ontology(
        title=ONTOLOGY_NAME, description="...", structure=structure,
    )
```

Caveat: `title_eq` match assumes titles are unique in this org/workspace — Encord does not
enforce ontology title uniqueness server-side, so `get_ontologies(title_eq=...)` could
theoretically return >1 result if duplicates were created. Worth guarding
(`len(existing) > 1` -> log a warning / pick most recently edited via `edited_after`... or just
take `existing[0]`).

Related project code: `/Users/ankurchaudhary/encord/scripts/04_create_ontology.py` and
`/Users/ankurchaudhary/encord/src/ontology_builder.py` build up `OntologyStructure` objects
idempotently (reusing existing objects/attributes by name) before calling `create_ontology` —
this upsert pattern is the missing piece to make the whole script safe to re-run against an
already-existing ontology.
