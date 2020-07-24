"""Tool to make an overlay."""
from argparse import ArgumentParser
import os

from odroidimage.creator import OverlayCreator


def main():
    parser = ArgumentParser(description="Create an overlay for the ODROID")

    parser.add_argument(
        "basedir",
        help="Directory containing the base filesystem (i.e. before the overlay is applied).",
    )
    parser.add_argument(
        "finaldir",
        help="Directory containing the desired final state of the filesystem after the overlay has been applied.",
    )
    parser.add_argument("outdir", help="Directory to output the overlay to")
    parser.add_argument("-s", "--squash", help="File to output squashfs filesystem to")
    args = parser.parse_args()

    if not os.path.exists(args.outdir):
        os.mkdir(args.outdir)

    if args.squash is not None and os.path.exists(args.squash):
        print("Error: squashfs output already exists.", file=sys.stderr)
        exit(1)

    creator = OverlayCreator(args.basedir, args.finaldir, args.outdir,)

    creator.create()

    if args.squash is not None:
        creator.generate_squashfs(args.squash)
