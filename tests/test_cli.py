from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def test_describe_cli(tmp_path: Path) -> None:
    result = subprocess.run(
        [sys.executable, "-m", "ctrltest_mcp", "--describe"],
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(result.stdout)
    assert payload["name"] == "ctrltest-mcp"
    assert payload["default_transport"] == "stdio"
