# Exploiting a Stack Buffer Overflow on the NETGEAR R6700v3 (CVE-2022-27646) with the Help of Symbolic Execution
<!--TODO--------------------------------------------------------------------------------------------
- [ ] Add all external references
--------------------------------------------------------------------------------------------------->
## Introduction
This repository is intended to demonstrate some functionalities of
[Morion](https://github.com/pdamian/morion), a proof-of-concept (PoC) tool to experiment with
**symbolic execution** on real-world (ARMv7) binaries. We show some of
[Morion](https://github.com/pdamian/morion)'s capabilities by giving a concrete example, namely, how
it can assist during the process of creating a working **exploit for CVE-2022-27646** - a stack
buffer overflow vulnerability in NETGEAR R6700v3 routers (affected version 1.0.4.120_10.0.91, fixed
in later versions).

The repository contains all **files** (under [firmware](./firmware/), [libcircled](./libcircled/),
[morion](./morion/) and [server](./server/)) needed to follow along (e.g. scripts to emulate the
vulnerable ARMv7 binary) and reproduce the discussed steps of how to use
[Morion](https://github.com/pdamian/morion). The **documentation** (under [docs](./docs/) and
[logs](./logs/)), to demonstrate [Morion](https://github.com/pdamian/morion)'s workings, contains
the following chapters:
1. [Setup](docs/1_setup.md) - Explains how to setup analysis (running *Morion*) and target systems
    (running target binary *circled*).
2. [Emulation](docs/2_emulation.md) - Explains how to emulate the vulnerable target binary.
3. [Tracing](docs/3_tracing.md) - Explains how to record a concrete execution trace of the target
    binary using *Morion*.
4. [Symbolic Execution](docs/4_symbex.md) - Explains how to use *Morion* for analyzing the recorded
     trace symbolically.
5. [Vulnerability CVE-2022-27646](docs/5_vulnerability.md) - Provides some background information to
    the targeted vulnerability.
6. [Exploitation](docs/6_exploitation.md) - Explains how *Morion* can assist during the process of
    crafting an exploit.
## References
- Morion PoC Tool:
  - https://github.com/pdamian/morion
- Defeating the NETGEAR R6700v3:
  - https://www.synacktiv.com/en/publications/pwn2own-austin-2021-defeating-the-netgear-r6700v3.html
- Emulating, Debugging and Exploiting NETGEAR R6700v3 *cicled* Binary:
  - https://medium.com/@INTfinity/1-1-emulating-netgear-r6700v3-circled-binary-cve-2022-27644-cve-2022-27646-part-1-5bab391c91f2
  - https://medium.com/@INTfinity/1-2-emulating-netgear-r6700v3-circled-binary-cve-2022-27644-cve-2022-27646-part-2-cf1571493117
  - https://medium.com/@INTfinity/1-3-exploiting-and-debugging-netgear-r6700v3-circled-binary-cve-2022-27644-cve-2022-27646-a80dbaf1245d
- NVRAM Emulator:
  - https://github.com/firmadyne/libnvram
- Ready-to-Use Cross-Compilation Toolchains:
  - https://toolchains.bootlin.com/
- Other Tools:
  - https://github.com/ReFirmLabs/binwalk
  - https://github.com/pwndbg/pwndbg
  - https://github.com/slimm609/checksec.sh
  - https://github.com/sashs/Ropper
  - https://github.com/JonathanSalwan/ROPgadget
## Authors
- [Damian Pfammatter](https://github.com/pdamian), [Cyber-Defense Campus (ar S+T)](https://www.cydcampus.admin.ch/)
