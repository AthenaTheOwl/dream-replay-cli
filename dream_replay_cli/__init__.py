"""Contract-stable shim package for DreamReplay.

The implementation lives in ``src/dreamreplay/``. This package exposes
the names the factory contract expects (``cli``, ``score``, ``ledger``,
``report``) by re-exporting from the real package.
"""

from __future__ import annotations

__version__ = "0.1.0"
