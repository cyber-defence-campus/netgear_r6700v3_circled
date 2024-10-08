# Table of Contents
0. [Introduction](../README.md#introduction)
1. [Setup](./1_setup.md#setup)
    1. [Analysis / Host System](./1_setup.md#analysis--host-system)
    2. [ARMHF Guest System](./1_setup.md#armhf-guest-system)
2. [Emulation](./2_emulation.md)
3. [Tracing](./3_tracing.md)
4. [Symbolic Execution](./4_symbex.md)
5. [Vulnerability CVE-2022-27646](./5_vulnerability.md)
6. [Exploitation](./6_exploitation.md)
# Setup
This chapter lists instructions on how to set up an **analysis system** (also referred to as the
**host system**), which, on the one hand, hosts a **guest system** emulating the targeted ARMv7
binary and, on the other hand, contains [Morion](https://github.com/cyber-defence-campus/morion) to
collect execution traces that can then be analyzed symbolically.
## Analysis / Host System
- Install the following dependencies:
  - git
  - binwalk (https://github.com/ReFirmLabs/binwalk)
- Clone the project repository:
  ```
  git clone https://github.com/cyber-defence-campus/netgear_r6700v3_circled.git && cd netgear_r6700v3_circled/
  ```
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
  
  # Copy circled.driver.sh script (wrapper to emulate binary circled)
  cp firmware/circled.driver.sh $ROOTFS/circled.driver.sh
  ```
- Install [Morion](https://github.com/cyber-defence-campus/morion#installation).
## ARMHF Guest System
**Note**: In the following, we assume that the variable `$ROOTFS` points to the firmware's root
filesystem, as set in section [Analysis / Host System](./1_setup.md#analysis--host-system).
- Setup an ARMHF guest system (recommended: [QEMU ARMHF Debian VM](./1_setup_guest.md)).
- Copy the directories `$ROOTFS/` and `server/` to the ARMHF guest system.

Execute the following instructions within the ARMHF guest system:
- Configure conservative ASLR (as being used on the NETGEAR R6700v3 routers):
  ```shell
  echo 1 | sudo tee /proc/sys/kernel/randomize_va_spac
  ```
- Mount `/proc`, `/sys` and `/dev`:
  ```shell
  ./mount.sh    # Use flag -u to unmount
  ```
- Chroot into the root filesystem:
  ```shell
  sudo chroot $ROOTFS /usr/bin/env -i SHELL="/bin/ash" PS1="(r6700v3) # " /bin/ash
  ```

----------------------------------------------------------------------------------------------------
[Back-to-Top](./1_setup.md#table-of-contents)