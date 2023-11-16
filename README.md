# Exploiting a Stack Buffer Overflow on the Netgear R6700v3
## 1. Setup
### 1.1 Host
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
- Copy the root filesystem to an ARMHF guest system (e.g. a *QEMU* ARMHF Debian VM)
### 1.2 Guest: ARMHF
- In the following, we assume that variable $ROOTFS points to the copied firmware root filesystem

## 1. Individual Binary Emulation
- Extract the R6700v3 firmware with *binwalk*:
  ```
  binwalk -e -M firmware/R6700v3-V1.0.4.120_10.0.91.zip
  ```
- Use *QEMU* to boot an ARMHF Debian system
- Upload the firmware's root filesystem (`_R6700v3-V1.0.4.120_10.0.91.zip.extracted/_R6700v3-V1.0.4.120_10.0.91.chk.extracted/squashfs-root/`) to the ARM Debian system
- Build and copy a statically-linked version of *gdbserver* to the root filesystem (`/usr/bin/gdbserver`)
- Emulate the *circled* binary
  - Cross-compile (use *bootlin* toolchain for *armv7-eabihf* and *ulibc*) *libnvram* to emulate non-volatile RAM (NVRAM)
  - Chroot into the root filesystem
    - `sudo mount -t proc /proc/ ./squashfs-root/proc/`
    - `sudo mount -t sysfs /sys/ ./squashfs-root/sys/`
    - `sudo mount -o bind /dev/ ./squashfs-root/dev/`
    - `sudo chroot ./squashfs-root/ /bin/sh`
    - `export SHELL=/bin/sh`
    - `echo 1 | tee /proc/sys/kernel/randomize_va_space`
  - Execute the targeted binary (use `circled.sh` helper script)
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
## 3. Notes
```
git clone https://github.com/pdamian/netgear_r6700v3_circled.git && cd netgear_r6700v3_circled/
binwalk -e -M -C firmware/ firmware/R6700v3-V1.0.4.120_10.0.91.zip
export ROOTFS="`pwd`/firmware/_R6700v3-V1.0.4.120_10.0.91.zip.extracted/_R6700v3-V1.0.4.120_10.0.91.chk.extracted/squashfs-root"
cp binaries/gdbserver $ROOTFS/usr/bin/gdbserver
cp binaries/libnvram.so $ROOTFS/libnvram.so
python3 circled.patch.py $ROOTFS/bin/circled $ROOTFS/bin/circled.patched
chmod +x $ROOTFS/bin/circled.patched
cp circled.sh $ROOTFS/circled.sh
chmod +x $ROOTFS/circled.sh
cd libcricled/
make
cp libcircled.so $ROOTFS/libcricled.so
cd ../
```
