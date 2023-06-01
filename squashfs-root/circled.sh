#!/bin/sh
export SHELL=/bin/sh

# NVRAM emulator
mkdir -p /firmadyne/libnvram/
mkdir -p /firmadyne/libnvram.override/
cp /libnvram.so /firmadyne/libnvram.so

# Mount NAND media
mkdir -p /tmp/media/nand/
mount -t ramfs ramfs /tmp/media/nand/

# Run preloaded target binary with gdbserver
/usr/bin/gdbserver \
    --wrapper env 'LD_PRELOAD="/libcircled.so /firmadyne/libnvram.so /lib/libdl.so.0"' -- \
    127.0.0.1:3000 /bin/circled start

# Kill all leftover processes from the taraget
kill -9 $(ps w | grep [/]bin/circled | awk '{print $1}')

# Clean up
umount /mnt/
umount /tmp/media/nand/
rm -rf /tmp/media/nand/
umount /firmadyne/libnvram
rm -rf /firmadyne/