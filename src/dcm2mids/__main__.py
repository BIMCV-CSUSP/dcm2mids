import argparse
import logging
from pathlib import Path

from .create_mids_directory import create_mids_directory
from .get_dicomdir import get_dicomdir
from .logger import set_logger

parser = argparse.ArgumentParser(
    formatter_class=argparse.RawDescriptionHelpFormatter,
    description="Script for reading a folder with images and converting them to a BIDS/MIDS Structure.",
)

parser.add_argument(
    "-i", "--input", type=Path, help="Path to the input folder", required=True
)
parser.add_argument(
    "-o", "--output", type=Path, help="Path to the output folder", required=True
)
parser.add_argument(
    "-bp",
    "--body-part",
    dest="body_part",
    type=str,
    help="Specify which part of the body is in the dataset",
    required=True,
)
parser.add_argument(
    "-b",
    "--bids",
    dest="bids",
    action="store_true",
    help="Use BIDS standard. Only applicable for protocols/body parts considered in BIDS.",
)
parser.add_argument(
    "-v",
    "--verbose",
    dest="verbose",
    choices=["DEBUG", "INFO", "WARNING", "ERROR"],
    default="INFO",
    help="Verbose level. One of DEBUG, INFO, WARNING, ERROR",
)
parser.add_argument(
    "-log", "--logfile", type=Path, help="Path to the file to store logs"
)
args = parser.parse_args()

log_level = getattr(logging, args.verbose)
root_logger = set_logger(level=log_level, outpath=args.logfile)

fileset = get_dicomdir(args.input)

create_mids_directory(fileset, args.output, args.body_part)

# generate_tsvs(args.output)
