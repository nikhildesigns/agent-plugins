#!/usr/bin/env python3
"""Call the installed LocalEditor MCP helper when a client cannot expose it."""
import argparse
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
            "clientInfo": {"name": "localeditor-plugin-recovery", "version": "0.2.0"},
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


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("operation", choices=["discover", "call"])
    parser.add_argument("tool", nargs="?")
    args = parser.parse_args()
    if (args.operation == "call") != bool(args.tool):
        parser.error("call requires a tool name; discover takes no tool name")
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
