---
name: dataset-data-row-api
description: Exact signatures for EncordUserClient.get_datasets, Dataset.data_rows/list_data_rows, link_items, delete_data (verified against encord==0.1.195 source)
metadata:
  type: reference
---

Verified by reading `/opt/homebrew/lib/python3.14/site-packages/encord/{user_client,dataset}.py` and `encord/orm/dataset.py` for encord==0.1.195. Re-verify if the installed version differs materially — these are internal implementation facts, not just doc claims.

## Listing datasets

`user_client.get_datasets(title_eq=None, title_like=None, desc_eq=None, desc_like=None, created_before=None, created_after=None, edited_before=None, edited_after=None, include_org_access=False) -> List[Dict[str, Any]]`

Each item is `{"dataset": DatasetInfo(...), "user_role": DatasetUserRole | None}`. `DatasetInfo` (in `encord.orm.dataset`) has fields `dataset_hash: str`, `title: str`, `description`, `type`, `created_at`, `last_edited_at`, `backing_folder_uuid`. So to find by title: `next(d["dataset"] for d in user_client.get_datasets(title_eq="my dataset") if ...)` — filter with `title_eq`/`title_like` server-side rather than fetching all and scanning client-side.

## DataRow identifiers — no `.uuid` property exists

`DataRow` (in `encord.orm.dataset`, dict-subclass) exposes:
- `.uid` → returns the `data_hash` string (this is the "data_hash"/legacy row id). There is **no `.uuid` property** on DataRow — don't assume one.
- `.backing_item_uuid` → `UUID` of the underlying `encord.storage.StorageItem` that this data row is linked to. Raises `NotImplementedError` if not present (older/unsupported storage API path).
- `.title`, `.data_type`, `.created_at`, etc.

Get rows via `dataset.data_rows` (property, all rows, respects `dataset_access_settings`) or `dataset.list_data_rows(title_eq=, title_like=, created_before=, created_after=, data_types=, data_hashes=)` for filtered queries — both return `List[DataRow]`.

## Linking new items

`dataset.link_items(item_uuids: List[UUID], duplicates_behavior: DataLinkDuplicatesBehavior = DataLinkDuplicatesBehavior.SKIP) -> List[DataRow]`

`item_uuids` are **storage item UUIDs** (`encord.storage.StorageItem.uuid`), not data_hashes. `DataLinkDuplicatesBehavior` is an enum in `encord.orm.dataset`.

## Removing/unlinking data rows — method is `delete_data`, not `unlink_items`

`dataset.delete_data(data_hashes: Union[List[str], str]) -> None`

Takes **strings** (the `data_hash`/`DataRow.uid` values), not UUID objects, and not a list of DataRow objects. Internally calls `querier.basic_delete(Video, uid=data_hashes)` — this deletes the Video/data-unit record tied to the dataset, it is not a lighter-weight "unlink but keep in storage" operation. There is no separate `unlink_items`/`remove_data_rows` method in this SDK version — `delete_data` is the one and only removal API on `Dataset`.

Related: [[ontology_upsert_api]]
