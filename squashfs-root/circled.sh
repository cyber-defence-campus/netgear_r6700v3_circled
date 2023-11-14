#!/bin/sh
export SHELL=/bin/sh

# NVRAM emulator
echo "[>] Setup NVRAM emulator"
mkdir -p /firmadyne/libnvram/
mkdir -p /firmadyne/libnvram.override/
cp /libnvram.so /firmadyne/libnvram.so

# Mount NAND media
echo "[>] Mount NAND media"
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
    echo "[>] Launch circled binary with GDB attached"
    /usr/bin/gdbserver \
        --wrapper env 'LD_PRELOAD="/libcircled.so /firmadyne/libnvram.so /lib/libdl.so.0"' -- \
        127.0.0.1:3000 /bin/circled.patched start
else
    # Without gdbserver
    echo "[>] Launch circled binary without GDB attached"
    LD_PRELOAD="/libcircled.so /firmadyne/libnvram.so /lib/libdl.so.0" /bin/circled.patched start
    while [ ! -e "/tmp/st0" ]; do
        sleep 1
    done
    sleep 5
fi

# Kill all leftover processes from the target binary
echo "[>] Kill circled binary"
kill -9 $(ps w | grep [/]bin/circled | awk '{print $1}')

# Clean up
echo "[>] Clean up"
umount /mnt/
umount /tmp/media/nand/
umount /firmadyne/libnvram
rm -rf /firmadyne/
cat /tmp/circled.log
rm -rf /tmp/*
echo "[<] Done"