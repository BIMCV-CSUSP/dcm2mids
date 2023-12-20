import argparse
# Importante solo utilizar el modulo Path de pathlib.
from pathlib import Path


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

get_dicomdir(args.input)

create_mids_directory(args.input, args.output, args.body_part)

generate_tsvs(args.output)
