import sys
import yaml
import os
import logging

DEFAULT_CONFIG_PATH = "config.yaml"

# Logging configuration
# Format: [HH:MM:SS] [LEVEL] Message
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger("SwitchRemote")

def log(msg, level="INFO"):
    lvl = level.upper()
    if lvl == "INFO":
        logger.info(msg)
    elif lvl == "ERROR":
        logger.error(msg)
    elif lvl == "WARNING":
        logger.warning(msg)
    elif lvl == "DEBUG":
        logger.debug(msg)
    else:
        logger.info(msg)

def load_config(path=DEFAULT_CONFIG_PATH):
    if not os.path.exists(path):
        log(f"Config file not found: {path}", "ERROR")
        input("Press Enter to exit...")
        sys.exit(1)
    try:
        log("Loading configuration...")
        with open(path, "r", encoding="utf-8") as f:
            conf = yaml.safe_load(f)
            return conf
    except Exception as e:
        log(f"Failed to parse {path}: {e}", "ERROR")
        input("Press Enter to exit...")
        sys.exit(1)
