# ODROID Image

Tools for building ODROID images and overlays

## Dependencies

- `bash`
- `mkfs.vfat`, `mkfs.ext2`
- `parted`
- Python 2.7
- `rsync`
- `squashfs-tools`
- `uboot-tools`

## Running under Podman

The ODROID image can be run in a container using Podman (I'm sure this is possible under Docker but I haven't tried). As your computer is likely x86-based you will need to emulate/virtualise an ARM system in order to run the ODROID image. We can do this using [multiarch/qemu-user-static](/multiarch/qemu-user-static).

Set up `qemu-user-static` with:
`sudo podman run --rm --privileged multiarch/qemu-user-static --reset -p yes`

Run the image with:
`podman run --rm -t rgilton/sr2017-base /usr/bin/bash`
