#!/usr/bin/env python3
"""Combined AI industry + AI investment probe for a single daily intelligence cron."""
from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

SCRIPTS = [
    ("ai_news", Path.home() / ".hermes/scripts/ai_news_rss_probe.py"),
    ("ai_investment", Path.home() / ".hermes/scripts/ai_investment_rss_probe.py"),
]


def run_script(name: str, path: Path) -> dict:
    try:
        proc = subprocess.run(
            [sys.executable, str(path)],
            capture_output=True,
            text=True,
            timeout=115,
            check=False,
        )
        data = None
        if proc.stdout.strip():
            # Defensive: strip warnings/noise before first JSON char.
            out = proc.stdout
            idx = out.find("{")
            if idx >= 0:
                data = json.loads(out[idx:])
        return {
            "name": name,
            "script": str(path),
            "returncode": proc.returncode,
            "error": proc.stderr[-1000:] if proc.stderr else None,
            "data": data,
        }
    except Exception as e:
        return {"name": name, "script": str(path), "returncode": None, "error": f"{type(e).__name__}: {e}", "data": None}


def main() -> int:
    result = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "note": "Combined candidate leads for AI industry news and AI investment/funding. Treat all items as leads; agent must verify source/date/facts before inclusion.",
        "sections": [run_script(name, path) for name, path in SCRIPTS],
    }
    result["stats"] = {
        sec["name"]: (sec.get("data") or {}).get("stats") for sec in result["sections"]
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
