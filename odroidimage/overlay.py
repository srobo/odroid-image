import os
import stat

def cmp_files(a, b):
    """Compare two files

    Return False if different"""

    if not os.path.lexists(a) or not os.path.lexists(b):
        return False

    a_s, b_s = os.lstat(a), os.lstat(b)

    # Check that these two files are the same time and have the
    # same permissions
    if a_s.st_mode != b_s.st_mode:
        return False

    if a_s.st_uid != b_s.st_uid or \
       a_s.st_gid != b_s.st_gid:
        return False

    # Only compare size if it's a regular file
    if stat.S_ISREG(a_s.st_mode) != 0:
        if a_s.st_size != b_s.st_size:
            return False

        c_a = open(a, "r").read()
        c_b = open(b, "r").read()
        if c_a != c_b:
            return False

    elif stat.S_ISLNK(a_s.st_mode) != 0:
        # Check the links have the same target
        if os.readlink(a) != os.readlink(b):
            return False

    # Files are the same!
    return True

def trim_fslash(d):
    "Remove first slash from a path"
    while len(d) and d[0] == "/":
        d = d[1:]
    return d

def trim_tslash(d):
    "Remove trailing slashes from a path"
    while len(d) and d[-1] == "/":
        d = d[:-1]
    return d
