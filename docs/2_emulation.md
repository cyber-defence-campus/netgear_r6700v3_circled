# Table of Contents
0. [Introduction](../README.md#introduction)
1. [Setup](./1_setup.md)
2. [Emulation](./2_emulation.md#emulation)
    1. [circled.patch.py](./2_emulation.md#circledpatchpy)
    2. [libnvram.so](./2_emulation.md#libnvramso)
    3. [libcircled.so](./2_emulation.md#libcircledso)
    4. [circled.server.py](./2_emulation.md#circledserverpy)
    5. [circled.driver.sh](./2_emulation.md#circleddriversh)
3. [Tracing](./3_tracing.md)
4. [Symbolic Execution](./4_symbex.md)
5. [Vulnerability CVE-2022-27646](./5_vulnerability.md)
6. [Exploitation](./6_exploitation.md)
# Emulation
In this chapter, we briefly mention a handful of **files** and **scripts** that can be used to
emulate the intended target, the binary *circled* from NETGEAR R6700v3 routers (firmware version
1.0.4.120_10.0.91). For each of these files, a brief explanation of its purpose is provided.

**Note**: While not identical, our emulation was inspired by 
[Emulating, Debugging and Exploiting NETGEAR R6700v3 cicled Binary](https://medium.com/@INTfinity/1-1-emulating-netgear-r6700v3-circled-binary-cve-2022-27644-cve-2022-27646-part-1-5bab391c91f2).
### circled.patch.py
The purpose of the first file ([`firmware/circled.patch.py`](../firmware/circled.patch.py)) is to
apply a simple **patch** to the target binary *circled*. The patch removes the invocation of a
function (by replacing  `0xc7a0: bl #0xc6a4` with `0xc7a0: mov r0, #0`) that prohibits the usage of
the environment variable `LD_PRELOAD` (used as a sort of **anti-debugging** measure). As will be
explained below, we use the well-known `LD_PRELOAD` trick to hook selected invocations of shared
library functions (e.g. to emulate NVRAM peripherals).
### libnvram.so
The target binary *circled* relies on the presence of some **NVRAM peripherals**. We simulate these
by preloading (using the `LD_PRELOAD` environment variable) the binary with the open-source library
[libnvram](https://github.com/firmadyne/libnvram). The library emulates the behavior of NVRAM
peripherals by storing key-value pairs into a `tmpfs` mounted at `/firmadyne/libnvram/`. The file
[`firmware/bins/libnvram.so`](../firmware/bins/libnvram.so) is a pre-compiled version
(cross-compiled for `armv7-eabihf` with `uclibc`) of the library.
### libcircled.so
The file [`firmware/bins/libcircled.so`](../firmware/bins/libcircled.so) is another shared library
that is going to be preloaded when invoking the target binary *circled*. It has been pre-compiled
(cross-compiled for `armv7-eabihf` with `uclibc`) from the source file
[`libcircled/circled.c`](../libcircled/circled.c) and contains two hooks for `uclibc` functions
`fgets` and `system`. While `fgets` is hooked only to print out some debugging information, function
`system` modifies two invocations of the `curl` command-line tool that download files
[`circleinfo.txt`](../server/resources/circleinfo.txt) and
[`database.bin`](../server/resources/database.bin) from remote NETGEAR **update servers**. As
explained in more details in chapter [Vulnerability CVE-2022-27646](./5_vulnerability.md), these
download requests perform no certificate validation to authenticate the update servers, what might
allow attackers to force routers to download malicious versions of the files (e.g. using DNS or TCP
redirection). With `libcircled.so` we hook the `curl` invocations to download files from our local
web server (see next [section](./2_emulation.md#circledserverpy)), simulating such an attack.
### circled.server.py
File [`server/circled.server.py`](../server/circled.server.py) implements a simple web server that
may deliver different versions of files [`circleinfo.txt`](../server/resources/circleinfo.txt) and
[`database.bin`](../server/resources/database.bin). As explained in chapter
[Exploitation](./6_exploitation.md), these files will contain the actual payloads triggering the
vulnerability we want to exploit.
### circled.driver.sh
The file [`firmware/circled.driver.sh`](../firmware/circled.driver.sh) is a simple **driver script** that sets up
NVRAM/NAND media, runs the target binary *circled* with all the preloaded libraries, and cleans up
after termination of the target. The script allows to specify a command-line argument `--gdb`, which
when given, leads to the target being run with `gdbserver` attached.

----------------------------------------------------------------------------------------------------
[Back-to-Top](./2_emulation.md#table-of-contents)