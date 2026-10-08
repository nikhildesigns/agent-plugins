"""Protocol checks for recovery transport; never launches the app or real helper."""
import base64
import contextlib
import importlib.util
import io
import json
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import MagicMock, patch

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


PNG = base64.b64decode("iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+aG1sAAAAASUVORK5CYII=")


class ImageOutputTests(unittest.TestCase):
    def result(self, data=None):
        return {"content": [
            {"type": "text", "text": '{"revision":"saved","width":1,"height":1}'},
            {"type": "image", "mimeType": "image/png", "data": data or base64.b64encode(PNG).decode()},
        ]}

    def invoke(self, result, output_path="/approved/review.png", open_error=None):
        session = MagicMock()
        session.discover.return_value = {"tools": [{"name": "render_canvas"}]}
        session.request.return_value = result
        output, errors = io.StringIO(), io.StringIO()
        options = ["--image-output", output_path] if output_path is not None else []
        file = MagicMock()
        file.__enter__.return_value = file
        with patch.object(mcp, "McpSession", return_value=session), patch.object(
            sys, "argv", [str(SCRIPT), "call", "render_canvas", *options]
        ), patch.object(sys, "stdin", io.StringIO('{"path":"/approved/Canvas.lcv"}')), patch.object(
            mcp.Path, "is_file", return_value=True
        ), patch.object(mcp.Path, "is_dir", return_value=True), patch.object(
            mcp.Path, "open", return_value=file, side_effect=open_error
        ) as opened, contextlib.redirect_stdout(output), contextlib.redirect_stderr(errors):
            status = mcp.main()
        session.close.assert_called_once()
        return status, output.getvalue(), errors.getvalue(), opened, file

    def test_saves_exact_png_and_preserves_revision_without_base64(self):
        result = self.result()
        status, output, errors, opened, file = self.invoke(result)
        self.assertEqual((status, errors), (0, ""))
        opened.assert_called_once_with("xb")
        file.write.assert_called_once_with(PNG)
        data = json.loads(output)
        self.assertEqual(data["content"][0], result["content"][0])
        self.assertEqual(data["imageOutput"], {"path": "/approved/review.png", "mimeType": "image/png", "bytes": len(PNG)})
        self.assertNotIn(result["content"][1]["data"], output)
        self.assertEqual(result["content"][1]["type"], "image")

    def test_default_omits_image_without_writing(self):
        result = self.result()
        status, output, _, opened, _ = self.invoke(result, output_path=None)
        self.assertEqual(status, 0)
        opened.assert_not_called()
        self.assertNotIn(result["content"][1]["data"], output)
        self.assertIn("--image-output", output)
        self.assertNotIn("imageOutput", json.loads(output))

    def test_existing_file_or_symlink_is_never_overwritten(self):
        status, output, errors, opened, file = self.invoke(self.result(), open_error=FileExistsError("exists"))
        self.assertEqual((status, output), (1, ""))
        opened.assert_called_once_with("xb")
        file.write.assert_not_called()
        self.assertIn("exists", errors)

    def test_tool_error_preserves_diagnostics_and_never_creates_file(self):
        result = self.result()
        result["isError"] = True
        result["content"][0]["text"] = "scopeDenied"
        status, output, _, opened, _ = self.invoke(result)
        self.assertEqual(status, 1)
        opened.assert_not_called()
        self.assertTrue(json.loads(output)["isError"])
        self.assertIn("scopeDenied", output)
        self.assertNotIn(result["content"][1]["data"], output)

    def test_missing_multiple_wrong_type_or_invalid_image_never_creates_file(self):
        missing = {"content": [{"type": "text", "text": "metadata"}]}
        multiple = self.result()
        multiple["content"].append(multiple["content"][1])
        wrong_type = self.result()
        wrong_type["content"][1]["mimeType"] = "image/jpeg"
        oversized_dimensions = bytearray(PNG)
        oversized_dimensions[16:20] = (4097).to_bytes(4, "big")
        for result in [missing, multiple, wrong_type, self.result("not base64!"),
                       self.result(base64.b64encode(b"not png").decode()),
                       self.result(base64.b64encode(oversized_dimensions).decode())]:
            with self.subTest(result=result):
                status, output, errors, opened, _ = self.invoke(result)
                self.assertEqual((status, output), (1, ""))
                self.assertTrue(errors)
                opened.assert_not_called()

    def test_oversized_png_is_rejected_before_file_creation(self):
        with patch.object(mcp, "MAX_IMAGE_BYTES", len(PNG) - 1):
            status, output, errors, opened, _ = self.invoke(self.result())
        self.assertEqual((status, output), (1, ""))
        self.assertIn("limit", errors)
        opened.assert_not_called()

    def test_output_requires_absolute_png_path_and_existing_parent(self):
        for value in ["relative.png", "/approved/image.jpeg"]:
            with self.subTest(value=value), self.assertRaises(ValueError):
                mcp.image_destination(value)
        with patch.object(mcp.Path, "is_dir", return_value=False), self.assertRaises(ValueError):
            mcp.image_destination("/missing/review.png")

    def test_malformed_content_is_rejected_without_writing(self):
        for result in [[], {"content": None}, {"content": ["bad block"]}]:
            with self.subTest(result=result):
                status, output, errors, opened, _ = self.invoke(result)
                self.assertEqual((status, output), (1, ""))
                self.assertIn("malformed", errors)
                opened.assert_not_called()

    def test_disk_failure_reports_output_path_and_no_success(self):
        with patch.object(mcp.Path, "open") as opened:
            opened.return_value.__enter__.return_value.write.side_effect = OSError("disk full")
            with self.assertRaisesRegex(OSError, "/approved/review.png"):
                mcp.printable_result(self.result(), Path("/approved/review.png"))

    def test_image_option_is_rejected_for_discovery(self):
        with patch.object(sys, "argv", [str(SCRIPT), "discover", "--image-output", "/approved/review.png"]), contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as stopped:
            mcp.main()
        self.assertEqual(stopped.exception.code, 2)


if __name__ == "__main__":
    unittest.main()
