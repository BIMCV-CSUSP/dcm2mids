import argparse
from pathlib import Path

from .create_mids_directory import create_mids_directory
from .get_dicomdir import get_dicomdir


def main():
    """
    Main entry point allowing external calls
    """


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
    help="""Specify which part of the body are in the dataset(REQUIRED)""",
    required=True,
)
parser.add_argument(
    "-b",
    "--bids",
    dest="bids",
    action="store_true",
    help="use BIDS standard. Only applicable for protocols/body parts considered in BIDS.",
)
args = parser.parse_args()

fileset = get_dicomdir(args.input)

create_mids_directory(fileset, args.output, args.body_part)

# generate_tsvs(args.output)
