"""Run the Encord pipeline stage by stage.

Each stage is a script in scripts/. They're listed explicitly below so you can
comment out any step you don't need to re-run.
"""
import logging
import runpy
import sys
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

ROOT = Path(__file__).resolve().parent
SCRIPTS_DIR = ROOT / "scripts"


def run_step(script_name):
    """Run a single pipeline script by file name."""
    logger.info("Running %s", script_name)
    try:
        runpy.run_path(str(SCRIPTS_DIR / script_name), run_name="__main__")
    except SystemExit as e:
        if e.code:
            logger.error("%s failed (exit %s), stopping", script_name, e.code)
            raise
    except Exception:
        logger.exception("%s crashed, stopping", script_name)
        sys.exit(1)


def main():
    # make sure `from src...` works when scripts run
    sys.path.insert(0, str(ROOT))

    # Comment out any step you don't need to run.
    run_step("01_create_cloud_synced_folder.py")   # create the GCS-synced storage folder
    run_step("02_attach_metadata.py")               # attach weather/scene/timeofday metadata
    run_step("03_export_ontology_objects.py")        # export ontology objects from the JSON labels
    run_step("04_create_ontology.py")                # create the ontology in Encord
    run_step("05_create_dataset.py")                 # create dataset from folder images
    run_step("06_create_project.py")                 # create project with dataset + ontology

    logger.info("Done")


if __name__ == "__main__":
    main()
