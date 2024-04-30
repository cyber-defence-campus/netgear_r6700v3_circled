# Table of Contents
0. [Introduction](../README.md#introduction)
1. [Setup](./1_setup.md)
2. [Emulation](./2_emulation.md)
3. [Tracing](./3_tracing.md)
4. [Symbolic Execution](./4_symbex.md#symbolic-execution)
    1. [Setup](./4_symbex.md#setup)
    2. [Run](./4_symbex.md#run)
    3. [Discussion](./4_symbex.md#discussion)
        1. [Loading the Trace File](./4_symbex.md#loading-the-trace-file)
        2. [How Hooking Works](./4_symbex.md#how-hooking-works)
        3. [Analyzing Symbolic State](./4_symbex.md#analyzing-symbolic-state)
5. [Vulnerability CVE-2022-27646](./5_vulnerability.md)
6. [Exploitation](./6_exploitation.md)
<!--TODO--------------------------------------------------------------------------------------------
- [ ] Does ARMv7 really use registers `r0` and `r1` for return values?
- [ ] Change text of links and validate them
- [ ] Refer to a page as chapter (not section)
- [ ] Review whether all addresses/values are consistent
--------------------------------------------------------------------------------------------------->
# Symbolic Execution
Chapter [Tracing](./3_tracing.md) explained how to collect a concrete execution trace of your
target, which in our specific case is the ARMv7 binary _circled_. If you followed along the given
instructions, this trace was stored in the file `circled.yaml`. As we will see below, this trace
file may then be used as input for the different **analysis modules** implemented by
[Morion](https://github.com/pdamian/morion). These analysis modules execute the collected trace
**symbolically**, which then allows for reasoning about the target's behavior by solving constraints
for specified mathematical problems. An example for such a problem might for instance be the
question of whether or not it is possible for the program counter (register `pc`) to become a
certain value, and if so, how this can be achieved (e.g. leading to a control-flow hijacking
condition).
<hr>
<figure>
  <img src="../images/Morion_Overview.svg" alt="Morion Overview"/>
  <figcaption>
    Figure 4.1: Morion Overview - Showing Morion's two operation modes tracing and symbolic 
    execution.
  </figcaption>
</figure>
<hr>

## Setup
Before running one of [Morion](https://github.com/pdamian/morion)'s symbolic analysis modules, the
collected trace file `circled.yaml` might optionally be customized. Such **customizations** could
for example be to:
- Mark (additional) register values or memory locations as being symbolic (in the entry state)
- Modify the parameter `mode` of hooked functions
- Add/remove assembly instructions to/from the trace
- Add extra inputs for analysis modules (e.g. intended ROP chains for analysis module
  `morion_rop_generator`, see e.g. chapter [Exploitation](./6_exploitation.md))

In our documented example of the binary _circled_, all relevant configurations have already been
defined in the file [circled.init.yaml](../morion/circled.init.yaml), which during tracing got
copied over to the file `circled.yaml`. Therefore, no further customizations are needed.

## Run
Use the following step to **symbolically execute** a previously collected trace from a concrete
execution run of binary _circled_:

1. Use _morion_ to execute the collected trace symbolically:
    - System: [Analysis / Host (morion)](./1_setup.md#analysis--host-system)
    - Command:
        ```
        cd morion/;             # Ensure to be within the correct directory
        morion -h;              # Optionally show usage help
        morion circled.yaml;    # Execute program trace symbolically
        ```

Remember that if you followed along the instructions in chapter [Tracing](./3_tracing.md), the trace
was collected while the vulnerable binary processed a sample payload leading to a
**crasher/segfault** (as might have been identified by a fuzzer).
### Analysis Modules
[Morion](https://github.com/pdamian/morion) implements different analysis modules that are based on
symbolic execution. The chosen design attempts to make [Morion](https://github.com/pdamian/morion)
easily **extendable** with new modules. The currently implemented ones are summarized in the table
below:

| Module                  | Description |
|-------------------------|-------------|
| morion                  | Perform symbolic execution on a binary's program trace. |
| morion_backward_slicer  | Symbolically execute a program trace for backward slicing. The analysis identifies backward slices for a specified register or memory address. |
| morion_branch_analyzer  | Symbolically execute a program trace for branch analysis. The analysis identifies multi-way branches along the trace and outputs concrete values of how to reach the non-taken branch. A specific branch is only evaluated once. |
| morion_path_analyzer    | Symbolically execute a program trace for path analysis. The analysis identifies unique paths along the trace and outputs concrete values of how to reach these paths. A path consists of a sequence of multi-way branches. The last multi-way branch in each outputted path is non- taken in the concrete execution of the trace. |
| morion_memory_hijacker  | Symbolically execute a program trace to identify potential memory hijacks. A memory hijack corresponds to the target of a memory read or write operation being (partly) symbolic. |
| morion_control_hijacker | Symbolically execute a program trace to identify potential control flow hijacks. A control flow hijack corresponds to registers, influencing the control flow (such as pc), becoming (partly) symbolic. |
| morion_rop_generator    | Symbolically execute a program trace to help generating a ROP chain. |

## Discussion
In the following, we discuss some aspects of the symbolic execution process as implemented by
[Morion](https://github.com/pdamian/morion).
### Loading the Trace File
As explained in section [Tracing: Collecting the Trace](./3_tracing.md#collecting-the-trace), beside
the executed assembly instructions, the initial **concrete values** of all registers and/or memory
locations accessed within the trace are recorded (in our specific example in the file
`circled.yaml`). Before starting the actual symbolic execution, these are used by
[Morion](https://github.com/pdamian/morion) to initialize the corresponding concrete register and/or
memory values within the context of the symbolic execution engine
(which in our case is [Triton](https://triton-library.github.io/)). This assures that the symbolic
execution of the recorded trace uses the correct concrete register and/or memory values. This
initialization of registers and/or memory locations can be observed in
[Morion](https://github.com/pdamian/morion)'s debug output:
```
[2024-04-11 10:46:19] [INFO] Start loading file 'circled.yaml'...
[2024-04-11 10:46:21] [DEBG] Regs:
[2024-04-11 10:46:21] [DEBG] 	n=0x0
[2024-04-11 10:46:21] [DEBG] 	r0=0x21ae0
[2024-04-11 10:46:21] [DEBG] 	r1=0x1
[2024-04-11 10:46:21] [DEBG] 	r10=0xbeffbcc4
[2024-04-11 10:46:21] [DEBG] 	r11=0xbeffc4c4
[2024-04-11 10:46:21] [DEBG] 	r2=0x258
[2024-04-11 10:46:21] [DEBG] 	r3=0x0
[2024-04-11 10:46:21] [DEBG] 	r4=0x1b850
[2024-04-11 10:46:21] [DEBG] 	r5=0xbeffc828
[2024-04-11 10:46:21] [DEBG] 	r6=0xbeffc6c4
[2024-04-11 10:46:21] [DEBG] 	r7=0xbeffc5c4
[2024-04-11 10:46:21] [DEBG] 	r8=0x21ae0
[2024-04-11 10:46:21] [DEBG] 	r9=0xffff68a8
[2024-04-11 10:46:21] [DEBG] 	sp=0xbeffb830
[2024-04-11 10:46:21] [DEBG] 	v=0x0
[2024-04-11 10:46:21] [DEBG] 	z=0x0
[2024-04-11 10:46:21] [DEBG] Mems:
[2024-04-11 10:46:21] [DEBG] 	0x0000d230=0xbc  
[2024-04-11 10:46:21] [DEBG] 	0x0000d231=0x6a j
[2024-04-11 10:46:21] [DEBG] 	0x0000d232=0xff  
[2024-04-11 10:46:21] [DEBG] 	0x0000d233=0xff
[...]
[2024-04-11 10:46:21] [DEBG] 	0x000120f8=0x25 %
[2024-04-11 10:46:21] [DEBG] 	0x000120f9=0x73 s
[2024-04-11 10:46:21] [DEBG] 	0x000120fa=0x20  
[2024-04-11 10:46:21] [DEBG] 	0x000120fb=0x25 %
[2024-04-11 10:46:21] [DEBG] 	0x000120fc=0x73 s
[2024-04-11 10:46:21] [DEBG] 	0x000120fd=0x00
[...]
[2024-04-11 10:46:21] [DEBG] 	0xbeffc0c4=0x00  
[2024-04-11 10:46:21] [DEBG] 	0xbeffc82c=0x41 A
[2024-04-11 10:46:21] [DEBG] 	0xbeffc82d=0x41 A
[...]
[2024-04-11 10:46:21] [DEBG] 	0xbeffc84e=0x41 A
[2024-04-11 10:46:21] [DEBG] 	0xbeffc84f=0x41 A
[...]
```
In a similar manner, registers and/or memory locations can be assigned a new **symbolic variable**,
before the actual symbolic execution of the trace begins. To for example mark the register `r0` as
being symbolic (alongside its concrete initial value of `0x21ae0`), the trace file `circled.yaml`
(respectively the file [circled.init.yaml](../morion/circled.init.yaml)) could contain an entry such
as the one shown below:
```
[...]
states:
  entry:
    regs:
      'r0': ['0x21ae0', '$$$$$$$$']   # Marking register r0 as being symbolic
      [...]
    mems:
      '0x000120f8': ['0x25', '$$'     # Marking memory location 0x120f8 as being symbolic
      [...]
[...]
```
As can be seen in the excerpt above, [Morion](https://github.com/pdamian/morion) uses the specifier
`$$` for referring to a **symbolic byte**. In the above example, where a symbolic register and a
symbolic memory location were defined, [Morion](https://github.com/pdamian/morion)'s debug output,
while loading the trace file, would look like this:
```
[...]
[2024-04-11 10:46:21] [DEBG] 	r0=0x21ae0
[2024-04-11 10:46:21] [DEBG] 	r0=$$$$$$$$
[...]
[2024-04-11 10:46:21] [DEBG] 	0x000120f8=0x25 %
[2024-04-11 10:46:21] [DEBG] 	0x000120f8=$$
[...]
```
Note that in our example of binary _circled_, we do not manually mark any register and/or memory
location as being symbolic (there are no `$$` specifiers in the entry state of file
[circled.init.yaml](../morion/circled.init.yaml)). Instead, and as will be explained in section
[Symbex: How Hooking Works](./4_symbex.md#how-hooking-works) below, all symbolic variables are
automatically introduced by [Morion](https://github.com/pdamian/morion) and its model for the hooked
`libc` function `fgets`.

After initializing concrete and/or symbolic values of all necessary registers and/or memory
locations in the context of the symbolic execution engine,
[Morion](https://github.com/pdamian/morion) sets up the defined function **hooks**:
```
[...]
[2024-04-11 10:46:21] [DEBG] Hooks:
[2024-04-11 10:46:21] [DEBG] 	0x0000d040: 'lib:func_hook (on=entry, mode=skip)'
[2024-04-11 10:46:21] [DEBG] 	0x0000d044: 'lib:func_hook (on=leave, mode=skip)'
[...]
[2024-04-11 10:46:21] [DEBG] 	0x0000c9c4: 'lib:func_hook (on=entry, mode=skip)'
[2024-04-11 10:46:21] [DEBG] 	0x0000c9c8: 'lib:func_hook (on=leave, mode=skip)'
[2024-04-11 10:46:21] [DEBG] 	0x0000cfe0: 'libc:fgets (on=entry, mode=model)'
[2024-04-11 10:46:21] [DEBG] 	0x0000cfe4: 'libc:fgets (on=leave, mode=model)'
[2024-04-11 10:46:21] [DEBG] 	0x0000d094: 'libc:fgets (on=entry, mode=model)'
[2024-04-11 10:46:21] [DEBG] 	0x0000d098: 'libc:fgets (on=leave, mode=model)'
[2024-04-11 10:46:21] [DEBG] 	0x0000cffc: 'libc:sscanf (on=entry, mode=model)'
[2024-04-11 10:46:21] [DEBG] 	0x0000d000: 'libc:sscanf (on=leave, mode=model)'
[2024-04-11 10:46:21] [INFO] ... finished loading file 'circled.yaml'.
[...]
```
How hooking works, while executing a trace symbolically, is explained next.
### How Hooking Works
We already discussed how hooking works during tracing in section
[Tracing: How Hooking Works](./3_tracing.md#how-hooking-works). Here, we discuss some aspects about
hooking while executing a trace symbolically.
#### Abstract Function Hook with Mode Skip (Example libc:fclose)
In the chapter about tracing (see section
[Tracing: How Hooking Works](./3_tracing.md#how-hooking-works)), we have already seen that the file
[circled.init.yaml](../morion/circled.init.yaml) defines a hook for entry and leave addresses
`0xd040` and `0xd044`, respectively. The hook corresponds to a call to function `fclose` (synopsis:
`int fclose(FILE *stream);`) from `libc` (or to be more specific, `uclibc` in case of the binary
_circled_). Due to the hooking, the effective assembly instructions of the function itself have not
been traced. Instead [Morion](https://github.com/pdamian/morion) injected some instructions to
reproduce some of the function's side-effects. Since we used an **abstract function hook**
(`hooks:lib:func_hook:`), the only modelled side-effect corresponds to setting the correct return
value(s). For the ARMv7 architecture that we target, a function's return value is generally stored
in register `r0` (and potentially `r1`). This is exactly what instructions `0x1000` - `0x100c` are
used for. [Morion](https://github.com/pdamian/morion) injected assembly instructions to move the
trace's effective return value of function `fclose` (here `0`, meaning a successful closure of the
corresponding file stream) to the return register(s).
```
[...]
[2024-04-11 10:46:22] [DEBG] 0x0000d03c (08 00 a0 e1): mov r0, r8
[2024-04-11 10:46:22] [DEBG] --> Hook: 'lib:func_hook (on=entry, mode=skip)'
[2024-04-11 10:46:22] [DEBG]           'func_hook'
[2024-04-11 10:46:22] [DEBG]     ---
[2024-04-11 10:46:22] [DEBG] 0x0000d040 (ee cf ff ea): b #0x1000               # // Hook: lib:func_hook (on=entry, mode=skip)
[2024-04-11 10:46:22] [DEBG] 0x00001000 (00 00 a0 e3): mov r0, #0              # // Hook: lib:func_hook (on=leave, mode=skip)
[2024-04-11 10:46:22] [DEBG] 0x00001004 (00 00 40 e3): movt r0, #0             # // Hook: lib:func_hook (on=leave, mode=skip)
[2024-04-11 10:46:22] [DEBG] 0x00001008 (01 10 a0 e3): mov r1, #1              # // Hook: lib:func_hook (on=leave, mode=skip)
[2024-04-11 10:46:22] [DEBG] 0x0000100c (00 10 40 e3): movt r1, #0             # // Hook: lib:func_hook (on=leave, mode=skip)
[2024-04-11 10:46:22] [DEBG] 0x00001010 (0b 30 00 ea): b #0xd044               # // Hook: lib:func_hook (on=leave, mode=skip)
[2024-04-11 10:46:22] [DEBG]     ---
[2024-04-11 10:46:22] [DEBG] <-- Hook: 'lib:func_hook (on=leave, mode=skip)'
[2024-04-11 10:46:22] [DEBG] 0x0000d044 (04 30 9d e5): ldr r3, [sp, #4]
[...]
```
When running a trace symbolically, [Morion](https://github.com/pdamian/morion) follows along the
recorded instructions (including the ones injected by hooks during tracing) and executes them one by
one using its underlying symbolic execution engine ([Triton](https://triton-library.github.io/) in
our case). For hooks with mode `skip`, no additional modifications of the symbolic state are
performed. As we will see in the next example, this might be different when using a hook with mode
`model`.
#### Specific Function Hook with Mode Model (Example libc:fgets)
As mentioned in section [Tracing: How Hooking Works](./3_tracing.md#how-hooking-works), the file
[circled.init.yaml](../morion/circled.init.yaml), beside others, also defines a hook for entry and
leave addresses `0xcfe0` and `0xcfe4`, respectively. The hook is intended to catch calls to
function `fgets` (synopsis: `char *fgets(char *s, int n, FILE *stream)`) of library `uclibc`. Again,
due to the hooking, the effective assembly instructions of the function itself have not been
recorded during tracing. Instead, some instructions got injected to reproduce the side-effects
that the function has on the memory and register contexts. When looking closely to the injected
instructions, one observes that first the effective bytes of string `s` are set
(`0xbeffc0c4: 0x41 'A'` - `0xbeffc4c2: 0x58 'X'`, `0xbeffc4c3: 0x00`), and second the
correct return value (`0xbeffc0c4` - the address of string `s`) is placed into register `r0`. In
contrast to an abstract function hook (`hooks:lib:func_hook:`) where only instructions to handle
correct function return values are injected, **specific function hooks** (`hooks:libc:fgets`) handle
additional function-specific side-effects to the memory and register contexts.
```
[...]
[2024-04-11 10:46:21] [INFO] Start symbolic execution...
[2024-04-11 10:46:21] [DEBG] 0x0000cfc0 (64 37 65 e5): strb r3, [r5, #-0x764]!
[...]
[2024-04-11 10:46:21] [DEBG] 0x0000cfdc (05 00 a0 e1): mov r0, r5
[2024-04-11 10:46:21] [DEBG] --> Hook: 'libc:fgets (on=entry, mode=model)'
[2024-04-11 10:46:21] [DEBG]           'char *fgets(char *restrict s, int n, FILE *restrict stream);'
[2024-04-11 10:46:21] [DEBG] 	 s = 0xbeffc0c4
[2024-04-11 10:46:21] [DEBG] 	 n = 1024
[2024-04-11 10:46:21] [DEBG] 	 stream = 0x00021ae0
[2024-04-11 10:46:21] [DEBG]     ---
[2024-04-11 10:46:21] [DEBG] 0x0000cfe0 (06 d0 ff ea): b #0x1000               # // Hook: libc:fgets (on=entry, mode=model)
[2024-04-11 10:46:21] [DEBG] 0x00001000 (c4 00 0c e3): movw r0, #0xc0c4        # // Hook: libc:fgets (on=leave, mode=model)
[2024-04-11 10:46:21] [DEBG] 0x00001004 (ff 0e 4b e3): movt r0, #0xbeff        # // Hook: libc:fgets (on=leave, mode=model)
[2024-04-11 10:46:21] [DEBG] 0x00001008 (41 10 a0 e3): mov r1, #0x41           # // Hook: libc:fgets (on=leave, mode=model)
[2024-04-11 10:46:21] [DEBG] 0x0000100c (00 10 40 e3): movt r1, #0             # // Hook: libc:fgets (on=leave, mode=model)
[2024-04-11 10:46:21] [DEBG] 0x00001010 (00 10 c0 e5): strb r1, [r0]           # // Hook: libc:fgets (on=leave, mode=model)
[...]
[2024-04-11 10:46:22] [DEBG] 0x00005fd8 (c2 04 0c e3): movw r0, #0xc4c2        # // Hook: libc:fgets (on=leave, mode=model)
[2024-04-11 10:46:22] [DEBG] 0x00005fdc (ff 0e 4b e3): movt r0, #0xbeff        # // Hook: libc:fgets (on=leave, mode=model)
[2024-04-11 10:46:22] [DEBG] 0x00005fe0 (58 10 a0 e3): mov r1, #0x58           # // Hook: libc:fgets (on=leave, mode=model)
[2024-04-11 10:46:22] [DEBG] 0x00005fe4 (00 10 40 e3): movt r1, #0             # // Hook: libc:fgets (on=leave, mode=model)
[2024-04-11 10:46:22] [DEBG] 0x00005fe8 (00 10 c0 e5): strb r1, [r0]           # // Hook: libc:fgets (on=leave, mode=model)
[2024-04-11 10:46:22] [DEBG] 0x00005fec (c3 04 0c e3): movw r0, #0xc4c3        # // Hook: libc:fgets (on=leave, mode=model)
[2024-04-11 10:46:22] [DEBG] 0x00005ff0 (ff 0e 4b e3): movt r0, #0xbeff        # // Hook: libc:fgets (on=leave, mode=model)
[2024-04-11 10:46:22] [DEBG] 0x00005ff4 (00 10 a0 e3): mov r1, #0              # // Hook: libc:fgets (on=leave, mode=model)
[2024-04-11 10:46:22] [DEBG] 0x00005ff8 (00 10 40 e3): movt r1, #0             # // Hook: libc:fgets (on=leave, mode=model)
[2024-04-11 10:46:22] [DEBG] 0x00005ffc (00 10 c0 e5): strb r1, [r0]           # // Hook: libc:fgets (on=leave, mode=model)
[2024-04-11 10:46:22] [DEBG] 0x00006000 (c4 00 0c e3): movw r0, #0xc0c4        # // Hook: libc:fgets (on=leave, mode=model)
[2024-04-11 10:46:22] [DEBG] 0x00006004 (ff 0e 4b e3): movt r0, #0xbeff        # // Hook: libc:fgets (on=leave, mode=model)
[2024-04-11 10:46:22] [DEBG] 0x00006008 (f5 1b 00 ea): b #0xcfe4               # // Hook: libc:fgets (on=leave, mode=model)
[2024-04-11 10:46:22] [DEBG] 	 s = 0xbeffc0c4
[2024-04-11 10:46:22] [DEBG] 	*s = 'AAA[...]AAA X'
[2024-04-11 10:46:22] [DEBG] 	0xbeffc0c4 = $$
[2024-04-11 10:46:22] [DEBG] 	...
[2024-04-11 10:46:22] [DEBG] 	0xbeffc4c2 = $$
[2024-04-11 10:46:22] [DEBG]     ---
[2024-04-11 10:46:22] [DEBG] <-- Hook: 'libc:fgets (on=leave, mode=model)'
[2024-04-11 10:46:22] [DEBG] 0x0000cfe4 (00 00 50 e3): cmp r0, #0
[...]
[2024-04-11 10:46:22] [DEBG] 0x0000cf20 (03 db 8d e2): add sp, sp, #0xc00      #                                                 
[2024-04-11 10:46:22] [DEBG] 0x0000cf24 (f0 8f bd e8): pop {r4, r5, r6, r7, r8, sb, sl, fp, pc}#                                                 
[2024-04-11 10:46:22] [INFO] ... finished symbolic execution (pc=0x41414140).
[...]
```
Since we defined a function-specific hook to be used with mode `model`, additional modifications to
the **symbolic state** might be performed. These modifications can happen either at entry or when
leaving the hook. The model implementation of `fgets` (see
[libc.py#L12](https://github.com/pdamian/morion/blob/main/morion/symbex/hooking/libc.py#L12) for
more details), for instance, makes the string `s` symbolic. This means that new symbolic variables
get assigned to each character/byte of the read string.

But why does one want to make `s` symbolic?
Well, `s` is read in from a resource external to the targeted binary (here a file), which is
potentially controllable by a (malicious) user. By making `s` symbolic we might conduct various
analysis about how it, respectively an attacker, can influence our target program. As will be
explained in the next section [Analyzing Symbolic State](./4_symbex.md#analyzing-symbolic-state), in
the case of binary *circled*, we for instance immediately see that the program counter (`pc`) at the
end of the trace is symbolic. Phrased differently, the `pc` can (somehow) be influenced by
attacker-controllable values, potentially leading to control-flow hijacking attacks.

**Note**: In case you want to hook invocations of function `fgets` without making the read string
symbolic, define the corresponding hook to use mode `skip`.

**Note**: [Morion](https://github.com/pdamian/morion) is a *proof-of-concept (PoC)* tool intended to be
used for experimenting with symbolic execution on (real-world) (ARMv7) binaries. It currently
implements (only) a handful of hooks for common `libc` functions. These should be extended in future
work (pull requests are welcome).
### Analyzing Symbolic State
If we symbolize inputs that an attacker can control, symbolic execution not only allows us to see
which parts of a target binary can be influenced, but also how this may happen. At the end of a
symbolic execution run, [Morion](https://github.com/pdamian/morion) for instance analyzes the
**symbolic state** (can be disabled using option `--skip_state_analysis`). This means that an
overview is given about which registers and memory locations are based on symbolic variable(s). In
the example of the collected trace of binary *circled*, one immediately sees that the program
counter (register `pc`) is one of these candidates. Remember that we only marked inputs an attacker
might control as being symbolic, meaning that an attacker can potentially influence the program's
control-flow.
```
[...]
[2024-04-11 10:46:22] [INFO] Start analyzing symbolic state...
[2024-04-11 10:46:22] [INFO] Symbolic Regs:
[2024-04-11 10:46:22] [INFO] 	pc=$$$$$$$$
[2024-04-11 10:46:22] [INFO] 	r10=$$$$$$$$
[2024-04-11 10:46:22] [INFO] 	r11=$$$$$$$$
[2024-04-11 10:46:23] [INFO] 	r4=$$$$$$$$
[2024-04-11 10:46:23] [INFO] 	r5=$$$$$$$$
[2024-04-11 10:46:23] [INFO] 	r6=$$$$$$$$
[2024-04-11 10:46:23] [INFO] 	r7=$$$$$$$$
[2024-04-11 10:46:24] [INFO] 	r8=$$$$$$$$
[2024-04-11 10:46:24] [INFO] 	r9=$$$$$$$$
[2024-04-11 10:46:24] [INFO] Symbolic Mems:
[2024-04-11 10:47:23] [INFO] 	0xbeffc0c4=$$
[2024-04-11 10:47:23] [INFO] 	...
[2024-04-11 10:47:23] [INFO] 	0xbeffc4c2=$$
[2024-04-11 10:47:23] [INFO] 	0xbeffc5c4=$$
[2024-04-11 10:47:23] [INFO] 	0xbeffc6c4=$$
[2024-04-11 10:47:23] [INFO] 	...
[2024-04-11 10:47:23] [INFO] 	0xbeffcac0=$$
[2024-04-11 10:47:23] [INFO] ... finished analyzing symbolic state.
[2024-04-11 10:47:23] [INFO] Start storing file 'circled.yaml'...
[2024-04-11 10:47:25] [INFO] ... finished storing file 'circled.yaml'.
```
In chapter [Exploitation](./6_exploitation.md), we will see how symbolic execution might help us to
decide whether the crasher we traced might be **exploitable** or not, i.e. corresponds to an actual
security vulnerability or just an annoying bug. We will also see, how symbolic execution can quickly
give us a first high-level intuition about what **capabilities** (e.g. arbitrary read/write,
control-flow hijacking, etc.) one might gain with the underlying issue. Also, we will show how
symbolic execution might help us during the process of generating a working **exploit** for the
targeted vulnerability (CVE-2022-27646).

----------------------------------------------------------------------------------------------------
[Back-to-Top](./4_symbex.md#table-of-contents)