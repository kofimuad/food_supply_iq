"""Export the FastAPI OpenAPI schema to packages/api-types/openapi.json.

Run whenever the API contract changes:
    python api/scripts/export_openapi.py   (from repo root, with the api venv)

The typed TS client is then regenerated from that JSON via `pnpm gen:types`.
No database/server is needed — this only introspects the route definitions.
"""

import json
from pathlib import Path

from app.main import app

OUT = Path(__file__).resolve().parents[2] / "packages" / "api-types" / "openapi.json"


def main() -> None:
    schema = app.openapi()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(schema, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {OUT}  ({len(schema['paths'])} paths)")


if __name__ == "__main__":
    main()
