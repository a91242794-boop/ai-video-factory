#!/usr/bin/env python3
import json, sys
from pathlib import Path
try:
    import jsonschema
except ImportError:
    print("缺少 jsonschema：pip install jsonschema", file=sys.stderr)
    raise SystemExit(2)

if len(sys.argv) != 3:
    print("用法: python validate.py <data.json> <schema.json>")
    raise SystemExit(2)

data = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
schema = json.loads(Path(sys.argv[2]).read_text(encoding="utf-8"))
jsonschema.validate(data, schema)
print("VALID")
