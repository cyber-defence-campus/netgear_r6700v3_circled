# Table of Contents
1. [Setup](./1_setup.md#setup)
    1. [Host System](./1_setup.md#host-system)
    2. [ARMHF Guest System](./1_setup.md#armhf-guest-system)
2. [Emulation](./2_emulation.md)
3. [Vulnerability CVE-2022-27646](./3_vulnerability.md)
4. [Tracing](./4_tracing.md)
5. [Symbolic Execution](./5_symbex.md)
6. [Exploitation](./6_exploitation.md)
<!--TODO--------------------------------------------------------------------------------------------
- [ ] Document how to install Morion
- [ ] Step-by-step test the documented setup
--------------------------------------------------------------------------------------------------->
# Setup
## Host System
- Install the following dependencies:
  - git
  - binwalk (https://github.com/ReFirmLabs/binwalk)
  - morion (https://github.com/pdamian/morion)
- Clone the project repository:
  ```
  git clone https://github.com/pdamian/netgear_r6700v3_circled.git && cd netgear_r6700v3_circled/
- Extract the R6700v3 firmware with *binwalk*:
  ```
  binwalk -e -M -C firmware/ firmware/R6700v3-V1.0.4.120_10.0.91.zip
  ```
- Copy the following files to the firmware's root filesystem:
  ```
  # Variable pointing to the root filesystem
  export ROOTFS="$(pwd)/firmware/_R6700v3-V1.0.4.120_10.0.91.zip.extracted/_R6700v3-V1.0.4.120_10.0.91.chk.extracted/squashfs-root"
  
  # Copy pre-built gdbserver binary (or compile your own statically-linked version; arch: armv7-eabihf, libc: uclibc)
  cp firmware/bins/gdbserver $ROOTFS/gdbserver
  
  # Copy pre-built libnvram.so library (or compile your own version; arch: armv7-eabihf, libc: uclibc)
  cp firmware/bins/libnvram.so $ROOTFS/libnvram.so
  
  # Copy pre-built libcircled.so library (or compile your own version; arch: armv7-eabihf, libc: uclibc)
  cp firmware/bins/libcircled.so $ROOTFS/libcircled.so

  # Patch out the anti-debugging functionality (allow LDPRELOAD) of the circled binary
  python3 firmware/circled.patch.py $ROOTFS/bin/circled $ROOTFS/bin/circled.patched
  
  # Copy circled.sh script (wrapper to emulate binary circled)
  cp firmware/circled.sh $ROOTFS/circled.sh
  ```
- Copy the directories `$ROOTFS/` and `server/` to an ARMHF guest system (e.g. a *QEMU* ARMHF Debian VM).
## ARMHF Guest System
- In the following, we assume that the variable $ROOTFS points to the copied firmware's root filesystem.
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
  export SHELL=/bin/sh
  ```
