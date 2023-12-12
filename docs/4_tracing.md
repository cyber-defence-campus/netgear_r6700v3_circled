# Table of Contents
1. [Setup](./1_setup.md)
2. [Emulation](./2_emulation.md)
3. [Vulnerability CVE-2022-27646](./3_vulnerability.md)
4. [Tracing](./4_tracing.md#tracing)
    1. [Setup](./4_tracing.md#setup)
        1. [GDB Commands Script](./4_tracing.md#gdb-commands-script)
        2. [YAML File](./4_tracing.md#yaml-file)
    2. [Run](./4_tracing.md#run)
    3. [Discussion](./4_tracing.md#discussion)
        1. [Loading the Trace File](./4_tracing.md#loading-the-trace-file)
        2. [Collecting the Trace](./4_tracing.md#collecting-the-trace)
        3. [How Hooking Works](./4_tracing.md#how-hooking-works)
5. [Symbolic Execution](./5_symbex.md)
6. [Exploitation](./6_exploitation.md)
# Tracing
In the following, we document how to collect a **concrete execution trace** of our target, a
known vulnerable ARMv7 binary named *circled* (see
[Vulnerability CVE-2022-27646](./3_vulnerability.md)). The trace is collected in a cross-platform
remote setup, i.e. despite our host system being x86-based, the target runs on an (emulated)
ARMv7-based device (see [Emulation](./2_emulation.md)). The collected trace may later be used for
different symbolic execution runs/analyses (see [Symbolic Execution](./5_symbex.md)), which can be
done offline, for instance on a more powerful machine.

<figure>
  <img src="../images/Morion_Overview.svg" alt="Morion Overview"/>
  <figcaption>
    Fig. 1: Morion Overview - Showing Morion's two operation modes tracing and symbolic execution.
  </figcaption>
</figure>

## Setup
Before collecting concrete execution traces of the target binary _circled_, the following files need
to be set up.
### GDB Commands Script
The file [circled.trace.gdb](../morion/circled.trace.gdb) is a _GNU Project Debugger (GDB)_ commands
script. As shown in the figure above, [Morion](https://github.com/pdamian/morion) uses GDB to
interact with its target during the process of tracing. The script contains GDB commands that bring
the target to the point from which tracing should start (e.g. to follow along and break the relevant
thread when dealing with multi-threaded binaries, as it is the case with _circled_). As show below,
the trace can then be collected with the command `morion_trace`, a custom GDB command implemented by
[Morion](https://github.com/pdamian/morion) (usage:
`morion_trace [debug] <trace_file_yaml:str> <stop_addr:int> [<stop_addr:int> [...]]`).
Alongside some stop addresses, `morion_trace` expects as argument a YAML file, into which the trace
will be stored. As explained below in section [YAML File](./4_tracing.md#yaml-file), the
inputted YAML file can hold additional information that steers how the trace will be collected (e.g.
by hooking certain functions).
```
[...]
# Addresses
[...]
set $before_vulnerability     = 0xcfc0
[...]

# Break before vulnerability
break *$before_vulnerability
continue

# Trace till return of function updating_database
morion_trace debug circled.yaml 0xf1a4
[...]
```
As can be seen in the code excerpt above, the trace we intend to collect should start/stop at 
addresses `0xcfc0` and `0xf1a4`, respectively. Start and stop addresses of the trace need to be
selected adequately for the intended purpose. In our specific case where we intend to generate an
exploit for CVE-2022-27646 (see also [Exploitation](./6_exploitation.md)), which means that the
trace should include both the points where attacker-controllable inputs are introduced and where
these inputs lead to a potential vulnerability (e.g. the point the binary is crashing due to a
memory violation condition - as for instance found by a fuzzing campaign).
### YAML File
Next, the file [circled.init.yaml](../morion/circled.init.yaml) needs to be defined. It typically
includes information about the trace's entry state (`states:entry:`), as well as about functions
that should be hooked (`hooks:`).
#### States
Typically, the [circled.init.yaml](../morion/circled.init.yaml) file first defines information about
the trace's entry state (`states:entry:`). More specifically, we define concrete register and/or
memory values, that [Morion](https://github.com/pdamian/morion) - respectively _GDB_ - will set
before collecting the trace (see also
[Loading the Trace File](./4_tracing.md#loading-the-trace-file)).
```
[...]
states:
  entry:
    regs:
    mems:
      '0x000120f8': ['0x25']  # '%'
      '0x000120f9': ['0x73']  # 's'
      '0x000120fa': ['0x20']  # ' '
      '0x000120fb': ['0x25']  # '%'
      '0x000120fc': ['0x73']  # 's'
      '0x000120fd': ['0x00']  #
[...]
```
In the example of binary _circled_ above, we manually set a format string `%s %s`. Within the trace
that we are about to collect, this format string is solely used by the function `sscanf` - a
function that we hook (see next section on Hooks) and in consequence, do not trace all of its
assembly instructions. Due to skipping the function's instructions,
[Morion](https://github.com/pdamian/morion) does not record all memory locations accessed by it,
which is why we need to add them manually.

Here and in other places, [Morion](https://github.com/pdamian/morion) is designed with the intention
to give an analyst extensive configuration flexibilities, so that cases can be handled where the
tool does not (yet) implement full automation. In the example of `sscanf`, a future hooking
implementation could improve on this, so that the format string is automatically added to the
accessed memory pool.

The general format to configure the **entry state** looks like this:
```
states:
  entry:
    regs:
      'r0': ['0x00', '$$']
    mems:
      '0x00000000': ['0x00', '$$']
```
Beside setting concrete values, like `0x00` in the example above, we might also mark certain
registers and/or memory locations as being symbolic (indicated by the specifier `$$`). The symbolic
values have not yet any effect during tracing, but will be central during symbolic execution (see 
[Symbolic Execution](./5_symbex.md)).
#### Hooks
Next, the [circled.init.yaml](../morion/circled.init.yaml) file typically defines information about
hooks (`hooks:`). A hook is a **sequence of consecutive assembly instructions** (from an `entry` to
a `leave` address) that will not be recorded in the trace. As a consequence, these instructions will
later not be executed by the symbolic execution engine, which takes the recorded trace as input.
Most of the time, hooks will correspond to function calls (such as
`0x0000d040 (73 f1 ff eb): bl #0x9614 <fclose@plt>`), where the effective symbolic execution of all
included assembly instructions does either not scale, is irrelevant for the intended purpose (e.g.
exploit generation) or the function has well-known semantics that can be mimicked by a semantic
function model (TODO: Add reference).
```
hooks:
  lib:
    func_hook:
    - {entry: '0xd040', leave: '0xd044', mode: 'skip'}   # fclose@plt
    [...]
    - {entry: '0xc9c4', leave: '0xc9c8', mode: 'skip'}   # free@plt
  libc:
    fgets:
    - {entry: '0xcfe0', leave: '0xcfe4', mode: 'model'}  # fgets@plt
    - {entry: '0xd094', leave: '0xd098', mode: 'model'}  # fgets@plt
    sscanf:
    - {entry: '0xcffc', leave: '0xd000', mode: 'model'}  # sscanf@plt
[...]
```
As can be seen in the code excerpt above, hooks include - beside `entry` and `leave` addresses - a
parameter `mode`. This is only relevant during symbolic execution and will therefore be explained
in section [Symbolic Execution](./5_symbex.md). More details regarding hooking during trace
collection can be found in section [How Hooking Works](./4_tracing.md#how-hooking-works) below.

Note: As mentioned before, [Morion](https://github.com/pdamian/morion) generally intends to favor
configuration flexibility over full automation. Due to this, `leave` addresses of hooks (currently)
need to be configured manually, since in general, the return address of a function is hard to
determine (e.g. tail calls).
## Run
Use the following steps to create a **trace** of the binary _circled_, while it is targeted with a
_proof-of-vulnerability (PoV)_ payload (as for instance being identified by a fuzzer):
1. Start a HTTP server, delivering PoV payloads:
   - System: [Guest](./1_setup.md)
   - Command:
      ```
      python3 server/circled.server.py --payload "pov"
      ```
2. Emulate the binary _circled_ with GDB attached (and therefore not using ASRL):
   - System: [Guest (chroot)](./1_setup.md)
   - Command:
     ```
     /circled.sh --gdb
3. Collect an execution trace of the binary _circled_:
   - System: [Host (morion)](./1_setup.md)
   - Command:
     ```
     cd morion/;                              # Ensure to be within the correct directory
     cp circled.init.yaml circled.yaml;       # Start with a fresh circled.yaml file
     gdb-multiarch -q -x circled.trace.gdb;   # Use GDB for cross-platform remote trace collection
     ```
## Discussion
In the following, we discuss some aspects of the tracing process as implemented by
[Morion](https://github.com/pdamian/morion).
### Loading the Trace File
As seen above, the file `circled.yaml` (initially a copy of
[circled.init.yaml](../morion/circled.init.yaml)) may define concrete **register**
(`states:entry:regs:`) and/or **memory** (`states:entry:mems:`) values, which are set (using _GDB_)
before starting the actual tracing process:
```
[...]
[2023-11-28 08:56:32] [INFO] Start loading trace file 'circled.yaml'...
[2023-11-28 08:56:32] [DEBG] Regs:
[2023-11-28 08:56:32] [DEBG] Mems:
[2023-11-28 08:56:32] [DEBG] 	0x000120f8 = 0x25 %
[2023-11-28 08:56:32] [DEBG] 	0x000120f9 = 0x73 s
[2023-11-28 08:56:32] [DEBG] 	0x000120fa = 0x20  
[2023-11-28 08:56:32] [DEBG] 	0x000120fb = 0x25 %
[2023-11-28 08:56:32] [DEBG] 	0x000120fc = 0x73 s
[2023-11-28 08:56:32] [DEBG] 	0x000120fd = 0x00
```
Also, the **hooks** defined in `circled.yaml` are applied (using _GDB_), so that they take effect
(see also [How Hooking Works](./4_tracing.md#how-hooking-works)) when collecting the concrete
execution trace:
```
[2023-11-28 08:56:32] [DEBG] Hooks:
[2023-11-28 08:56:32] [DEBG] 	0x0000d040 'lib:func_hook (on=entry, mode=skip)'
[2023-11-28 08:56:32] [DEBG] 	0x0000d044 'lib:func_hook (on=leave, mode=skip)'
[...]
[2023-11-28 08:56:32] [DEBG] 	0x0000c9c4 'lib:func_hook (on=entry, mode=skip)'
[2023-11-28 08:56:32] [DEBG] 	0x0000c9c8 'lib:func_hook (on=leave, mode=skip)'
[2023-11-28 08:56:32] [DEBG] 	0x0000cfe0 'libc:fgets (on=entry, mode=model)'
[2023-11-28 08:56:32] [DEBG] 	0x0000cfe4 'libc:fgets (on=leave, mode=model)'
[2023-11-28 08:56:32] [DEBG] 	0x0000d094 'libc:fgets (on=entry, mode=model)'
[2023-11-28 08:56:32] [DEBG] 	0x0000d098 'libc:fgets (on=leave, mode=model)'
[2023-11-28 08:56:32] [DEBG] 	0x0000cffc 'libc:sscanf (on=entry, mode=model)'
[2023-11-28 08:56:32] [DEBG] 	0x0000d000 'libc:sscanf (on=leave, mode=model)'
[...]
[2023-11-28 08:56:32] [INFO] ... finished loading trace file 'circled.yaml'.
```
Once this is done, the actual tracing can start.
### Collecting the Trace
Collecting a trace includes the recording of the following pieces of information:
- Executed assembly **instructions** (e.g. `0x0000cfc0 (64 37 65 e5): strb r3, [r5, #-0x764]!`)
- **Initial values** of all accessed registers and memory locations (e.g. `r3 = 0x0`,
  `r5 = 0xbeffc868` or `0xbeffc104 = 0x00`)
```
[2023-11-28 08:56:32] [INFO] Start tracing...
[2023-11-28 08:56:32] [DEBG] 0x0000cfc0 (64 37 65 e5): strb r3, [r5, #-0x764]!   # store 1st assembly instruction
[2023-11-28 08:56:32] [DEBG] Regs:
[2023-11-28 08:56:32] [DEBG] 	r3 = 0x0                                         # store value of accessed register r3 (initial access)
[2023-11-28 08:56:32] [DEBG] 	r5 = 0xbeffc868                                  # store value of accessed register r5 (initial access)
[2023-11-28 08:56:32] [DEBG] Mems:
[2023-11-28 08:56:32] [DEBG] 	0xbeffc104 = 0x00                                # store value of memory 0xbeffc104 (initial access)
[2023-11-28 08:56:32] [DEBG] 0x0000cfc4 (64 32 9f e5): ldr r3, [pc, #0x264]      # store 2nd assembly instruction
[2023-11-28 08:56:32] [DEBG] Regs:                                               # ignore value of accessed register r3 (stored before)
[2023-11-28 08:56:32] [DEBG] Mems:
[2023-11-28 08:56:32] [DEBG] 	0x0000d230 = 0xbc                                # store value of memory 0x0000d230 (initial access)
[2023-11-28 08:56:32] [DEBG] 	0x0000d231 = 0x6a j                              # store value of memory 0x0000d231 (initial access)
[2023-11-28 08:56:32] [DEBG] 	0x0000d232 = 0xff                                # store value of memory 0x0000d232 (initial access)
[2023-11-28 08:56:32] [DEBG] 	0x0000d233 = 0xff                                # store value of memory 0x0000d233 (initial access)
[...]
```
The initial values of register (`states:entry:regs:`) and memory locations (`states:entry:mems:`)
are stored, so that they can later be set in the symbolic context. This is needed so that the
symbolic execution engine uses the correct concrete values.

The collected information (instructions and initial values) is stored in the file `circled.yaml`,
i.e. the file is updated as shown in the next code excerpt. The file `circled.yaml` serves as input
for subsequent symbolic execution runs (see also [Symbolic Execution](./5_symbex.md)).
```
[...]
instructions:
- ['0x0000cfc0', 64 37 65 e5, 'strb r3, [r5, #-0x764]!', '']
- ['0x0000cfc4', 64 32 9f e5, 'ldr r3, [pc, #0x264]', '']
[...]
- ['0x0000cf20', 03 db 8d e2, 'add sp, sp, #0xc00', '']
- ['0x0000cf24', f0 8f bd e8, 'pop {r4, r5, r6, r7, r8, sb, sl, fp, pc}', '']
states:
  entry:
    addr: '0x0000cfc0'
    regs:
      [...]
      r3: ['0x00000000']
      [...]
      r5: ['0xbeffc868']
      [...]
    mems:
      '0x0000d230': ['0xbc']
      '0x0000d231': ['0x6a']
      '0x0000d232': ['0xff']
      '0x0000d233': ['0xff']
      [...]
      '0x000120f8': ['0x25']  # '%'
      '0x000120f9': ['0x73']  # 's'
      '0x000120fa': ['0x20']  # ' '
      '0x000120fb': ['0x25']  # '%'
      '0x000120fc': ['0x73']  # 's'
      '0x000120fd': ['0x00']  #
      [...]
      '0xbeffc104': ['0x00']
      [...]
```

If we look at the end of the tracing process's debug output, we can observe that the trace did not
end at our configured stop address `0xf1a4`, but at address `0xcf24`:
```
[2023-11-28 08:56:41] [DEBG] 0x0000cf20 (03 db 8d e2): add sp, sp, #0xc00
[2023-11-28 08:56:41] [DEBG] Regs:
[2023-11-28 08:56:41] [DEBG] Mems:
[2023-11-28 08:56:41] [DEBG] 0x0000cf24 (f0 8f bd e8): pop {r4, r5, r6, r7, r8, sb, sl, fp, pc}
[2023-11-28 08:56:41] [DEBG] Regs:
[2023-11-28 08:56:41] [DEBG] Mems:
[2023-11-28 08:56:41] [DEBG] 	0xbeffc86c = 0x41 A
[2023-11-28 08:56:41] [DEBG] 	0xbeffc86d = 0x41 A
[...]
[2023-11-28 08:56:41] [DEBG] 	0xbeffc88a = 0x41 A
[2023-11-28 08:56:41] [DEBG] 	0xbeffc88b = 0x41 A
[2023-11-28 08:56:41] [ERRO] 	Failed to execute instruction at address 0x0000cf24: 'Remote connection closed'
[2023-11-28 08:56:41] [INFO] ... finished tracing (pc=0x0000cf24).
[2023-11-28 08:56:41] [INFO] Start storing trace file 'circled.yaml'...
[2023-11-28 08:56:43] [INFO] ... finished storing trace file 'circled.yaml'.
```
This is due to the fact, that our target binary crashed before reaching the intended stop address.
More specifically, and as we will see in greater detail later on, the instruction
`0x0000cf24 (f0 8f bd e8): pop {r4, r5, r6, r7, r8, sb, sl, fp, pc}` tried to pop a value from the
stack that led to an invalid program counter (`pc` register), and in consequence, resulted in a
**segmentation fault** (segfault). We will learn later on how [symbolic execution](./5_symbex.md)
can help us to decide whether this situation is [exploitable](./6_exploitation.md) or not, and if
so, how we can do it.
### How Hooking Works
As mentioned before, hooking allows a specified **sequence of assembly instructions** (e.g.
corresponding to a called function) not to be added to the trace. In consequence, these instructions
will later on not be executed by the symbolic execution engine and have therefore no effect on the
symbolic state. Typically, this is required to address **scalability** issues of symbolic execution
or to abstract away **environmental interactions** (e.g. with 3rd party libraries, inter-process
communications, Kernel, device drivers, coprocessors, etc.).

Below, we discuss how the hooking of two concrete _libc_ functions look like, while
[Morion](https://github.com/pdamian/morion) collects a trace.
#### Abstract Function Hook (Example libc:fclose)
The [circled.init.yaml](../morion/circled.init.yaml) file defines a hook for entry and leave 
addresses `0xd040` and `0xd044`, respectively. The corresponding entry is located under the key
`hooks:lib:func_hook:`, which means that an abstract hooking mechanism for functions should be used
(see
[morion/tracing/gdb/hooking/lib](https://github.com/pdamian/morion/blob/main/morion/tracing/gdb/hooking/lib.py)
for implementation details), as compared to a specific one, which will be the case in the second
example below. The **abstract function hooking** mechanism will skip the actual assembly
instructions of the function, and instead inject instructions that move the function's concrete 
return value to the appropriate return register(s) (`r0`/`r1` for ARMv7 architectures). This is
needed so that during symbolic execution the return register(s) hold the correct concrete value(s)
and the symbolic execution proceeds in synchronization with the concrete one. 

The described behavior can be observed in [Morion](https://github.com/pdamian/morion)'s debug output
below. Instructions with addresses `0xd040`, `0x1000` - `0x1010` have been injected by
[Morion](https://github.com/pdamian/morion) to set the correct concrete return value(s) of the
function. The last injected instruction at address `0x1010` transfers control back to the
instruction at the `leave` address (`0x0000d044 (04 30 9d e5): ldr r3, [sp, #4]`).

Note: [Morion](https://github.com/pdamian/morion) also implements the concept of hooking arbitrary
sequences of assembly instructions ("`hooks:lib:inst_hook:`"), not necessarily belonging to function
calls. These are similar to the ones regarding functions, but do not inject any instructions for
setting return values.
```
[...]
[2023-11-28 08:56:37] [DEBG] 0x0000d03c (08 00 a0 e1): mov r0, r8                                            #                                                                               
[2023-11-28 08:56:37] [DEBG] Regs:
[2023-11-28 08:56:37] [DEBG] Mems:
[2023-11-28 08:56:37] [INFO] --> Hook: 'lib:func_hook (on=entry, mode=skip)'
[2023-11-28 08:56:37] [INFO]           'func_hook'
[2023-11-28 08:56:37] [DEBG] 0x0000d040 (ee cf ff ea): b #-0xc040                                            # // Hook: lib:func_hook (on=entry, mode=skip)                                  
[2023-11-28 08:56:37] [INFO]    ---
[2023-11-28 08:56:37] [DEBG] 0x00001000 (00 00 a0 e3): mov  r0, #0x0                                         # // Hook: lib:func_hook (on=leave, mode=skip)                                  
[2023-11-28 08:56:37] [DEBG] 0x00001004 (00 00 40 e3): movt r0, #0x0                                         # // Hook: lib:func_hook (on=leave, mode=skip)                                  
[2023-11-28 08:56:37] [DEBG] 0x00001008 (01 10 a0 e3): mov  r1, #0x1                                         # // Hook: lib:func_hook (on=leave, mode=skip)                                  
[2023-11-28 08:56:37] [DEBG] 0x0000100c (00 10 40 e3): movt r1, #0x0                                         # // Hook: lib:func_hook (on=leave, mode=skip)                                  
[2023-11-28 08:56:37] [DEBG] 0x00001010 (0b 30 00 ea): b #0xc034                                             # // Hook: lib:func_hook (on=leave, mode=skip)                                  
[2023-11-28 08:56:37] [INFO] <-- Hook: 'lib:func_hook (on=leave, mode=skip)'
[2023-11-28 08:56:37] [DEBG] 0x0000d044 (04 30 9d e5): ldr r3, [sp, #4]                                      #                                                                               
[2023-11-28 08:56:37] [DEBG] Regs:
[2023-11-28 08:56:37] [DEBG] Mems:
[2023-11-28 08:56:37] [DEBG] 	0xbeffb874 = 0x06  
[2023-11-28 08:56:37] [DEBG] 	0xbeffb875 = 0x00  
[2023-11-28 08:56:37] [DEBG] 	0xbeffb876 = 0x00  
[2023-11-28 08:56:37] [DEBG] 	0xbeffb877 = 0x00
[...]
```
#### Specific Function Hook (Example libc:fgets)
In general, not only function return values (as discussed in the previous section), but all
**side-effects** with respect to registers and/or memory locations need to be covered, in order for
the symbolic execution to be correct. This is why more specific function hook implementations might
be needed.

One such function, with rather simple to cover side-effects, is _fgets_ from _libc_
(synopsis: `char *fgets(char *s, int n, FILE *stream)`). The function reads a maximum of `n-1` bytes
from a file `stream` to an address given by `s` (newline or end-of-file conditions can make the
function read less bytes).
In the file [circled.init.yaml](../morion/circled.init.yaml), the hook for function `fgets` is
defined under the key `hooks:libc:fgets:`. [Morion](https://github.com/pdamian/morion) will
therefore apply the specific _fgets_ implementation as defined in file
[morion/tracing/gdb/hooking/libc](https://github.com/pdamian/morion/blob/main/morion/tracing/gdb/hooking/libc.py).

As can be seen in the output below, [Morion](https://github.com/pdamian/morion) injected
instructions (addresses `0xcfe0`, `0x1000` - `0x6008`) that move the concrete string read by
`fgets` (which actually corresponds to the PoV payload served by the HTTP server) to the appropriate
memory addresses.
```
[...]
[2023-11-28 08:56:32] [DEBG] 0x0000cfdc (05 00 a0 e1): mov r0, r5                                            #                                                                               
[2023-11-28 08:56:32] [DEBG] Regs:
[2023-11-28 08:56:32] [DEBG] 	r0 = 0x21ae0
[2023-11-28 08:56:32] [DEBG] Mems:
[2023-11-28 08:56:32] [INFO] --> Hook: 'libc:fgets (on=entry, mode=model)'
[2023-11-28 08:56:32] [INFO]           'char *fgets(char *restrict s, int n, FILE *restrict stream);'
[2023-11-28 08:56:32] [INFO] 	 s      = 0xbeffc104
[2023-11-28 08:56:32] [INFO] 	 n      = 1024
[2023-11-28 08:56:32] [INFO] 	 stream = 0x00021ae0
[2023-11-28 08:56:32] [DEBG] 0x0000cfe0 (06 d0 ff ea): b #-0xbfe0                                            # // Hook: libc:fgets (on=entry, mode=model)                                    
[2023-11-28 08:56:32] [INFO]    ---
[2023-11-28 08:56:33] [INFO] 	 s      = 0xbeffc104
[2023-11-28 08:56:33] [INFO] 	*s      = 'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA X'
[2023-11-28 08:56:33] [DEBG] 0x00001000 (04 01 0c e3): mov  r0, #0xc104                                      # // Hook: libc:fgets (on=leave, mode=model)                                    
[2023-11-28 08:56:33] [DEBG] 0x00001004 (ff 0e 4b e3): movt r0, #0xbeff                                      # // Hook: libc:fgets (on=leave, mode=model)                                    
[2023-11-28 08:56:33] [DEBG] 0x00001008 (41 10 a0 e3): mov  r1, #0x41                                        # // Hook: libc:fgets (on=leave, mode=model)                                    
[2023-11-28 08:56:33] [DEBG] 0x0000100c (00 10 40 e3): movt r1, #0x0                                         # // Hook: libc:fgets (on=leave, mode=model)                                    
[2023-11-28 08:56:33] [DEBG] 0x00001010 (00 10 c0 e5): strb r1, [r0]                                         # // Hook: libc:fgets (on=leave, mode=model)
[...]
[2023-11-28 08:56:33] [DEBG] 0x00005fec (03 05 0c e3): mov  r0, #0xc503                                      # // Hook: libc:fgets (on=leave, mode=model)                                    
[2023-11-28 08:56:33] [DEBG] 0x00005ff0 (ff 0e 4b e3): movt r0, #0xbeff                                      # // Hook: libc:fgets (on=leave, mode=model)                                    
[2023-11-28 08:56:33] [DEBG] 0x00005ff4 (00 10 a0 e3): mov  r1, #0x0                                         # // Hook: libc:fgets (on=leave, mode=model)                                    
[2023-11-28 08:56:33] [DEBG] 0x00005ff8 (00 10 40 e3): movt r1, #0x0                                         # // Hook: libc:fgets (on=leave, mode=model)                                    
[2023-11-28 08:56:33] [DEBG] 0x00005ffc (00 10 c0 e5): strb r1, [r0]                                         # // Hook: libc:fgets (on=leave, mode=model)                                    
[2023-11-28 08:56:33] [DEBG] 0x00006000 (04 01 0c e3): mov  r0, #0xc104                                      # // Hook: libc:fgets (on=leave, mode=model)                                    
[2023-11-28 08:56:33] [DEBG] 0x00006004 (ff 0e 4b e3): movt r0, #0xbeff                                      # // Hook: libc:fgets (on=leave, mode=model)                                    
[2023-11-28 08:56:33] [DEBG] 0x00006008 (f5 1b 00 ea): b #0x6fdc                                             # // Hook: libc:fgets (on=leave, mode=model)                                    
[2023-11-28 08:56:33] [INFO] <-- Hook: 'libc:fgets (on=leave, mode=model)'
[2023-11-28 08:56:33] [DEBG] 0x0000cfe4 (00 00 50 e3): cmp r0, #0                                            #  
```
The implementation of all a function's side-effects might not always be so simple as in the example 
of `fgets`. In consequence, **simplifications/abstractions** might sometimes be needed, which as a
drawback might introduce inconsistencies between the effective concrete and symbolic execution.
Depending on the intended task that you intend to solve with symbolic execution, this might or might
not be acceptable.