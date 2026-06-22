"""Entry for ``python -m dream_replay_cli``.

Delegates to the real click group in ``dreamreplay.cli`` so the
contract-named command (``python -m dream_replay_cli validate``) drives
the same CLI as ``dreamreplay``.
"""

from __future__ import annotations

from dreamreplay.cli import main

if __name__ == "__main__":
    main()
