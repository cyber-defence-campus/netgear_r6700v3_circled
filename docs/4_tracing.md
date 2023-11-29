# Table of Contents
1. [Setup](./1_setup.md)
2. [Emulation](./2_emulation.md)
3. [Vulnerability CVE-2022-27646](./3_vulnerability.md)
4. [Tracing](./4_tracing.md#tracing)
   1. [Setup](./4_tracing.md#setup)
      1. [GDB Commands Script](./4_tracing.md#gdb-commands-script)
      2. [Init YAML File](./4_tracing.md#init-yaml-file)
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

<figure align="center">
  <img src="../images/Morion_Overview.svg" alt="Morion Overview"/>
  <figcaption>
    Fig. 1: Morion Overview - Showing the two main phases of Morion, tracing and symbolic execution
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
will be stored. As explained below in section [Init YAML File](./4_tracing.md#init-yaml-file), the
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
### Init YAML File
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
parameter `mode`. This parameter can be used to distinguish multiple hooking implementations that
will be executed instead of the actual function's assembly instructions.
[Morion](https://github.com/pdamian/morion) currently implements (only) a handful of hooks for
common _libc_ functions, with supported modes of `skip`, `model` or `taint` (TODO: Add reference).
More details regarding hooking during trace collection can be found in section
[How Hooking Works](./4_tracing.md#how-hooking-works) below.
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
### Loading the Trace File
As seen above, the file `circled.yaml` (initially a copy of
[circled.init.yaml](../morion/circled.init.yaml)) may define concrete **register**
(`states:entry:regs:`) and/or **memory** (`states:entry:mems:`) values, which are set (using GDB)
before starting the actual tracing process:
```
[...]
[2023-11-28 08:56:32] [INFO] Start loading trace file 'circled.yaml'...
[2023-11-28 08:56:32] [DEBG] Regs:
[2023-11-28 08:56:32] [DEBG] Mems:
[2023-11-28 08:56:32] [DEBG] 	0x000120f8 = 0x25 %   # Setting a format string that will be accessed within the trace
[2023-11-28 08:56:32] [DEBG] 	0x000120f9 = 0x73 s
[2023-11-28 08:56:32] [DEBG] 	0x000120fa = 0x20  
[2023-11-28 08:56:32] [DEBG] 	0x000120fb = 0x25 %
[2023-11-28 08:56:32] [DEBG] 	0x000120fc = 0x73 s
[2023-11-28 08:56:32] [DEBG] 	0x000120fd = 0x00
```
Also, the **hooks** defined in `circled.yaml` are applied (using GDB), so that they take effect
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

The collected information (instructions and initial values) is stored in the `circled.yaml` file,
i.e. the file is updated as shown below:
```
[...]
instructions:
- ['0x0000cfc0', 64 37 65 e5, 'strb r3, [r5, #-0x764]!', '']
- ['0x0000cfc4', 64 32 9f e5, 'ldr r3, [pc, #0x264]', '']
[...]
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
The file `circled.yaml` serves as input for subsequent symbolic execution runs (see also
[Symbolic Execution](./5_symbex.md)).
### How Hooking Works
Hooking allows a specified **sequence of assembly instructions** (e.g. corresponding to a called
function) not to be added to the trace. In consequence, these instructions will later on not be 
executed by the symbolic execution engine and have therefore no effect on the symbolic state.
Typically, this is required to address **scalability** issues of symbolic execution or to abstract
away **environment interactions** (e.g. 3rd party libraries, inter-process communication, Kernel,
device drivers, coprocessors, etc.).
#### Mode: Skip
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
[2023-11-28 08:56:37] [DEBG] 0x0000d048 (00 00 53 e3): cmp r3, #0                                            #
[...]
```
#### Mode: Model
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
