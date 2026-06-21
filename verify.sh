#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
python3 -m py_compile "$ROOT/scripts/ai_news_rss_probe.py" "$ROOT/scripts/ai_investment_rss_probe.py" "$ROOT/scripts/ai_daily_intelligence_probe.py"
python3 "$ROOT/scripts/ai_daily_intelligence_probe.py" > /tmp/ai_daily_intelligence_probe_sample.json
python3 - <<'PY'
import json
p='/tmp/ai_daily_intelligence_probe_sample.json'
d=json.load(open(p))
print('Probe generated_at:', d.get('generated_at'))
print('Stats:')
for k,v in (d.get('stats') or {}).items():
    print(' ', k, v)
assert d.get('sections'), 'missing sections'
for sec in d['sections']:
    assert sec.get('data'), f"missing data for {sec.get('name')}"
print('OK: probe scripts compile and return JSON. Sample saved to', p)
PY
