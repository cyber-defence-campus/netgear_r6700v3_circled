#!/bin/sh
export SHELL=/bin/sh

# NVRAM emulator
mkdir -p /firmadyne/libnvram/
mkdir -p /firmadyne/libnvram.override/
cp /libnvram.so /firmadyne/libnvram.so

# Mount NAND media
mkdir -p /tmp/media/nand/
mount -t ramfs ramfs /tmp/media/nand/

# Parse command line arguments
use_gdb=false
while [[ "$#" -gt 0 ]]; do
    case $1 in
        --gdb) use_gdb=true;
    esac
    shift
done

# Run preloaded target binary
if [ "$use_gdb" = true ]; then
    # With gdbserver
    /usr/bin/gdbserver \
        --wrapper env 'LD_PRELOAD="/libcircled.so /firmadyne/libnvram.so /lib/libdl.so.0"' -- \
        127.0.0.1:3000 /bin/circled start
else
    # Without gdbserver
    LD_PRELOAD="/libcircled.so /firmadyne/libnvram.so /lib/libdl.so.0" /bin/circled start
    sleep 30
fi

# Kill all leftover processes from the taraget
kill -9 $(ps w | grep [/]bin/circled | awk '{print $1}')

# Clean up
umount /mnt/
umount /tmp/media/nand/
rm -rf /tmp/media/nand/
umount /firmadyne/libnvram
rm -rf /firmadyne/