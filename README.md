# ODROID Image

Tools for building ODROID images and overlays

## Dependencies

- `bash`
- `mkfs.vfat`, `mkfs.ext2`
- `parted`
- Python 3.6+
- `rsync`
- `squashfs-tools`
- `uboot-tools`

## Setup

Whilst the Python code for this repository can be shipped as a package, and published to PyPI, it is currently not packaged as such. Thus, for usage, you will need to setup the `poetry` development environment. `poetry` is used to allow us to ship this as a package and manage python dependencies.

- Clone the repository from GitHub to a folder on your local machine
- `cd` to that folder, and tell Poetry to install dependencies and set up a virtualenv: `poetry install`
- You can now enter the virtual environment using `poetry shell` and develop using your IDE of choice.

When the virtualenv is active, the following cli commands are available:

### `merge-overlay`

```
usage: merge-overlay [-h] [-s] baseroot overlay outputdir

Merge an ODROID overlay on-top of a root filesystem

positional arguments:
  baseroot         Base root filesystem on which to apply the overlay
  overlay          Mounted overlay directory
  outputdir        The directory to output the merged result to

optional arguments:
  -h, --help       show this help message and exit
  -s, --skip-copy  Skip to applying the overlay immediately (for debug)
```

### `mkoverlay`

```
usage: mkoverlay [-h] [-s SQUASH] basedir finaldir outdir

Create an overlay for the ODROID

positional arguments:
  basedir               Directory containing the base filesystem (i.e. before the
                        overlay is applied).
  finaldir              Directory containing the desired final state of the
                        filesystem after the overlay has been applied.
  outdir                Directory to output the overlay to

optional arguments:
  -h, --help            show this help message and exit
  -s SQUASH, --squash SQUASH
                        File to output squashfs filesystem to
```
