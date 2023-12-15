import argparse
# Importante solo utilizar el modulo Path de pathlib.
from pathlib import Path

# Path: __main__.py

parser = argparse.ArgumentParser(
    formatter_class=argparse.RawDescriptionHelpFormatter,
    description="Script for reading a folder with images and converting them to a BIDS/MIDS Structure.",
)

parser.add_argument("-i", "--input", type=Path, help="Path to the input folder", required=True)
parser.add_argument("-o", "--output", type=Path, help="Path to the output folder", required=True)
#parser.add_argument('-bp', '--body-part', dest="body_part", type=str,
#                   help="""Specify which part of the body are 
#                   in the dataset(REQUIRED)""", required=True)
args = parser.parse_args()



