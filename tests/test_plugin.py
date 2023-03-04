from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from textwrap import dedent


def test_smoke(tmp_path: Path) -> None:
    file_path = tmp_path / 'example.py'
    source = """
        def f():
            pass
    """
    file_path.write_text(dedent(source))
    cmd = [sys.executable, '-m', 'flake8', '--isolated', str(tmp_path)]
    result = subprocess.run(cmd, stdout=subprocess.PIPE)

    assert result.returncode == 1
    msgs = result.stdout.decode().strip().splitlines()
    print(*msgs, sep='\n')

    assert len(msgs) == 3
    for msg in msgs:
        assert 'example.py:' in msg
        assert ':1: PLC' in msg
    assert 'PLC114 Missing module docstring (missing-module-docstring)' in msgs[0]
    assert 'PLC116 Missing function or method docstring' in msgs[1]
    assert 'PLC103 Function name "f"' in msgs[2]
