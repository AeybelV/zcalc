"""
zcalc CLI

"""

import argparse
import os
import sys
from typing import List, Optional

from zcalc import stackup


def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    """Parses arguements from command line

    Args:
        argv: CLI arguments

    Returns: A argspace Namespace that can be operated on

    """
    # Default printout when called with no args
    parser = argparse.ArgumentParser(
        description="PCB trace width / impedance / current calculator."
    )

    # Possible Argumenets
    parser.add_argument(
        "--stackup",
        required=True,
        help="YAML file describing the physical PCB stackup (copper, cores, prepregs, mask, etc.).",
    )

    parser.add_argument(
        "--nets",
        required=True,
        help="YAML file describing per-net electrical and layout requirements.",
    )

    parser.add_argument(
        "--out",
        default="out",
        help="Output directory for CSV/JSON/plots (default: ./out).",
    )

    parser.add_argument(
        "--no-plots",
        action="store_true",
        help="Disable generation of PNG plots even if matplotlib is installed.",
    )

    parser.add_argument(
        "--table-format",
        default="markdown",
        choices=["markdown", "simple", "csv", "tsv"],
        help="Table format for stdout summary (default: markdown).",
    )

    return parser.parse_args(argv)


def main(argv: Optional[List[str]] = None) -> None:
    """Program Entrypoint"""

    args = parse_args(argv)

    os.makedirs(args.out, exist_ok=True)

    try:
        s = stackup.load_stackup(args.stackup)
        print(s)
    except stackup.InvalidStackup as e:
        print(e)
        sys.exit(-1)

    print("Goodbye!")
