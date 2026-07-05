"""Fetch storage items from Encord and download JSON content in parallel."""

import sys
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Optional

import requests
from encord.orm.storage import StorageItemType
from encord.storage import StorageFolder, StorageItem

_thread_local = threading.local()


def _session() -> requests.Session:
    if not hasattr(_thread_local, "s"):
        _thread_local.s = requests.Session()
    return _thread_local.s


def fetch_storage_items(
    folder: StorageFolder,
    page_size: int = 1000,
    verbose: bool = True,
) -> tuple[list[StorageItem], list[StorageItem]]:
    """Return (image_items, json_items) from the folder."""
    if verbose:
        print("Fetching image items...", file=sys.stderr, flush=True)
    images = list(folder.list_items(item_types=[StorageItemType.IMAGE], page_size=page_size))
    if verbose:
        print(f"  {len(images):,} images", file=sys.stderr, flush=True)
        print("Fetching JSON items (with signed URLs)...", file=sys.stderr, flush=True)
    jsons = list(
        folder.list_items(
            item_types=[StorageItemType.PLAIN_TEXT],
            get_signed_urls=True,
            page_size=page_size,
        )
    )
    if verbose:
        print(f"  {len(jsons):,} JSON files", file=sys.stderr, flush=True)
    return images, jsons


def _download_one(item: StorageItem) -> tuple[str, Optional[dict]]:
    url = item.get_signed_url()
    if not url:
        return item.name, None
    try:
        resp = _session().get(url, timeout=30)
        resp.raise_for_status()
        return item.name, resp.json()
    except Exception:
        return item.name, None


def download_json_contents(
    json_items: list[StorageItem],
    concurrency: int = 50,
    sample: Optional[int] = None,
    verbose: bool = True,
) -> list[tuple[str, dict]]:
    """Download and parse JSON content. Returns (item_name, parsed_data) pairs."""
    if sample is not None and sample < len(json_items):
        import random
        items_to_fetch = random.sample(json_items, sample)
        if verbose:
            print(
                f"Sampling {sample:,}/{len(json_items):,} JSON files "
                f"(concurrency={concurrency})...",
                file=sys.stderr, flush=True,
            )
    else:
        items_to_fetch = json_items
        if verbose:
            print(
                f"Downloading {len(items_to_fetch):,} JSON files "
                f"(concurrency={concurrency}) — this may take a few minutes...",
                file=sys.stderr, flush=True,
            )

    results: list[tuple[str, dict]] = []
    errors = 0

    with ThreadPoolExecutor(max_workers=concurrency) as pool:
        futures = {pool.submit(_download_one, item): item for item in items_to_fetch}
        done = 0
        for future in as_completed(futures):
            name, data = future.result()
            done += 1
            if data is not None:
                results.append((name, data))
            else:
                errors += 1
            if verbose and done % 5000 == 0:
                print(f"  {done:,}/{len(items_to_fetch):,} downloaded...", file=sys.stderr, flush=True)

    if verbose:
        print(
            f"  Done: {len(results):,} parsed, {errors:,} errors.",
            file=sys.stderr, flush=True,
        )
    return results
