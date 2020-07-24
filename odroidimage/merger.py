#!/usr/bin/env python3
from subprocess import check_call
import os
from .overlay import trim_fslash, cmp_files
import shutil
import stat
import sys
import tempfile

class OverlayMerger:

    def __init__(self, baseroot, overlay, outputdir):
        self.baseroot = baseroot
        self.overlay = overlay
        self.outputdir = outputdir

    def merge(self):
         # Iterate through the overlay, replacing things in the target as we go
        for overlay_cur_dirpath, dirnames, filenames in os.walk(self.overlay):

            # TODO: Deduplicate this
            # Path relative to root:
            rel_cur_dirpath = overlay_cur_dirpath[ len(self.overlay): ]
            rel_cur_dirpath = trim_fslash(rel_cur_dirpath)

            # Iterate through directories
            for dirname in dirnames:
                output_full_dirpath = os.path.join( self.outputdir, rel_cur_dirpath, dirname )
                overlay_full_dirpath = os.path.join( overlay_cur_dirpath, dirname )

                if not cmp_files( overlay_full_dirpath, output_full_dirpath ):
                    self._add_dir( overlay_full_dirpath, output_full_dirpath )

            # Iterate through filenames
            for filename in filenames:
                output_full_filepath = os.path.join( self.outputdir, rel_cur_dirpath, filename )
                overlay_full_filepath = os.path.join( overlay_cur_dirpath, filename )

                if self._is_whiteout(overlay_full_filepath):
                    self._whiteout(output_full_filepath)
                else:
                    self._add_file( overlay_full_filepath, output_full_filepath )

    @staticmethod
    def _add_dir(src, dest):
        "Add the given directory (not its contents)"
        print("ADD dir:", dest)
        cmd = ["/usr/bin/rsync", "-dlptgoD", src, dest]
        check_call(cmd)

    @staticmethod
    def _add_file(src, dest):
        "Add the given file"
        print("ADD file:", dest)
        cmd = ["/usr/bin/rsync", "-lptgoD", src, dest]
        check_call(cmd)

    @staticmethod
    def _is_whiteout(path):
        "Test the given path to see if it's a whiteout"
        s = os.lstat(path)

        if not stat.S_ISCHR(s.st_mode):
            return False

        if os.major(s.st_rdev) == 0 and os.minor(s.st_rdev) == 0:
            return True

        return False

    @staticmethod
    def _whiteout(path):
        "Whiteout the given path"
        print("Whiteout", path)

        if os.path.islink(path) or os.path.isfile(path):
            os.remove(path)
        else:
            shutil.rmtree(path)
