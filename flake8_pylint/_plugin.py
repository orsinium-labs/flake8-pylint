from __future__ import annotations

import sys
from ast import AST
from tokenize import TokenInfo
from typing import TYPE_CHECKING, Any, Iterator, Sequence

from pylint.lint import Run
from pylint.reporters import BaseReporter


if TYPE_CHECKING:
    from pylint.message import Message
    from pylint.reporters.ureports.nodes import BaseLayout


if sys.version_info >= (3, 8):
    from importlib import metadata as importlib_metadata
else:
    import importlib_metadata


STDIN = 'stdin'
PREFIX = 'PL'

try:
    # older pylint versions
    from pylint.__pkginfo__ import version
    VERSION = version
except ImportError:
    try:
        VERSION = importlib_metadata.version('pylint')
    except Exception:
        VERSION = 'unknown'


class Reporter(BaseReporter):
    def __init__(self) -> None:
        self.errors: list[dict[str, Any]] = []
        super().__init__()

    def _display(self, layout: BaseLayout) -> None:
        pass

    def handle_message(self, msg: Message) -> None:
        # ignore `invalid syntax` messages, it is already checked by `pycodestyle`
        if msg.msg_id == 'E0001':
            return
        self.errors.append(dict(
            row=msg.line,
            col=msg.column,
            text='{prefix}{id} {msg} ({symbol})'.format(
                prefix=PREFIX,
                id=msg.msg_id,
                msg=msg.msg or '',
                symbol=msg.symbol,
            ),
            code=msg.msg_id,
        ))


class PyLintChecker:
    name = 'pylint'
    version = VERSION

    def __init__(
        self,
        tree: AST,
        file_tokens: Sequence[TokenInfo],
        filename: str = STDIN,
    ) -> None:
        self.tree = tree
        self.filename = filename

    def run(self) -> Iterator[tuple[int, int, str, type]]:
        reporter = Reporter()
        Run([self.filename], reporter=reporter, do_exit=False)
        for error in reporter.errors:
            yield error['row'], error['col'], error['text'], type(self)
