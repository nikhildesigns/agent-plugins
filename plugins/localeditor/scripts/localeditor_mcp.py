#!/usr/bin/env python3
"""Call the installed LocalEditor MCP helper when a client cannot expose it."""
import argparse
import base64
import binascii
from collections import deque
import json
from pathlib import Path
import queue
import subprocess
import sys
import threading
import time

HELPER = Path("/Applications/LocalEditor.app/Contents/Helpers/localeditor-mcp")
TIMEOUT = 45
MAX_IMAGE_BYTES = 8 * 1024 * 1024
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


class McpSession:
    def __init__(self):
        self.process = subprocess.Popen(
            [str(HELPER)], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
            stderr=subprocess.PIPE, text=True, encoding="utf-8",
        )
        self.incoming = queue.Queue(maxsize=128)
        self.errors = deque(maxlen=20)
        self.next_id = 0
        threading.Thread(target=self._read, daemon=True).start()
        threading.Thread(target=self._read_errors, daemon=True).start()

    def _read(self):
        try:
            while True:
                line = self.process.stdout.readline(16 * 1024 * 1024 + 1)
                if not line:
                    self.incoming.put(RuntimeError("LocalEditor MCP closed its output."))
                    return
                if len(line) > 16 * 1024 * 1024:
                    raise RuntimeError("LocalEditor MCP response exceeded the transport limit.")
                self.incoming.put(json.loads(line))
        except Exception as error:
            self.incoming.put(error)

    def _read_errors(self):
        for line in self.process.stderr:
            self.errors.append(line[:2000].rstrip())

    def send(self, message):
        self.process.stdin.write(json.dumps(message, ensure_ascii=False) + "\n")
        self.process.stdin.flush()

    def request(self, method, params):
        self.next_id += 1
        request_id = self.next_id
        self.send({"jsonrpc": "2.0", "id": request_id, "method": method, "params": params})
        # Bound the whole request, including unsolicited notification traffic.
        deadline = time.monotonic() + TIMEOUT
        while True:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise RuntimeError("Timed out waiting for LocalEditor MCP.")
            try:
                message = self.incoming.get(timeout=remaining)
            except queue.Empty as error:
                raise RuntimeError("Timed out waiting for LocalEditor MCP.") from error
            if isinstance(message, Exception):
                raise message
            if not isinstance(message, dict):
                raise RuntimeError("LocalEditor MCP returned a malformed response.")
            if message.get("id") != request_id:
                continue
            if "error" in message:
                raise RuntimeError(json.dumps(message["error"], ensure_ascii=False))
            if "result" not in message:
                raise RuntimeError("LocalEditor MCP response has no result.")
            return message["result"]

    def discover(self):
        info = self.request("initialize", {
            "protocolVersion": "2024-11-05", "capabilities": {},
            "clientInfo": {"name": "localeditor-plugin-recovery", "version": "0.4.1"},
        })
        self.send({"jsonrpc": "2.0", "method": "notifications/initialized"})
        tools = []
        cursor = None
        seen_cursors = set()
        while True:
            page = self.request("tools/list", {"cursor": cursor} if cursor else {})
            tools.extend(page.get("tools", []))
            cursor = page.get("nextCursor")
            if not cursor:
                return {"server": info, "tools": tools}
            if cursor in seen_cursors:
                raise RuntimeError("LocalEditor MCP repeated its tool-list cursor.")
            seen_cursors.add(cursor)

    def close(self):
        try:
            self.process.stdin.close()
            self.process.wait(timeout=2)
        except (OSError, subprocess.TimeoutExpired):
            self.process.terminate()
            try:
                self.process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                self.process.kill()
                self.process.wait()
        finally:
            self.process.stdout.close()
            self.process.stderr.close()


def image_destination(value):
    path = Path(value)
    if not path.is_absolute() or path.suffix.lower() != ".png":
        raise ValueError("--image-output requires an absolute .png path.")
    if not path.parent.is_dir():
        raise ValueError("The image output parent directory must already exist.")
    return path


