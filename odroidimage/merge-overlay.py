#!/usr/bin/env python3
from argparse import ArgumentParser
from subprocess import check_call
import os
from .overlay import trim_fslash, cmp_files
import shutil
import stat
import sys
import tempfile

def add_dir(src, dest):
    "Add the given directory (not its contents)"
    print("ADD dir:", dest)
    cmd = ["/usr/bin/rsync", "-dlptgoD", src, dest]
    check_call(cmd)

def add_file(src, dest):
    "Add the given file"
    print("ADD file:", dest)
    cmd = ["/usr/bin/rsync", "-lptgoD", src, dest]
    check_call(cmd)

def is_whiteout(path):
    "Test the given path to see if it's a whiteout"
    s = os.lstat(path)

    if not stat.S_ISCHR(s.st_mode):
        return False

    if os.major(s.st_rdev) == 0 and os.minor(s.st_rdev) == 0:
        return True

    return False

def whiteout(path):
    "Whiteout the given path"
    print("Whiteout", path)

    if os.path.islink(path) or os.path.isfile(path):
        os.remove(path)
    else:
        shutil.rmtree(path)

if __name__ == "__main__":

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

    # Iterate through the overlay, replacing things in the target as we go
    for overlay_cur_dirpath, dirnames, filenames in os.walk(args.overlay):

        # Path relative to root:
        rel_cur_dirpath = overlay_cur_dirpath[ len(args.overlay): ]
        rel_cur_dirpath = trim_fslash(rel_cur_dirpath)

        for dirname in dirnames:
            output_full_dirpath = os.path.join( args.outputdir, rel_cur_dirpath, dirname )
            overlay_full_dirpath = os.path.join( overlay_cur_dirpath, dirname )

            if not cmp_files( overlay_full_dirpath, output_full_dirpath ):
                add_dir( overlay_full_dirpath, output_full_dirpath )

        for filename in filenames:
            output_full_filepath = os.path.join( args.outputdir, rel_cur_dirpath, filename )
            overlay_full_filepath = os.path.join( overlay_cur_dirpath, filename )

            if is_whiteout(overlay_full_filepath):
                whiteout(output_full_filepath)
            else:
                add_file( overlay_full_filepath, output_full_filepath )
