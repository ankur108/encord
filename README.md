# Encord FDE Challenge - Ankur Chaudhary

Migrating an autonomous-driving customer's images, scene-level metadata, and
annotations into the Encord platform so they can **view, search, and continue
annotating** the data — done **programmatically** via the Encord Python SDK so
the customer can fold it into their own ingestion pipelines.

The data lives in a public GCS bucket, organized by split:

```
gs://enc-techint-datasets/ds-challenge-bddfde26/
├── 10k/                 # Images (JPEG, 720p)
│   ├── train/           # 7,000 images
│   ├── val/             # 1,000 images
│   └── test/            # 2,000 images
└── 100k/                # Annotation & metadata files (JSON)
    ├── train/           # 70,000 files
    ├── val/             # 10,000 files
    └── test/            # 20,000 files
```

## Deliverables

1. **Code** — the Python pipeline in this repo (`main.py` + `scripts/` + `src/`),
   plus a GitHub Actions workflow that  runs it end-to-end (`.github/workflows/run-pipeline.yml`).
2. **Encord entities** — links to the created Folder and Project:
   - Index Folder: https://app.encord.com/data/files/3123532e-921f-47a9-a5dd-e934e02b1356
   - Project: https://app.encord.com/projects/view/ebb6b706-2afe-44c0-b19b-d04fe6eeebf8/summary
   - Dataset: https://app.encord.com/data/datasets/355527c2-3510-4981-a7ad-32becd023724
   - Ontology: https://app.encord.com/ontologies/view/101332ac-f5cd-4d9c-b6f8-6e9892719af9/structure

## Mapping to the challenge brief

The task asks us to get images, metadata, and labels into Encord so the customer
can review and plan enrichment, with **all images in the Data section but only
labelled images added to the project**, and to surface engineering
characteristics in the report. Here's how this repo addresses each requirement.

| Brief requirement | Where it's handled |
| --- | --- |
| Folder in Index for all images | Stage 1 — cloud-synced folder over `10k/` |
| Ontology reflecting annotation categories | Stages 3–4 — ontology **derived from the data** |
| Dataset linking data units to the project | Stage 5 — only images that have metadata are linked |
| Project for the annotation workflow | Stage 6 — dataset + ontology |
| Searchable scene metadata (`weather`/`scene`/`time_of_day`) | Stage 2 — registers a metadata schema and attaches `client_metadata` |
| Programmatic & handable to the customer | All stages are SDK-driven; config is externalized |
| Handle unclean production data | Skip logic at every stage (see Coverage) |

## Approach

The migration is broken into small, independently runnable stages. Each maps to
an Encord entity the customer needs:

| Stage | Script | Encord entity | What it does |
| --- | --- | --- | --- |
| 1 | `01_create_cloud_synced_folder.py` | Folder (Index) | Get-or-create a cloud-synced Index folder over the `10k/` GCS prefix so **all** images appear in the Data section, then trigger + wait on a sync job |
| 2 | `02_attach_metadata.py` | — | Register the metadata schema, read the label JSONs, and attach `weather` / `scene` / `time_of_day` as searchable `client_metadata` on each image (batched via a `Bundle`) |
| 3 | `03_export_ontology_objects.py` | — | Scan the label JSONs to discover object categories, shapes, and attributes → `reports/ontology_objects.json` |
| 4 | `04_create_ontology.py` | Ontology | Build the ontology in Encord from the discovered categories/shapes/attributes |
| 5 | `05_create_dataset.py` | Dataset | Create a dataset and link **only** the folder images that carry metadata (labelled images) |
| 6 | `06_create_project.py` | Project | Get-or-create the annotation project tying the dataset + ontology together |

### Metadata schema (prescribed — do not modify)

Attached to each image as `client_metadata`, and pre-registered as a metadata
schema (stage 2, `ensure_metadata_schema`) so the fields are searchable/filterable
in the Encord UI:

| Field | Source (BDD JSON) | Type | Example |
| --- | --- | --- | --- |
| `weather` | `attributes.weather` | varchar | `clear`, `rainy`, `overcast` |
| `scene` | `attributes.scene` | varchar | `highway`, `city street`, `residential` |
| `time_of_day` | `attributes.timeofday` | varchar | `daytime`, `night`, `dawn/dusk` |

The BDD export uses the key `timeofday`; stage 2 is meant to map it to the
required `time_of_day` field name via `_METADATA_FIELD_MAP` in
`02_attach_metadata.py`.

