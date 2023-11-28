# Table of Contents
1. [Setup](./setup.md)
2. [Emulation](./emulation.md)
3. [Tracing](./tracing.md)
   1. [Setup](./tracing.md#setup)
      1. [GDB Commands Script](./tracing.md#gdb-commands-script)
      2. [Hooks](./tracing.md#hooks)
      3. [States](./tracing.md#states)
   2. [Run](./tracing.md#run)
4. [Symbolic Execution](./symbex.md)
# Tracing
## Setup
### GDB Commands Script
[circled.trace.gdb](../morion/circled.trace.gdb):
```
[...]
# Addresses
[...]
set $before_vulnerability     = 0xcfc0
[...]

# Break before vulnerabilty
break *$before_vulnerability
continue

# Trace till return of function updating_database
morion_trace debug circled.yaml 0xf1a4
[...]
```
### Hooks
[circled.init.yaml](../morion/circled.init.yaml):
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
### States
[circled.init.yaml](../morion/circled.init.yaml):
```
[...]
states:
  entry:
    mems:
      '0x000120f8': ['0x25']  # '%'
      '0x000120f9': ['0x73']  # 's'
      '0x000120fa': ['0x20']  # ' '
      '0x000120fb': ['0x25']  # '%'
      '0x000120fc': ['0x73']  # 's'
      '0x000120fd': ['0x00']  #
[...]
```
## Run
Use the following steps to create a **trace** of the binary _circled_, while it is targeted with a _proof-of-vulnerability (PoV)_ payload (as for instance being identified by a fuzzer):
1. Start a HTTP server, delivering PoV payloads:
   - System: [Guest](./setup.md)
   - Command:
      ```
      python3 server/circled.server.py --payload "pov"
      ```
2. Emulate the binary _circled_ with GDB attached (and therefore not using ASRL):
   - System: [Guest (chroot)](./setup.md)
   - Command:
     ```
     /circled.sh --gdb
3. Collect an execution trace of the binary _circled_:
   - System: [Host (morion)](./setup.md)
   - Command:
     ```
     cd morion/;                              # Ensure to be within the correct directory
     cp circled.init.yaml circled.yaml;       # Start with a fresh circled.yaml file
     gdb-multiarch -q -x circled.trace.gdb;   # Use GDB for cross-platform remote trace collection
     ```
