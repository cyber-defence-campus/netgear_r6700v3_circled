# Table of Contents
1. [Setup](./1_setup.md)
2. [Emulation](./2_emulation.md#emulation)
    1. [circled.patch.py](./2_emulation.md#cicrledpatchpy)
    2. [libnvram.so](./2_emulation.md#libnvramso)
    3. [libcircled.so](./2_emulation.md#libcircledso)
    4. [circled.sh](./2_emulation.md#circledsh)
    5. [circled.server.py](./2_emulation.md#circledserverpy)
3. [Vulnerability CVE-2022-27646](./3_vulnerability.md)
4. [Tracing](./4_tracing.md)
5. [Symbolic Execution](./5_symbex.md)
6. [Exploitation](./6_exploitation.md)
<!--TODO--------------------------------------------------------------------------------------------
--------------------------------------------------------------------------------------------------->
# Emulation
In this chapter we briefly mention a handful of files and scripts that can be used to run the
intended target, the binary *circled* from Netgear R6700v3 routers (firmware version
10.04.120_10.0.91). For each of these files, a short explanation about its purpose is given.

**Note**: Although not exactly the same, our emulation got inspired by 
[Emulating, Debugging and Exploiting Netgear R6700v3 *cicled* Binary](../README.md#references).
### circled.patch.py
The purpose of the first file (`firmware/circled.patch.py`) is to apply a simple **patch** to the
target binary *circled*. The patch removes the invocation of a function (by replacing 
`0xc7a0: bl #0xc6a4` with `0xc7a0: mov r0, #0`) that prohibits the usage of the environment variable
`LD_PRELOAD` (used as a sort of **anti-debugging** measure). As will be explained below, we use the
well-known `LD_PRELOAD` trick to hook selected invocations of shared library functions (e.g. to
emulate NVRAM peripherals).
### libnvram.so
The target binary *circled* relies on the presence of some **NVRAM peripherals**. We simulate these
by preloading (using the `LD_PRELOAD` environment variable) the binary with the open-source library
[libnvram](https://github.com/firmadyne/libnvram). The library emulates the behavior of NVRAM
peripherals by storing key-value pairs into a `tmpfs` mounted at `/firmadyne/libnvram/`. The file
`firmware/bins/libnvram.so` is a pre-compiled version of the library.
### libcircled.so
`firmware/bins/libcircled.so` cross-compiled from `libcircled/circled.c`
- hook
    - (fgets) only for debugging
    - system
        - Download circleinfo.txt from http://127.0.0.1:5000/circleinfo.txt instead of original server
        - Download database.bin from http://127.0.0.1:5000/database.bin instead of original server
### circled.sh
`firmware/circled.sh`
- Setup NAND/NVRAM emulator
- (Setup NVRAM emulator)
- (Mount NAND media (why?))
- command line argument `-gdb`
- run preloaded target binary with or without gdbserver
- clean up
### circled.server.py
`server/circled.server.py`
----------------------------------------------------------------------------------------------------
[Back-to-Top](./2_emulation.md#table-of-contents)