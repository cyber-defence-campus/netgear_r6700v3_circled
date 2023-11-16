#!/usr/bin/env python3
## -*- coding: utf-8 -*-
import argparse
from   shutil   import copyfile

base_addr = 0x8000
patch_addr = 0xf984
opcodes   = b"\x00\x00\xa0\xe3"    # mov r0, #0

def main() -> None:
    # Argument parsing
    description = """
    Remove anti-debugging check (LD_PRELOAD) in the binary circled.
    """
    parser = argparse.ArgumentParser(description=description,
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("circled_orig", help="name of input file (original circled binary)")
    parser.add_argument("circled_patched", help="name of output file (patched circled binary)")
    args = parser.parse_args()

    # Make a copy of the original binary
    copyfile(args.circled_orig, args.circled_patched)

    # Replace '0xc7a0: bl #0xc6a4' with '0xc7a0: mov r0, #0'
    with open(args.circled_patched, "rb+") as f:
        f.seek(patch_addr-base_addr)
        f.write(opcodes)
    
if __name__ == "__main__":
    main()