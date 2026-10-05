"""Protocol checks for recovery transport; never launches the app or real helper."""
import contextlib
import importlib.util
import io
import json
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import patch

sys.dont_write_bytecode = True
SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "localeditor_mcp.py"
SPEC = importlib.util.spec_from_file_location("localeditor_mcp", SCRIPT)
mcp = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(mcp)

SERVER = r"""
import json, sys
initialized = False
for line in sys.stdin:
    request = json.loads(line)
    method = request["method"]
    if method == "notifications/initialized":
        initialized = True
        continue
    assert method == "initialize" or initialized
    if method == "initialize":
        result = {"serverInfo": {"name": "fixture"}, "instructions": "fixture instructions"}
    elif method == "tools/list":
        if request["params"].get("cursor"):
            result = {"tools": [{"name": "blocked"}]}
        else:
            result = {"tools": [{"name": "read_document"}], "nextCursor": "next"}
    else:
        assert method == "tools/call"
        if request["params"]["name"] == "blocked":
            result = {"isError": True, "content": [{"type": "text", "text": "scopeDenied"}]}
        else:
            result = {"content": [{"type": "text", "text": request["params"]["arguments"]["path"]}]}
    print(json.dumps({"jsonrpc": "2.0", "method": "notifications/progress", "params": {}}), flush=True)
    print(json.dumps({"jsonrpc": "2.0", "id": request["id"], "result": result}), flush=True)
"""


class RecoveryTests(unittest.TestCase):
    def setUp(self):
        real_popen = subprocess.Popen
        self.real_popen = real_popen
        def start_fixture(command, **kwargs):
            self.assertEqual(command, [str(mcp.HELPER)])
            return real_popen([sys.executable, "-u", "-c", SERVER], **kwargs)
        self.process_patch = patch.object(mcp.subprocess, "Popen", side_effect=start_fixture)
        self.process_patch.start()
        self.addCleanup(self.process_patch.stop)

    def invoke(self, arguments, stdin=""):
        output, errors = io.StringIO(), io.StringIO()
        with patch.object(sys, "argv", [str(SCRIPT), *arguments]), patch.object(
            sys, "stdin", io.StringIO(stdin)
        ), patch.object(mcp.Path, "is_file", return_value=True), contextlib.redirect_stdout(
            output
        ), contextlib.redirect_stderr(errors):
            status = mcp.main()
        return status, output.getvalue(), errors.getvalue()

    def test_initialization_notifications_and_paginated_discovery(self):
        status, output, _ = self.invoke(["discover"])
        self.assertEqual(status, 0)
        data = json.loads(output)
        self.assertEqual(data["server"]["instructions"], "fixture instructions")
        self.assertEqual([tool["name"] for tool in data["tools"]], ["read_document", "blocked"])

    def test_literal_unicode_arguments_are_sent_as_json(self):
        path = "/Users/test/a 'quote' $HOME \u65e5\u672c\u8a9e.md"
        status, output, _ = self.invoke(["call", "read_document"], json.dumps({"path": path}))
        self.assertEqual(status, 0)
        self.assertEqual(json.loads(output)["content"][0]["text"], path)

    def test_tool_error_is_preserved_and_has_unsuccessful_exit(self):
        status, output, _ = self.invoke(["call", "blocked"], "{}")
        self.assertEqual(status, 1)
        self.assertTrue(json.loads(output)["isError"])
        self.assertEqual(json.loads(output)["content"][0]["text"], "scopeDenied")

    def test_unavailable_tool_stops_before_call(self):
        status, output, errors = self.invoke(["call", "missing_tool"], "{}")
        self.assertEqual(status, 1)
        self.assertEqual(output, "")
        self.assertIn("does not expose", errors)


    def test_transport_timeout_closes_the_helper(self):
        real_popen = self.real_popen
        child = []
        def start_silent(command, **kwargs):
            process = real_popen([sys.executable, "-c", "import sys; sys.stdin.read()"], **kwargs)
            child.append(process)
            return process
        with patch.object(mcp.subprocess, "Popen", side_effect=start_silent), patch.object(mcp, "TIMEOUT", 0.05):
            status, output, errors = self.invoke(["discover"])
        self.assertEqual(status, 1)
        self.assertEqual(output, "")
        self.assertIn("Timed out", errors)
        self.assertIsNotNone(child[0].poll())

    def test_closed_output_fails_without_hanging(self):
        real_popen = self.real_popen
        with patch.object(mcp.subprocess, "Popen", side_effect=lambda command, **kwargs:
                          real_popen([sys.executable, "-c", "pass"], **kwargs)):
            status, output, errors = self.invoke(["discover"])
        self.assertEqual(status, 1)
        self.assertEqual(output, "")
        self.assertIn("closed its output", errors)


if __name__ == "__main__":
    unittest.main()