def printable_result(result, destination=None):
    """Keep MCP metadata/errors, never emit image base64 into model context."""
    if not isinstance(result, dict):
        raise ValueError("LocalEditor MCP returned a malformed tool result.")
    content = result.get("content", [])
    if not isinstance(content, list) or not all(isinstance(item, dict) for item in content):
        raise ValueError("LocalEditor MCP returned malformed content blocks.")
    images = [item for item in content if item.get("type") == "image"]
    output = dict(result)
    output["content"] = [
        {"type": "text", "text": "Image data omitted by recovery transport; use --image-output to save a PNG for inspection."}
        if item.get("type") == "image" else item
        for item in content
    ]
    if destination is None or result.get("isError"):
        return output
    if len(images) != 1 or images[0].get("mimeType") != "image/png":
        raise ValueError("Image output requires exactly one image/png block in a successful tool result.")
    encoded = images[0].get("data")
    if not isinstance(encoded, str) or len(encoded) > 4 * ((MAX_IMAGE_BYTES + 2) // 3):
        raise ValueError("PNG data is missing or exceeds the 8 MiB image limit.")
    try:
        pixels = base64.b64decode(encoded, validate=True)
    except (ValueError, binascii.Error) as error:
        raise ValueError("The PNG image has invalid base64 data.") from error
    if len(pixels) > MAX_IMAGE_BYTES:
        raise ValueError("PNG data exceeds the 8 MiB image limit.")
    if (len(pixels) < 33 or pixels[:8] != PNG_SIGNATURE
            or pixels[8:16] != b"\x00\x00\x00\x0dIHDR"
            or not 1 <= int.from_bytes(pixels[16:20], "big") <= 4096
            or not 1 <= int.from_bytes(pixels[20:24], "big") <= 4096):
        raise ValueError("The image does not have a supported PNG header/dimensions.")
    # Exclusive creation rejects existing files and symlinks, including races.
    # Do not precreate output before the MCP call has succeeded and validated.
    try:
        with destination.open("xb") as file:
            file.write(pixels)
    except OSError as error:
        raise OSError(f"Could not save PNG at {destination}: {error}. A failed new write may leave a partial file.") from error
    output["imageOutput"] = {"path": str(destination), "mimeType": "image/png", "bytes": len(pixels)}
    return output


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("operation", choices=["discover", "call"])
    parser.add_argument("tool", nargs="?")
    parser.add_argument("--image-output", help="Save one successful PNG image to a new absolute path; never overwrite.")
    args = parser.parse_args()
    if (args.operation == "call") != bool(args.tool):
        parser.error("call requires a tool name; discover takes no tool name")
    if args.image_output and args.operation != "call":
        parser.error("--image-output is only supported with call")
    destination = None
    if args.image_output:
        try:
            destination = image_destination(args.image_output)
        except ValueError as error:
            parser.error(str(error))
    arguments = {}
    if args.operation == "call":
        try:
            arguments = json.load(sys.stdin)
            if not isinstance(arguments, dict):
                raise ValueError("Tool arguments must be a JSON object.")
        except (ValueError, UnicodeError) as error:
            parser.error(str(error))
    if not HELPER.is_file():
        print("LocalEditor MCP helper is missing. Install LocalEditor in /Applications.", file=sys.stderr)
        return 1
    session = None
    try:
        session = McpSession()
        discovered = session.discover()
        if args.operation == "discover":
            result = discovered
        else:
            if not any(tool.get("name") == args.tool for tool in discovered["tools"]):
                raise RuntimeError("The installed helper does not expose the requested tool.")
            result = session.request("tools/call", {"name": args.tool, "arguments": arguments})
            result = printable_result(result, destination)
        print(json.dumps(result, ensure_ascii=False))
        return 1 if result.get("isError") else 0
    except (OSError, RuntimeError, ValueError) as error:
        print(f"LocalEditor MCP recovery failed: {error}", file=sys.stderr)
        if session:
            for line in session.errors:
                print(line, file=sys.stderr)
        return 1
    finally:
        if session:
            session.close()


if __name__ == "__main__":
    sys.exit(main())
