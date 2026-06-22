"""validate_schemas — index.json must validate against dream.schema.json.

Usage:
  python scripts/validate_schemas.py
  python scripts/validate_schemas.py dreams/2026-W25/index.json

Implements R-DRM-006 (schema-validated index) and R-DRM-017 (schema
gate script).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from jsonschema import Draft202012Validator

REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = REPO_ROOT / "schemas" / "dream.schema.json"


def _validate(index_path: Path, validator: Draft202012Validator) -> list[str]:
    try:
        instance = json.loads(index_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        return [f"{index_path}: invalid JSON ({e.msg})"]
    errors = [
        f"{index_path}: {'.'.join(str(p) for p in err.absolute_path)}: "
        f"{err.message}"
        for err in validator.iter_errors(instance)
    ]
    return errors


def main(argv: list[str]) -> int:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    validator = Draft202012Validator(schema)

    if len(argv) > 1:
        paths = [Path(p) for p in argv[1:]]
    else:
        paths = sorted((REPO_ROOT / "dreams").glob("*/index.json"))

    if not paths:
        print("validate_schemas: no index.json files found")
        return 0

    all_errors: list[str] = []
    for p in paths:
        all_errors.extend(_validate(p, validator))
    if all_errors:
        for e in all_errors:
            print(e)
        return 1
    print(f"validate_schemas: {len(paths)} file(s) clean")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
