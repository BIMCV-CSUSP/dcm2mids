import logging
from logging import Logger
from pathlib import Path
from typing import Optional, Union


class ColorFormatter(logging.Formatter):
    def __init__(self, format: str):
        blue = "\x1b[94;20m"
        yellow = "\x1b[33;20m"
        red = "\x1b[31;20m"
        reset = "\x1b[0m"

        self.formats = {
            logging.DEBUG: blue + format + reset,
            logging.INFO: format,
            logging.WARNING: yellow + format + reset,
            logging.ERROR: red + format + reset,
        }

    def format(self, record):
        log_fmt = self.formats.get(record.levelno)
        formatter = logging.Formatter(log_fmt, datefmt="%H:%M:%S")
        return formatter.format(record)


def set_logger(
    level: int = logging.INFO, outpath: Optional[Union[Path, str]] = None
) -> Logger:
    logger = logging.getLogger("dcm2mids")
    logger.setLevel(logging.DEBUG)

    # Create console handler and set level desired level
    ch = logging.StreamHandler()
    ch.setLevel(level)

    format_string = "[%(asctime)s] %(name)s - %(levelname)s: %(message)s"

    # Create colored formatter
    color_formatter = ColorFormatter(format_string)
    ch.setFormatter(color_formatter)
    logger.addHandler(ch)

    if outpath:
        fh = logging.FileHandler(outpath, mode="w")
        fh.setLevel(logging.DEBUG)
        formatter = logging.Formatter(format_string)
        fh.setFormatter(formatter)
        logger.addHandler(fh)

    return logger
