#!/usr/bin/env python3
from argparse import ArgumentParser
import os
from .overlay import cmp_files, trim_fslash, trim_tslash
import stat
from subprocess import check_call
import sys

parser = ArgumentParser( description = "Create an overlay for the ODROID" )

parser.add_argument( "basedir",
                     help = "Directory containing the base filesystem (i.e. before the overlay is applied)." )
parser.add_argument( "finaldir",
                     help = "Directory containing the desired final state of the filesystem after the overlay has been applied." )
parser.add_argument( "outdir",
                     help = "Directory to output the overlay to" )
parser.add_argument( "-s", "--squash",
                     help = "File to output squashfs filesystem to" )

args = parser.parse_args()

def create_parent_dirs(src_path, relpath):
    "Duplicate the parent dirs in the overlay"

    parent = os.path.dirname(relpath)
    if parent != "":
        create_parent_dirs( os.path.dirname(src_path), parent )

    add_to_overlay(src_path, relpath)

def add_to_overlay(src_path, relpath, wholedir=False):
    "Add the given filename to the overlay"
    src_path, relpath = [trim_tslash(x) for x in [src_path, relpath]]
    destpath = os.path.join( args.outdir, relpath )

    print("Adding", relpath, wholedir)

    if not os.path.exists( os.path.dirname(destpath) ):
        "Output doesn't have the parent directories yet..."
        create_parent_dirs( os.path.dirname(src_path),
                            os.path.dirname(relpath) )

    if os.path.isdir(src_path):
        if wholedir:
            cmd = ["/usr/bin/rsync", "-a",
                   "{}/".format(src_path),
                   "{}/".format(destpath)]
            check_call(cmd)
        else:
            cmd = ["/usr/bin/rsync", "-dlptgoD",
                   src_path, destpath]
            check_call(cmd)
    else:
        cmd = ["/usr/bin/rsync", "-lptgoD",
               src_path, destpath]
        check_call(cmd)


def del_in_overlay(relpath):
    "Remove the given path in the overlay"
    print("Removing", relpath)
    destpath = os.path.join( args.outdir, relpath )

    os.mknod( destpath, 0o600 | stat.S_IFCHR, os.makedev(0,0) )

if not os.path.exists(args.outdir):
    os.mkdir(args.outdir)

if args.squash is not None and os.path.exists(args.squash):
    print("Error: squashfs output already exists.", file=sys.stderr)
    exit(1)

# Walk finaldir and find files/dirs that don't exist in basedir, or
# that are different to those in basedir

for final_dirpath, dirnames, filenames in os.walk(args.finaldir):

    # Path relative to root
    rel_dirpath = final_dirpath[len(args.finaldir):]
    rel_dirpath = trim_fslash(rel_dirpath)

    #print "Walk", rel_dirpath

    # Path that this dir would be in basedir
    base_dirpath = os.path.join( args.basedir, rel_dirpath )

    # Does this directory exist in basedir?
    if not os.path.exists( base_dirpath ):
        # It's a new directory
        add_to_overlay(final_dirpath, rel_dirpath, wholedir=True)

        # No point in continuing to recurse into it, as it's all new
        dirnames[:] = []
        continue

    # Directories both exist -- do they have the same perms etc?
    elif not cmp_files( base_dirpath, final_dirpath ):
        add_to_overlay(final_dirpath, rel_dirpath)

    # Now check our files
    for fname in filenames:
        base_fname = os.path.join(base_dirpath, fname)
        final_fname = os.path.join(final_dirpath, fname)

        if not cmp_files(base_fname, final_fname):
            add_to_overlay(final_fname,
                           os.path.join(rel_dirpath, fname))

print("----")

# Walk basedir and find files/dirs that aren't in finaldir
for base_dirpath, dirnames, filenames in os.walk(args.basedir):

    # Path relative to root
    rel_dirpath = base_dirpath[len(args.basedir):]
    rel_dirpath = trim_fslash(rel_dirpath)

    # Path that would be in finaldir
    final_dirpath = os.path.join( args.finaldir, rel_dirpath )

    # Does this directory exist in finaldir?
    if not os.path.exists( final_dirpath ):
        # It's been deleted
        del_in_overlay(rel_dirpath)

        # No point in continuing, as it's gone
        dirnames[:] = []
        continue

    # Now check our files
    for fname in filenames:
        base_fname = os.path.join(base_dirpath, fname)
        final_fname = os.path.join(final_dirpath, fname)

        if not os.path.lexists(final_fname):
            del_in_overlay(os.path.join(rel_dirpath, fname))

# The overlay always requires the 'old_root' dir
# This is for pivot_root to run against
old_root = os.path.join(args.outdir, "old_root")
if not os.path.exists(old_root):
    os.mkdir(old_root)

if args.squash is not None:
    check_call( ["mksquashfs", args.outdir, args.squash,
                 "-noappend",
                 "-comp", "xz",
                 "-Xbcj", "arm,armthumb"] )