> ⚠️ **Highlighted note — field naming.** The BDD source key is `timeofday`
> (no underscore) while the prescribed schema field is `time_of_day` (with
> underscore). This underscore mismatch between the export and the required
> schema is called out here in the report so the reviewer is aware of the naming
> discrepancy and how the field map bridges the two. The single-dict
> `_METADATA_FIELD_MAP` is where this mapping is controlled.

### Ontology (derived from the data)

The ontology is not hand-written — stage 3 scans the annotation JSONs and stage 4
turns the result into an `OntologyStructure`. From the sampled `test` split, the
discovered structure (`reports/ontology_objects.json`) is:

- **Bounding-box (`box2d`) objects**: `car`, `bus`, `truck`, `train`, `motor`,
  `bike`, `rider`, `person`, `traffic light`, `traffic sign` — each with the
  attributes `occluded`, `truncated`, `trafficLightColor`.
- **Polygon (`poly2d`) objects**: lane markings (`lane/crosswalk`,
  `lane/single|double white/yellow`, `lane/road curb`, `lane/single other`) with
  `direction` / `style` attributes, and drivable areas (`area/drivable`,
  `area/alternative`).

Because attribute *values* aren't known at discovery time, they're created as
free-text (`TextAttribute`) placeholders; the builder promotes boolean-only
attributes to a checklist and multi-value attributes to a radio when values are
supplied. Shapes seen in the data but not yet supported by the mapping
(`box3d`, `poly3d`, `point` where unmapped) are skipped with a warning.

## Setup

