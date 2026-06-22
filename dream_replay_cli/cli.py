"""CLI entry-point shim.

Re-exports the click group from ``dreamreplay.cli`` so callers using the
contract-named import path (``dream_replay_cli.cli:main``) still work.
"""

from __future__ import annotations

from dreamreplay.cli import cmd_run, main, run_pipeline

__all__ = ["cmd_run", "main", "run_pipeline"]


if __name__ == "__main__":
    main()
