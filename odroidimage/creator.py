#!/usr/bin/env python3
import os
from .overlay import cmp_files, trim_fslash, trim_tslash
import stat
from subprocess import check_call
import sys


class OverlayCreator:
    """Create an overlay."""

    def __init__(self, basedir, finaldir, outdir):
        self.basedir = basedir
        self.finaldir = finaldir
        self.outdir = outdir

    def _relative_path(self, path):
        """Find the path relative to root."""
        rel_dirpath = path[len(self.finaldir) :]
        return trim_fslash(rel_dirpath)

    def _walk_existing_files(self):
        """
        Walk finaldir and find files/dirs that exist and have changed.

        This includes files that don't exist in basedir and files that
        are different to those in basedir.
        """
        for final_dirpath, dirnames, filenames in os.walk(self.finaldir):

            # Path relative to root
            rel_dirpath = self._relative_path(final_dirpath)

            # print "Walk", rel_dirpath

            # Path that this dir would be in basedir
            base_dirpath = os.path.join(self.basedir, rel_dirpath)

            # Does this directory exist in basedir?
            if not os.path.exists(base_dirpath):
                # It's a new directory
                self._add_to_overlay(final_dirpath, rel_dirpath, wholedir=True)

                # No point in continuing to recurse into it, as it's all new
                dirnames[:] = []
                continue

            # Directories both exist -- do they have the same perms etc?
            elif not cmp_files(base_dirpath, final_dirpath):
                self._add_to_overlay(final_dirpath, rel_dirpath)

            # Now check our files
            for fname in filenames:
                base_fname = os.path.join(base_dirpath, fname)
                final_fname = os.path.join(final_dirpath, fname)

                if not cmp_files(base_fname, final_fname):
                    self._add_to_overlay(final_fname, os.path.join(rel_dirpath, fname))

    def _walk_missing_files(self):
        """Walk basedir and find files/dirs that aren't in finaldir."""

        for base_dirpath, dirnames, filenames in os.walk(self.basedir):

            # Path relative to root
            rel_dirpath = self._relative_path(base_dirpath)

            # Path that would be in finaldir
            final_dirpath = os.path.join(self.finaldir, rel_dirpath)

            # Does this directory exist in finaldir?
            if not os.path.exists(final_dirpath):
                # It's been deleted
                self._del_in_overlay(rel_dirpath)

                # No point in continuing, as it's gone
                dirnames[:] = []
                continue

            # Now check our files
            for fname in filenames:
                base_fname = os.path.join(base_dirpath, fname)
                final_fname = os.path.join(final_dirpath, fname)

                if not os.path.lexists(final_fname):
                    self._del_in_overlay(os.path.join(rel_dirpath, fname))

    def _ensure_folder_in_root(self, folder_path):
        abs_path = os.path.join(self.outdir, folder_path)
        if not os.path.exists(abs_path):
            os.mkdir(abs_path)

    def create(self):
        self._walk_existing_files()

        print("----")

        self._walk_missing_files()

        # The overlay always requires the 'old_root' dir
        # This is for pivot_root to run against
        self._ensure_folder_in_root("old_root")

    def generate_squashfs(self, squashdir):
        """Generate a squashfs."""
        check_call(
            [
                "mksquashfs",
                self.outdir,
                squashdir,
                "-noappend",
                "-comp",
                "xz",
                "-Xbcj",
                "arm,armthumb",
            ]
        )

    def _create_parent_dirs(self, src_path, relpath):
        "Duplicate the parent dirs in the overlay"
        parent = os.path.dirname(relpath)
        if parent != "":
            self._create_parent_dirs(os.path.dirname(src_path), parent)

        self._add_to_overlay(src_path, relpath)

    def _add_to_overlay(self, src_path, relpath, wholedir=False):
        "Add the given filename to the overlay"
        src_path, relpath = [trim_tslash(x) for x in [src_path, relpath]]
        destpath = os.path.join(self.outdir, relpath)

        print("Adding", relpath, wholedir)

        if not os.path.exists(os.path.dirname(destpath)):
            "Output doesn't have the parent directories yet..."
            self._create_parent_dirs(
                os.path.dirname(src_path), os.path.dirname(relpath)
            )

        if os.path.isdir(src_path):
            if wholedir:
                cmd = [
                    "/usr/bin/rsync",
                    "-a",
                    "{}/".format(src_path),
                    "{}/".format(destpath),
                ]
                check_call(cmd)
            else:
                cmd = ["/usr/bin/rsync", "-dlptgoD", src_path, destpath]
                check_call(cmd)
        else:
            cmd = ["/usr/bin/rsync", "-lptgoD", src_path, destpath]
            check_call(cmd)

    def _del_in_overlay(self, relpath):
        "Remove the given path in the overlay"
        print("Removing", relpath)
        destpath = os.path.join(self.outdir, relpath)

        os.mknod(destpath, 0o600 | stat.S_IFCHR, os.makedev(0, 0))