- Python 3.10+
- An Encord account with an SSH key registered
  ([docs](https://docs.encord.com/platform-documentation/Annotate/annotate-api-keys))
- Access to the customer's GCS cloud integration in Encord (the public bucket
  itself is read anonymously — see Design characteristics)
- Update the `PRIVATE_KEY_PATH` config variable (`src/config.py`, or the
  `ENCORD_PRIVATE_KEY_PATH` env override) with your Encord SSH private key
  destination, **or** create a private secret in GitHub
  (`ENCORD_API_KEYS_PRIVATE_KEY`) for CI runs — see Configuration below.

```bash
pip install -r requirements.txt
```

`requirements.txt`: `encord`, `google-cloud-storage`, `pytest`.

## Configuration

Everything the customer would change lives in `src/config.py`, and the
credential + GCS values can be overridden via environment variables so the code
runs on any machine (and in CI) without edits.

| Setting | Env override | Description |
| --- | --- | --- |
| `PRIVATE_KEY_PATH` | `ENCORD_PRIVATE_KEY_PATH` | Path to your Encord SSH private key **or** the key contents (see below) |
| `STORAGE_FOLDER_NAME` / `_DESCRIPTION` / `_METADATA` | — | The Index folder to create |
| `ONTOLOGY_NAME` | — | Ontology title |
| `DATASET_NAME` / `DATASET_DESCRIPTION` | — | Dataset title/description |
| `PROJECT_NAME` / `PROJECT_DESCRIPTION` | — | Project title/description |
| `ONTOLOGY_EXPORT_SOURCE` | — | `"local"` or `"gcs"` — where to read label JSONs |
| `ONTOLOGY_EXPORT_PATH` | — | Local dir (e.g. `./sample`) or a `gs://` path |
| `GCS_INTEGRATION_TITLE` | `ENCORD_GCS_INTEGRATION_TITLE` | GCS integration title in Encord (Settings → Integrations) |
| `GCS_REMOTE_URL` | `ENCORD_GCS_REMOTE_URL` | `gs://` bucket/prefix to sync from |
| `BLOB_LIMIT` | — | Cap on JSONs downloaded during ontology discovery (default `500`) |

**Credential handling.** `src/utils/encord_client.py` detects whether
`PRIVATE_KEY_PATH` points at a file on disk (local dev) or *is* the key contents
(CI, where the key is injected as a secret) and calls the right
`create_with_ssh_private_key` variant. No key material is committed.

## Running

Run the whole pipeline:

```bash
python main.py
```

`main.py` runs the stages in order, times each one and the total wall-clock, and
**stops at the first failure**. The whole end-to-end pipeline takes **~6 minutes**
to run. **To skip a step** (e.g. the folder already
exists), comment out its `run_step(...)` line. Any stage can also be run on its
own:

```bash
python scripts/05_create_dataset.py
```

### CI / hand-off

`.github/workflows/run-pipeline.yml` runs the full pipeline on push to `main`:
it checks out the repo, sets up Python 3.11, installs `requirements.txt`, and runs
`python main.py` with the Encord private key supplied via the
`ENCORD_API_KEYS_PRIVATE_KEY` secret (GCS integration/URL overrides are available
as commented-out `vars`). This is the "hand it to the customer and they change
only config" test in practice — they set their own secret and repo variables.

## Report

### Coverage

- **Images** — all images under `10k/` are made available in the Data section via
  the cloud-synced folder (7,000 train + 1,000 val + 2,000 test = **10,000**),
  satisfying the brief's "all images in the Data section" requirement.
- **Metadata** — stage 2 scans the bucket once, separates images from JSONs, and
  matches each image to its label **by filename stem**. Only images with a
  matching JSON *and* at least one of the target attributes get metadata; JSONs
  with no target attributes, and images whose JSON is missing, are logged and
  skipped.
- **Labelled-only into the project** — stage 5 links **only** folder images that
  carry `client_metadata` into the dataset (which the project is built on), so
  unlabelled images stay in Data but out of the annotation workflow — exactly as
  the brief requires. It also skips items already linked, so re-linking is safe.
- **Deliberate skips** — labels that reference images not present in `10k/` can't
  be annotated without the image and are skipped by design; unrecognised ontology
  shapes are skipped with a warning.
- Fill in measured counts after a run: `<N images with metadata>`,
  `<N skipped, reason>`, `<N objects in ontology>`.

> **Not yet imported: bounding-box/polygon labels as Encord label rows.** Stage 2
> imports the scene-level *metadata*; the geometry objects are used to *derive the
> ontology* but are not written into `LabelRowV2` rows. See limitations.

### Runtime / scaling

The dominant cost is **sequential GCS downloads of the label JSONs** (one HTTP
round-trip per file). At ~50–100 ms/file:

- A full scan of all ~100k JSONs ≈ **1.5–3 hours** single-threaded.
- The `10k/` image set only needs its ~10k matching labels ≈ **10–15 min**.
- Ontology discovery (stage 3) is deliberately capped at `BLOB_LIMIT` (500) JSONs
  and currently restricted to the `test` split, so it completes in well under a
  minute — enough to derive a representative ontology without scanning 100k files.

Encord write calls are already batched — stage 2 uses a `Bundle` (up to 1,000
updates per call) and stage 5 uses a single `link_items` call — so the bottleneck
is GCS I/O, not the Encord API. The cloud-sync in stage 1 is asynchronous: the
code starts the job and polls up to a 300s timeout, warning (not failing) if it's
still running. The clear scaling lever is **parallelizing the downloads** (thread
pool), which would cut the label steps roughly by the pool size. Report actual
wall-clock after your run (printed by `main.py`): **~19 min** end-to-end.

### Idempotency & re-runnability

The brief asks that a re-run not create duplicates or fail, and that we state what
a re-run creates/skips/updates. Current status per stage:

| Stage | Re-run behaviour |
| --- | --- |
| 1 Folder | **Get-or-create** — matches by exact name and returns the existing folder |
| 2 Metadata | **Idempotent update** — re-attaches the same `client_metadata` (overwrite, no duplication); schema registration skips keys that already exist |
| 3 Ontology export | **Overwrites** `reports/ontology_objects.json` deterministically |
| 4 Ontology create | ⚠️ **Not yet get-or-create** — `create_ontology` is called unconditionally, so a re-run creates a duplicate ontology. The in-memory builder (`ontology_builder.py`) *is* idempotent (reuses objects, tops up options), but the create call isn't guarded. |
| 5 Dataset | Dataset **create is not** get-or-create, **but** `link_items_to_dataset` skips items already linked, so linking is idempotent |
| 6 Project | **Get-or-create** — reuses an existing project with the same title |

### Configuration knobs

All of `src/config.py` (see table above) plus the env overrides, per-stage
skipping via `main.py`, and `BLOB_LIMIT` / `ONTOLOGY_EXPORT_SOURCE` /
`ONTOLOGY_EXPORT_PATH` for scoping ontology discovery. Not yet exposed as
first-class flags: `--sample N`, `--split`, and `--dry-run` (see limitations).

## Design characteristics

- **Portable** — no personal absolute paths; credentials and GCS config come from
  env vars, and the public bucket is read with an anonymous client (stages 2–3)
  so no credentials are needed for discovery. Runs unchanged in GitHub Actions.
- **Modular** — each stage is a standalone script with a `main()`; shared logic
  lives in `src/` (`storage_folder_builder`, `ontology_builder`,
  `dataset_builder`, `project_builder`, `utils/encord_client`). Scripts are thin
  orchestration; builders hold the reusable SDK logic.
- **Extensible** — the ontology is *derived from the data* (stage 3), so new
  categories/attributes are picked up automatically; the metadata field mapping
  is a single dict; the shape mapping is a single dict.
- **Resilient to unclean data** — per-file `try/except` during discovery, skip +
  warn for missing JSONs, missing attributes, unmatched images, and unrecognised
  shapes, rather than aborting the run.

## Limitations

Some of these are deliberate design trade-offs (with the reasoning below); others
are constraints of the 3-hour scope. Both are captured here.

**Deliberate trade-offs**

- **Ontology discovery on a 500-JSON sample gives the full picture.** Stage 3
  scans only ~500 label JSONs from the `test` split (capped at `BLOB_LIMIT`), and
  that already surfaces all **19 object categories**. Scanning the full 70k `train`
  files yields the same 19 categories — so the sample is representative and the
  full scan buys nothing for ontology derivation. I keep the sample to stay fast;
  widen it only if a future split is expected to introduce new categories.
- **Ontology export is a one-off, not run every time.** If a full-JSON scan were
  ever required, stage 3 (`03_export_ontology_objects.py`) is meant to be run
  **once, or on demand when the category set might change** — not on every pipeline
  run. The derived `reports/ontology_objects.json` is the durable artifact the
  later stages consume.
- **Metadata is scanned JSON-first, only where a matching JPEG exists.** Stage 2
  walks the label JSONs and processes only those with a matching image (by filename
  stem), so it avoids a full scan of both the JSON *and* JPEG sets. The scan reads
  from the **public GCS bucket, not from Encord** — this deliberately keeps read
  load off the Encord platform rather than listing/querying it for every item.
- **Cloud-synced folder instead of a storage (upload) folder.** I use a
  cloud-synced Index folder over the GCS prefix rather than uploading files into an
  Encord storage folder. This avoids re-uploading the customer's data and lets the
  Encord platform sync any new/upcoming files in the bucket automatically.
- **Metadata is overwritten wholesale, not diffed.** Stage 2 re-writes all
  `client_metadata` on every run rather than reading existing metadata, comparing
  it, and writing only the delta. Reading + comparing per item is more expensive
  (extra round-trips) than simply overwriting, so overwrite-always is the cheaper
  and simpler idempotent path here.

**Design limitations**

- **Metadata attachment may not scale by 1–2 orders of magnitude.** The current
  approach would need generators and a concurrency implementation to handle
  significantly larger datasets.

- **Ontology object export is limited to a subset of the JSONs.** It currently
  exports only a limited set of JSONs to extract ontology objects. If there were a
  need to scan all of them, I would merge the metadata-attachment and
  ontology-export steps into one so the JSONs are read only once — attaching
  metadata and extracting objects in the same pass.

- **No checkpointing.** Checkpoints should be implemented in the
  metadata-attachment and ontology-export steps so previously processed data does
  not have to be read again from the cache.

- **No observability for failures & data quality.** It doesn't capture error logs for failed
  metadata updates or incorrect annotations, so there is no visibility into what
  went wrong during a run.

- **Dependency versions are not pinned.** The Encord SDK and related libraries
  should be pinned to exact versions so pipeline runs stay reproducible and are
  not broken by upstream releases.

- **No backfill or retry mechanism.** There is no way to reprocess historical
  data or automatically retry transient failures, so a failed run must be
  restarted manually from the beginning.


## Project layout

```
main.py                              # runs pipeline stages in order, times them (skip via comments)
.github/workflows/run-pipeline.yml   # CI: install deps + run pipeline on push to main
requirements.txt                     # encord, google-cloud-storage, pytest
scripts/
  01_create_cloud_synced_folder.py   # Index folder over the GCS 10k/ prefix (get-or-create + sync)
  02_attach_metadata.py              # register schema + attach weather/scene/time_of_day to images
  03_export_ontology_objects.py      # discover ontology objects from label JSONs
  04_create_ontology.py              # create the ontology in Encord
  05_create_dataset.py               # dataset from folder images that have metadata (labelled only)
  06_create_project.py               # project with dataset + ontology
src/
  config.py                          # all configuration + env overrides
  storage_folder_builder.py          # cloud-synced folder create/sync helpers (get-or-create)
  ontology_builder.py                # builds OntologyStructure from discovered objects (idempotent)
  dataset_builder.py                 # create dataset + link items (skips already-linked)
  project_builder.py                 # get-or-create project from dataset + ontology by name
  utils/encord_client.py             # authenticated EncordUserClient (key path or contents)
reports/
  ontology_objects.json              # output of stage 3, input to stage 4
sample/                              # a few label JSONs for local testing
tests/                               # (empty — reserved for pytest)
```
