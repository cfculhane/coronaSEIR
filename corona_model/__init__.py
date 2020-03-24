"""
Corona SEIR Model
"""
from pathlib import Path

import pprintpp
import yaml

__version__ = "0.2.0"

from corona_model.shared_logging import setup_logging

SCRIPT_DIR = Path(__file__).parent
PROJECT_DIR = SCRIPT_DIR.parent
CONFIG = yaml.safe_load(SCRIPT_DIR.joinpath("config.yaml").read_text(encoding="utf-8"))
logger, log_pth = setup_logging(log_config_path=Path(SCRIPT_DIR, "logging_config.yaml"),
                                log_dir=PROJECT_DIR.joinpath("logs"),
                                module_name="CoronaSEIR")
logger.info(f"Started CoronaSEIR with config:")
logger.info(pprintpp.pprint(CONFIG))
