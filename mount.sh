#!/bin/bash

# Parse command line arguments
unmount=false
while [[ "$#" -gt 0 ]]; do
    case $1 in
        -u) unmount=true;
    esac
    shift
done

# (Un-) mounting
if [ "$unmount" = true ]; then
    sudo umount --recursive $ROOTFS/proc/
    sudo umount --recursive $ROOTFS/sys/
    sudo umount --recursive $ROOTFS/dev/
else
    sudo mount -t proc /proc/ $ROOTFS/proc/
    sudo mount -t sysfs /sys/ $ROOTFS/sys/
    sudo mount -o bind /dev/ $ROOTFS/dev/
fi