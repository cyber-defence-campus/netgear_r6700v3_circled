# Table of Contents
1. [Setup](./1_setup.md)
2. [Emulation](./2_emulation.md)
3. [Vulnerability CVE-2022-27646](./3_vulnerability.md)
4. [Tracing](./4_tracing.md)
5. [Symbolic Execution](./5_symbex.md)
6. [Exploitation](./6_exploitation.md)
# Symbolic Execution
## TODO
This parameter is used to distinguish multiple symbolic hooking implementations (see
[Symbolic Execution](./5_symbex.md)) that will be executed instead of the actual function's assembly
instructions.

[Morion](https://github.com/pdamian/morion) currently implements (only) a handful of hooks for
common _libc_ functions, with supported modes of `skip`, `model` or `taint` (TODO: Add reference).