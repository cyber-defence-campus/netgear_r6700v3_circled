# Exploiting a Stack Buffer Overflow on the Netgear R6700v3 (CVE-2022-27646) with the Help of Symbolic Execution
<!--TODO--------------------------------------------------------------------------------------------
- [ ] Revise references
--------------------------------------------------------------------------------------------------->
## Introduction
This repository is intended to demonstrate some functionalities of
[Morion](https://github.com/pdamian/morion), a proof-of-concept (PoC) tool to experiment with
**symbolic execution** on real-world (ARMv7) binaries. We show some of
[Morion](https://github.com/pdamian/morion)'s capabilities by giving a concrete example, namely, how
it can assist during the process of creating a working **exploit for CVE-2022-27646** - a stack
buffer overflow vulnerability in Netgear R6700v3 routers (version 10.04.120_10.0.91).

The repository contains all **files** (under `firmware/`, `libcircled/` and `server/`) needed to
follow along (e.g. scripts to emulate the vulnerable ARMv7 binary) and reproduce the discussed steps
of how to make use of [Morion](https://github.com/pdamian/morion). The **documentation**
(under `docs/`) to demonstrate [Morion](https://github.com/pdamian/morion)'s workings contains the
following chapters:
1. [Setup](docs/1_setup.md) - Explains how to setup analysis (running *Morion*) and target systems
    (running target binary).
2. [Emulation](docs/2_emulation.md) - Explains how to emulate the vulnerable target binary.
3. [Vulnerability CVE-2022-27646](docs/3_vulnerability.md) - Provides some background information to
    the targeted security vulnerability.
4. [Tracing](docs/4_tracing.md) - Explains how to record a concrete execution trace of the target
    binary using *Morion*.
5. [Symbolic Execution](docs/5_symbex.md) - Explains how to use *Morion* for analyzing the recordedd
     trace symbolically.
6. [Exploitation](docs/6_exploitation.md) - Explains how *Morion* might assist in crafting an
    exploit.
## References
- Morion PoC tool:
  - https://github.com/pdamian/morion
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
