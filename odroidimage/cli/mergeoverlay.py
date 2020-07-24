"""Tool to merge an overlay onto a rootfs."""
from argparse import ArgumentParser
from subprocess import check_call
import os
import sys

from odroidimage.merger import OverlayMerger

def main():
    parser = ArgumentParser( description = "Merge an ODROID overlay on-top of a root filesystem" )
    parser.add_argument( "baseroot",
                        help = "Base root filesystem on which to apply the overlay" )
    parser.add_argument( "overlay",
                        help = "Mounted overlay directory" )
    parser.add_argument( "outputdir",
                        help = "The directory to output the merged result to" )
    parser.add_argument( "-s", "--skip-copy", action="store_true",
                        help = "Skip to applying the overlay immediately (for debug)" )
    args = parser.parse_args()

    # Copy baseroot to output directory
    if not args.skip_copy:
        if os.path.exists(args.outputdir):
            print("Error: Output directory already exists", file=sys.stderr)
            exit(1)
    else:
        if not os.path.exists(args.outputdir):
            print("Error: Output directory doesn't exist", file=sys.stderr)
            exit(1)

    if not os.path.exists(args.overlay):
        print("Error: Overlay directory doesn't exist", file=sys.stderr)
        exit(1)

    if not os.path.isdir(args.overlay):
        print("Error: Overlay is not a directory", file=sys.stderr)
        exit(1)

    if not args.skip_copy:
        print("Copying base directory to target...", end=' ')
        sys.stdout.flush()
        check_call(["cp", "-a", args.baseroot, args.outputdir])
        print("done.")

    merger = OverlayMerger(args.baseroot, args.overlay, args.outputdir)

    merger.merge()
