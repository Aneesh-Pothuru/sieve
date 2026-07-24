from __future__ import annotations

import html
from pathlib import Path

from .models import AuditResult

STYLE = """
body{font-family:ui-monospace,SFMono-Regular,Menlo,monospace;background:#11100c;color:#f1ead7;margin:0}
main{max-width:1120px;margin:auto;padding:32px}.hero{border:1px solid #826f32;background:#1b190f;padding:24px}
h1,h2{color:#f1d76d}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:14px}
.card{border:1px solid #5d522b;background:#19170f;padding:15px}.critical,.high{color:#ff9b80}
table{border-collapse:collapse;width:100%;font-size:13px}th,td{border:1px solid #5d522b;padding:7px;text-align:left}
.band{font-size:34px;color:#fff}.muted{color:#b6aa82}.ok{color:#9de39f}
"""


def render(result: AuditResult, output: str | Path) -> Path:
    finding_cards = "".join(
        f"""<article class="card"><p class="muted">{html.escape(item.task_id)}</p>
        <h2 class="{item.severity}">{html.escape(item.verdict)}</h2>
        <p>{html.escape(item.detail)}</p>
        <p>secondary: {html.escape(', '.join(item.secondary) or '—')}<br>
        evidence: {html.escape(item.evidence_tier)}<br>
        FP lower bound: {'yes' if item.fp_lower_bound else 'no'}</p>
        <code>{html.escape(item.reproducer)}</code></article>"""
        for item in result.findings
    )
    rows = "".join(
        "<tr>"
        f"<td>{html.escape(task_id)}</td>"
        f"<td>{values['fp'].failures}/{values['fp'].trials}</td>"
        f"<td>{values['fp'].rate:.1%} [{values['fp'].low:.1%}, {values['fp'].high:.1%}]</td>"
        f"<td>{values['fn'].failures}/{values['fn'].trials}</td>"
        f"<td>{values['fn'].rate:.1%} [{values['fn'].low:.1%}, {values['fn'].high:.1%}]</td>"
        "</tr>"
        for task_id, values in result.grader_rates.items()
    )
    band = result.trust_band
    document = f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width"><title>SIEVE · {html.escape(result.suite_name)}</title>
<style>{STYLE}</style></head><body><main>
<section class="hero"><p class="muted">SIEVE · EVAL INFRASTRUCTURE AUDIT</p>
<h1>{html.escape(result.suite_name.upper())} · {result.task_count} tasks · {len(result.findings)} findings</h1>
<p class="band">TRUST-ADJUSTED SCORE · {band['reported']:.0%} could be {band['low']:.0%}–{band['high']:.0%}</p>
<p>Budget {result.budget['used']}/{result.budget['limit']} runs · skipped {result.budget['skipped']} ·
$0 · keyless · abstention {result.abstention_rate:.1%}</p>
<p class="muted">The band is a sensitivity calculation, not a CI. FP is a lower bound over constructed mutations.</p>
</section><h2>Findings</h2><section class="grid">{finding_cards}</section>
<h2>Measured grader FP/FN · Wilson 95% CI</h2>
<table><tr><th>task</th><th>FP count</th><th>FP rate [CI]</th><th>FN count</th><th>FN rate [CI]</th></tr>{rows}</table>
<p class="muted">Generated deterministically by local scripted probes.</p>
</main></body></html>"""
    destination = Path(output)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(document, encoding="utf-8")
    return destination

