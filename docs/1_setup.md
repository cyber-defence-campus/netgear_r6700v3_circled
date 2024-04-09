# Table of Contents
1. [Setup](./1_setup.md#setup)
    1. [Analysis / Host System](./1_setup.md#host-system)
    2. [ARMHF Guest System](./1_setup.md#armhf-guest-system)
2. [Emulation](./2_emulation.md)
3. [Vulnerability CVE-2022-27646](./3_vulnerability.md)
4. [Tracing](./4_tracing.md)
5. [Symbolic Execution](./5_symbex.md)
6. [Exploitation](./6_exploitation.md)
<!--TODO--------------------------------------------------------------------------------------------
--------------------------------------------------------------------------------------------------->
# Setup
This chapter lists instructions on how to set up an **analysis system** (also referred to as the
**host system**), which, on the one hand, hosts a **guest system** emulating the targeted ARMv7
binary and, on the other hand, contains [Morion](https://github.com/pdamian/morion) to collect
execution traces that can then be analyzed symbolically.
## Analysis / Host System
- Install the following dependencies:
  - git
  - binwalk (https://github.com/ReFirmLabs/binwalk)
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
- Install [Morion](https://github.com/pdamian/morion#installation).
## ARMHF Guest System
**Note**: In the following, we assume that the variable $ROOTFS points to the firmware's root filesystem, as set in section [Analysis/Host System](./1_setup.md#analysis--host-system).
- Setup an ARMHF guest system (recommended: *QEMU* ARMHF Debian VM).
- Copy the directories `$ROOTFS/` and `server/` to the ARMHF guest system.

Execute the following instructions within the ARMHF guest system:
- Configure conservative ASLR (as being used on the Netgear R6700v3 routers):
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

----------------------------------------------------------------------------------------------------
[Back-to-Top](./1_setup.md#table-of-contents)