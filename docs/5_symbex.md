# Table of Contents
1. [Setup](./1_setup.md)
2. [Emulation](./2_emulation.md)
3. [Vulnerability CVE-2022-27646](./3_vulnerability.md)
4. [Tracing](./4_tracing.md)
5. [Symbolic Execution](./5_symbex.md)
    1. [Setup](./5_symbex.md#setup)
        1. [YAML File](./5_symbex.md#yaml-file)
    2. [Run](./5_symbex.md#run)
    3. [Discussion](./5_symbex.md#discussion)
6. [Exploitation](./6_exploitation.md)
# Symbolic Execution
## TODO
This parameter is used to distinguish multiple symbolic hooking implementations (see
[Symbolic Execution](./5_symbex.md)) that will be executed instead of the actual function's assembly
instructions.

[Morion](https://github.com/pdamian/morion) currently implements (only) a handful of hooks for
common _libc_ functions, with supported modes of `skip`, `model` or `taint` (TODO: Add reference).
## Setup
### YAML File
#### Hooks
- parameter `mode`
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
## Run
Use the following step to **symbolically execute** a previously collected trace from a concrete
execution run of binary _circled_:

1. Use _morion_ to execute the collected trace symbolically:
    - System: [Host (morion)](./1_setup.md)
    - Command:
        ```
        cd morion/;             # Ensure to be within the correct directory
        morion -h;              # Optionally show usage help
        morion circled.yaml;    # Execute program trace symbolically
        ```

Remember that if you followed along the instructions in section [Tracing](./4_tracing.md), the trace
was collected while the vulnerable binary processed a sample payload leading to a
**crasher/segfault** (as might have been identified by a fuzzer).
### Analysis Modules
[Morion](https://github.com/pdamian/morion) implements different analysis modules that are based on
symbolic execution. The chosen design attempts to make [Morion](https://github.com/pdamian/morion)
easily extendable with new modules. The currently implemented ones are summarized in the table
below:

| Module                  | Description |
|-------------------------|-------------|
| morion                  | Perform symbolic execution on a binary's program trace. |
| morion_backward_slicer  | Symbolically execute a program trace for backward slicing. The analysis identifies backward slices for a specified register or memory address. |
| morion_branch_analyzer  | Symbolically execute a program trace for branch analysis. The analysis identifies multi-way branches along the trace and outputs concrete values of how to reach the non-taken branch. A specific branch is only evaluated once. |
| morion_path_analyzer    | Symbolically execute a program trace for path analysis. The analysis identifies unique paths along the trace and outputs concrete values of how to reach these paths. A path consists of a sequence of multi-way branches. The last multi-way branch in each outputted path is non- taken in the concrete execution of the trace. |
| morion_memory_hijacker  | Symbolically execute a program trace to identify potential memory hijacks. A memory hijack corresponds to the target of a memory read or write operation being (partly) symbolic. |
| morion_control_hijacker | Symbolically execute a program trace to identify potential control flow hijacks. A control flow hijack corresponds to registers, influencing the control flow (such as PC), becoming (partly) symbolic. |
| morion_rop_generator    | Symbolically execute a program trace to generate a ROP chain. |
| morion_pwndbg           | Use _morion_ together with the GDB-plugin _pwndbg_. |

## Discussion
In section [Exploitation](./6_exploitation.md) we will see how symbolic execution might help us to
decide whether the crasher might be exploited or not, i.e. corresponds to an actual security
vulnerability or just an annoying bug. We will also see, how symbolic execution can quickly give us
a first high-level intuition about what capabilities (e.g. arbitrary read/write, control-flow
hijacking, etc.) one might gain with the underlying issue. Also, we will show how symbolic execution
might help us during the process of generating a working exploit for the targeted vulnerability
(CVE-2022-27646).
### Loading the Trace File
```
[2023-11-30 12:47:34] [INFO] Start loading file 'circled.yaml'...
[2023-11-30 12:47:37] [DEBG] Concrete Regs:
[2023-11-30 12:47:37] [DEBG] 	n=0x0
[2023-11-30 12:47:37] [DEBG] 	r0=0x21ae0
[2023-11-30 12:47:37] [DEBG] 	r1=0x1
[2023-11-30 12:47:37] [DEBG] 	r10=0xbeffbd04
[2023-11-30 12:47:37] [DEBG] 	r11=0xbeffc504
[2023-11-30 12:47:37] [DEBG] 	r2=0x258
[2023-11-30 12:47:37] [DEBG] 	r3=0x0
[2023-11-30 12:47:37] [DEBG] 	r4=0x1b850
[2023-11-30 12:47:37] [DEBG] 	r5=0xbeffc868
[2023-11-30 12:47:37] [DEBG] 	r6=0xbeffc704
[2023-11-30 12:47:37] [DEBG] 	r7=0xbeffc604
[2023-11-30 12:47:37] [DEBG] 	r8=0x21ae0
[2023-11-30 12:47:37] [DEBG] 	r9=0xffff68a8
[2023-11-30 12:47:37] [DEBG] 	sp=0xbeffb870
[2023-11-30 12:47:37] [DEBG] 	v=0x0
[2023-11-30 12:47:37] [DEBG] 	z=0x0
[2023-11-30 12:47:37] [DEBG] Concrete Mems:
[2023-11-30 12:47:37] [DEBG] 	0x0000d230=0xbc  
[2023-11-30 12:47:37] [DEBG] 	0x0000d231=0x6a j
[2023-11-30 12:47:37] [DEBG] 	0x0000d232=0xff  
[2023-11-30 12:47:37] [DEBG] 	0x0000d233=0xff  
[...] 
[2023-11-30 12:47:37] [DEBG] 	0x000120f8=0x25 %
[2023-11-30 12:47:37] [DEBG] 	0x000120f9=0x73 s
[2023-11-30 12:47:37] [DEBG] 	0x000120fa=0x20  
[2023-11-30 12:47:37] [DEBG] 	0x000120fb=0x25 %
[2023-11-30 12:47:37] [DEBG] 	0x000120fc=0x73 s
[2023-11-30 12:47:37] [DEBG] 	0x000120fd=0x00  
[...]
[2023-11-30 12:47:37] [DEBG] 	0xbeffc104=0x00  
[2023-11-30 12:47:37] [DEBG] 	0xbeffc86c=0x41 A
[2023-11-30 12:47:37] [DEBG] 	0xbeffc86d=0x41 A
[...]
[2023-11-30 12:47:37] [DEBG] 	0xbeffc88e=0x41 A
[2023-11-30 12:47:37] [DEBG] 	0xbeffc88f=0x41 A
[2023-11-30 12:47:37] [DEBG] Symbolic Regs:
[2023-11-30 12:47:37] [DEBG] Symbolic Mems:
[2023-11-30 12:47:37] [DEBG] Hooks:
[2023-11-30 12:47:37] [DEBG] 	0x0000cfe0: 'libc:fgets (on=entry, mode=model)'
[2023-11-30 12:47:37] [DEBG] 	0x0000cfe4: 'libc:fgets (on=leave, mode=model)'
[2023-11-30 12:47:37] [DEBG] 	0x0000d094: 'libc:fgets (on=entry, mode=model)'
[2023-11-30 12:47:37] [DEBG] 	0x0000d098: 'libc:fgets (on=leave, mode=model)'
[2023-11-30 12:47:37] [DEBG] 	0x0000cffc: 'libc:sscanf (on=entry, mode=model)'
[2023-11-30 12:47:37] [DEBG] 	0x0000d000: 'libc:sscanf (on=leave, mode=model)'
[2023-11-30 12:47:37] [INFO] ... finished loading file 'circled.yaml'.
```
### How Hooking Works
```
[2023-11-30 12:47:37] [INFO] Start symbolic execution...
[2023-11-30 12:47:37] [DEBG] 0x0000cfc0 (64 37 65 e5): strb r3, [r5, #-0x764]! #
[...]
[2023-11-30 12:47:37] [DEBG] 0x0000cfdc (05 00 a0 e1): mov r0, r5              #
[2023-11-30 12:47:37] [DEBG] --> Hook: 'libc:fgets (on=entry, mode=model)'
[2023-11-30 12:47:37] [DEBG]           'char *fgets(char *restrict s, int n, FILE *restrict stream);'
[2023-11-30 12:47:37] [DEBG] 	 s = 0xbeffc104
[2023-11-30 12:47:37] [DEBG] 	 n = 1024
[2023-11-30 12:47:37] [DEBG] 	 stream = 0x00021ae0
[2023-11-30 12:47:37] [DEBG]     ---
[2023-11-30 12:47:37] [DEBG] 0x0000cfe0 (06 d0 ff ea): b #0x1000               # // Hook: libc:fgets (on=entry, mode=model)
[2023-11-30 12:47:37] [DEBG] 0x00001000 (04 01 0c e3): movw r0, #0xc104        # // Hook: libc:fgets (on=leave, mode=model)
[2023-11-30 12:47:37] [DEBG] 0x00001004 (ff 0e 4b e3): movt r0, #0xbeff        # // Hook: libc:fgets (on=leave, mode=model)
[2023-11-30 12:47:37] [DEBG] 0x00001008 (41 10 a0 e3): mov r1, #0x41           # // Hook: libc:fgets (on=leave, mode=model)
[2023-11-30 12:47:37] [DEBG] 0x0000100c (00 10 40 e3): movt r1, #0             # // Hook: libc:fgets (on=leave, mode=model)
[2023-11-30 12:47:37] [DEBG] 0x00001010 (00 10 c0 e5): strb r1, [r0]           # // Hook: libc:fgets (on=leave, mode=model)
[...]
[2023-11-30 12:47:37] [DEBG] 0x00005fe0 (58 10 a0 e3): mov r1, #0x58           # // Hook: libc:fgets (on=leave, mode=model)
[2023-11-30 12:47:37] [DEBG] 0x00005fe4 (00 10 40 e3): movt r1, #0             # // Hook: libc:fgets (on=leave, mode=model)
[2023-11-30 12:47:37] [DEBG] 0x00005fe8 (00 10 c0 e5): strb r1, [r0]           # // Hook: libc:fgets (on=leave, mode=model)
[2023-11-30 12:47:37] [DEBG] 0x00005fec (03 05 0c e3): movw r0, #0xc503        # // Hook: libc:fgets (on=leave, mode=model)
[2023-11-30 12:47:37] [DEBG] 0x00005ff0 (ff 0e 4b e3): movt r0, #0xbeff        # // Hook: libc:fgets (on=leave, mode=model)
[2023-11-30 12:47:37] [DEBG] 0x00005ff4 (00 10 a0 e3): mov r1, #0              # // Hook: libc:fgets (on=leave, mode=model)
[2023-11-30 12:47:37] [DEBG] 0x00005ff8 (00 10 40 e3): movt r1, #0             # // Hook: libc:fgets (on=leave, mode=model)
[2023-11-30 12:47:37] [DEBG] 0x00005ffc (00 10 c0 e5): strb r1, [r0]           # // Hook: libc:fgets (on=leave, mode=model)
[2023-11-30 12:47:37] [DEBG] 0x00006000 (04 01 0c e3): movw r0, #0xc104        # // Hook: libc:fgets (on=leave, mode=model)
[2023-11-30 12:47:37] [DEBG] 0x00006004 (ff 0e 4b e3): movt r0, #0xbeff        # // Hook: libc:fgets (on=leave, mode=model)
[2023-11-30 12:47:37] [DEBG] 0x00006008 (f5 1b 00 ea): b #0xcfe4               # // Hook: libc:fgets (on=leave, mode=model)
[2023-11-30 12:47:37] [DEBG] 	 s = 0xbeffc104
[2023-11-30 12:47:37] [DEBG] 	*s = 'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA X'
[2023-11-30 12:47:37] [DEBG] 	0xbeffc104 = $$
[2023-11-30 12:47:37] [DEBG] 	...
[2023-11-30 12:47:37] [DEBG] 	0xbeffc502 = $$
[2023-11-30 12:47:37] [DEBG]     ---
[2023-11-30 12:47:37] [DEBG] <-- Hook: 'libc:fgets (on=leave, mode=model)'
[2023-11-30 12:47:37] [DEBG] 0x0000cfe4 (00 00 50 e3): cmp r0, #0              #
[...]
[2023-11-30 12:47:37] [DEBG] 0x0000cf20 (03 db 8d e2): add sp, sp, #0xc00      #
[2023-11-30 12:47:37] [ERRO] Not terminated at a stop address: pc=0x41414140
[2023-11-30 12:47:37] [DEBG] 0x0000cf24 (f0 8f bd e8): pop {r4, r5, r6, r7, r8, sb, sl, fp, pc}#
[2023-11-30 12:47:37] [INFO] ... finished symbolic execution (pc=0x41414140).
```
### Analyzing Symbolic State
```
[...]
[2023-11-30 12:47:37] [INFO] Start analyzing symbolic state...
[2023-11-30 12:47:37] [INFO] Symbolic Regs:
[2023-11-30 12:47:38] [INFO] 	pc=$$$$$$$$
[2023-11-30 12:47:38] [INFO] 	r10=$$$$$$$$
[2023-11-30 12:47:38] [INFO] 	r11=$$$$$$$$
[2023-11-30 12:47:38] [INFO] 	r4=$$$$$$$$
[2023-11-30 12:47:38] [INFO] 	r5=$$$$$$$$
[2023-11-30 12:47:39] [INFO] 	r6=$$$$$$$$
[2023-11-30 12:47:39] [INFO] 	r7=$$$$$$$$
[2023-11-30 12:47:39] [INFO] 	r8=$$$$$$$$
[2023-11-30 12:47:40] [INFO] 	r9=$$$$$$$$
[2023-11-30 12:47:40] [INFO] Symbolic Mems:
[2023-11-30 12:48:39] [INFO] 	0xbeffc104=$$
[2023-11-30 12:48:39] [INFO] 	...
[2023-11-30 12:48:39] [INFO] 	0xbeffc502=$$
[2023-11-30 12:48:39] [INFO] 	0xbeffc604=$$
[2023-11-30 12:48:39] [INFO] 	0xbeffc704=$$
[2023-11-30 12:48:39] [INFO] 	...
[2023-11-30 12:48:39] [INFO] 	0xbeffcb00=$$
[2023-11-30 12:48:39] [INFO] ... finished analyzing symbolic state.
[2023-11-30 12:48:39] [INFO] Start storing file 'circled.yaml'...
[2023-11-30 12:48:41] [INFO] ... finished storing file 'circled.yaml'.
```