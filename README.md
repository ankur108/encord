# Encord FDE Challenge — Ankur Chaudhary

Migrating an autonomous-driving customer's images, scene-level metadata,
and annotations into the Encord platform so they can **view, search, and continue
annotating** the data.

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

1. **Code** — the Python pipeline in this repo (`main.py` + `scripts/` + `src/`).
2. **Encord entities** — links to the created Folder and Project:
   - Index Folder: `<ADD FOLDER URL>`
   - Project: `<ADD PROJECT URL>`
   - Dataset: `<ADD DATASET URL>`
   - Ontology: `<ADD ONTOLOGY URL>`

## Approach

The migration is broken into small, independently runnable stages. Each maps to
an Encord entity the customer needs:

| Stage | Script | Encord entity | What it does |
| --- | --- | --- | --- |
| 1 | `01_create_cloud_synced_folders.py` | Folder (Index) | Create a cloud-synced Index folder over the GCS bucket so **all** images appear in the Data section |
| 2 | `02_attach_metadata.py` | — | Read the label JSONs and attach `weather` / `scene` / `time_of_day` as searchable metadata on each image |
| 3 | `03_export_ontology_objects.py` | — | Scan the label JSONs to discover object categories, shapes, and attributes → `reports/ontology_objects.json` |
| 4 | `04_create_ontology.py` | Ontology | Build the ontology from the discovered categories |
| 5 | `05_create_dataset.py` | Dataset | Create a dataset from the folder's images (the units linked into a project) |
| 6 | `06_create_project.py` | Project | Create the annotation project tying the dataset + ontology together |

### Metadata schema (prescribed — do not modify)

Attached to each image as `client_metadata` using the exact field names required
by the customer:

| Field | Source (BDD JSON) | Example |
| --- | --- | --- |
| `weather` | `attributes.weather` | `clear`, `rainy`, `overcast` |
| `scene` | `attributes.scene` | `highway`, `city street`, `residential` |
| `time_of_day` | `attributes.timeofday` | `daytime`, `night`, `dawn/dusk` |

The BDD export uses the key `timeofday`; stage 2 maps it to the required
`time_of_day` field name (see `_METADATA_FIELD_MAP` in `02_attach_metadata.py`).

## Setup

- Python 3.10+
- An Encord account with an SSH key registered
  ([docs](https://docs.encord.com/platform-documentation/Annotate/annotate-api-keys))
- Access to the customer's GCS cloud integration in Encord

```bash
pip install -r requirements.txt
```

## Configuration

Everything the customer would change lives in `src/config.py`; the GCS values
can also be overridden via environment variables so the code runs on any machine
without edits.

| Setting | Env override | Description |
| --- | --- | --- |
| `PRIVATE_KEY_PATH` | — | Path to your Encord SSH private key |
| `STORAGE_FOLDER_NAME` / `_DESCRIPTION` / `_METADATA` | — | The Index folder to create |
| `ONTOLOGY_NAME` | — | Ontology title |
| `DATASET_NAME` / `DATASET_DESCRIPTION` | — | Dataset title/description |
| `PROJECT_NAME` / `PROJECT_DESCRIPTION` | — | Project title/description |
| `ONTOLOGY_EXPORT_SOURCE` | — | `"local"` or `"gcs"` — where to read label JSONs |
| `ONTOLOGY_EXPORT_PATH` | — | Local dir (e.g. `./sample`) or a `gs://` path |
| `GCS_INTEGRATION_TITLE` | `ENCORD_GCS_INTEGRATION_TITLE` | GCS integration title in Encord |
| `GCS_REMOTE_URL` | `ENCORD_GCS_REMOTE_URL` | `gs://` bucket/prefix to sync from |

## Running

Run the whole pipeline:

```bash
python main.py
```

`main.py` lists the stages explicitly and stops at the first failure. **To skip a
step** (e.g. the folder already exists), comment out its `run_step(...)` line.
Any stage can also be run on its own:

```bash
python scripts/05_create_dataset.py
```

## Report

### Coverage

- **Images** — all images under `10k/` are made available in the Data section via
  the cloud-synced folder (7,000 train + 1,000 val + 2,000 test = **10,000**).
- **Labels/metadata** — the `100k/` tree holds ~100,000 JSON files, ~10× the
  number of images. Stage 2 matches each image to its label **by filename stem**;
  only images with a matching JSON get metadata, and (via stage 5) only images
  with metadata are linked into the dataset/project. Labels that reference images
  not present in `10k/` are deliberately skipped — they can't be annotated
  without the image.
- Fill in measured counts after a run: `<N images with metadata>`,
  `<N skipped, reason>`.

### Runtime / scaling

The dominant cost is **sequential GCS downloads of the label JSONs** (one HTTP
round-trip per file). At ~50–100 ms/file:

- A full scan of all ~100k JSONs ≈ **1.5–3 hours** single-threaded.
- The `10k/` image set only needs its ~10k matching labels ≈ **10–15 min**.

Encord write calls are already batched — stage 2 uses a `Bundle` (up to 1,000
updates per call) and stage 5 uses a single `link_items` call — so the bottleneck
is GCS I/O, not the Encord API. The clear scaling lever is **parallelizing the
downloads** (thread pool), which would cut the label steps roughly by the pool
size. Report actual wall-clock after your run: `<runtime>`.

### Configuration knobs

All of `src/config.py` (see table above), plus per-stage skipping via `main.py`.
Not yet exposed: `--sample N`, `--split`, and `--dry-run` flags (see limitations).

## Design characteristics

- **Portable** — no personal absolute paths; GCS config comes from env vars, and
  the public bucket is read with an anonymous client (stage 3) so no credentials
  are needed for discovery.
- **Modular** — each stage is a standalone script with a `main()`; shared logic
  lives in `src/` (`storage_folders`, `ontology_builder`, `utils/encord_client`).
- **Extensible** — the ontology is *derived from the data* (stage 3), so new
  categories/attributes are picked up automatically; the metadata field mapping
  is a single dict.

## Known limitations & trade-offs

Given the 3-hour scope, these are deliberate:

- **Annotations are not yet imported as Encord labels.** Stage 2 imports the
  scene-level *metadata* from the JSONs; the bounding-box objects are used to
  *derive the ontology* but are not written into label rows. Importing them
  (`LabelRowV2`) is the natural next step.
- **Partial idempotency.** Stage 1 (folder) is get-or-create. Ontology, dataset,
  and project creation are **not** yet get-or-create — a re-run would create
  duplicates. Skipping is currently manual via `main.py`.
- **Scope flags** (`--sample`, `--split`, `--dry-run`) are described above but
  not implemented.
- **Sequential downloads** are the main performance limit (see Runtime).

## Project layout

```
main.py                              # runs pipeline stages in order (skip via comments)
scripts/
  01_create_cloud_synced_folders.py  # Index folder over the GCS bucket
  02_attach_metadata.py              # attach weather/scene/time_of_day to images
  03_export_ontology_objects.py      # discover ontology objects from label JSONs
  04_create_ontology.py              # create the ontology in Encord
  05_create_dataset.py               # dataset from folder images (labeled only)
  06_create_project.py               # project with dataset + ontology
src/
  config.py                          # all configuration
  storage_folders.py                 # folder create/sync helpers (get-or-create)
  ontology_builder.py                # builds OntologyStructure from discovered objects
  utils/encord_client.py             # authenticated EncordUserClient
reports/
  ontology_objects.json              # output of stage 3, input to stage 4
sample/                              # a few label JSONs for local testing
```
