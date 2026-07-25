from __future__ import annotations

import html
from pathlib import Path

from .models import AuditResult

STYLE = """
:root{
  --bg:#0b0c09;--panel:#141610;--panel-2:#1a1d14;--line:#34382a;
  --text:#faf9ef;--muted:#a6a68e;--faint:#6f725e;--yellow:#e8ee72;
  --amber:#f2bd63;--coral:#ff7e69;--green:#7ae3a2;--cyan:#6dd5d4;
  --shadow:0 26px 74px rgba(0,0,0,.42)
}
*{box-sizing:border-box}html{scroll-behavior:smooth}body{margin:0;color:var(--text);
background:radial-gradient(circle at 78% -8%,rgba(232,238,114,.12),transparent 30rem),
linear-gradient(rgba(232,238,114,.02) 1px,transparent 1px),
linear-gradient(90deg,rgba(232,238,114,.02) 1px,transparent 1px),var(--bg);
background-size:auto,34px 34px,34px 34px;font:14px/1.55 Inter,ui-sans-serif,
-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}.topbar{height:58px;padding:0 26px;
display:flex;align-items:center;justify-content:space-between;border-bottom:1px solid var(--line);
position:sticky;top:0;z-index:10;background:rgba(11,12,9,.88);backdrop-filter:blur(16px)}
.brand{display:flex;align-items:center;gap:11px;font-weight:780}.brand-mark{width:27px;height:27px;
border-radius:8px;display:grid;place-items:center;background:linear-gradient(145deg,var(--yellow),
var(--amber));color:#141409;box-shadow:0 0 23px rgba(232,238,114,.22)}.topmeta{display:flex;
gap:14px;align-items:center;color:var(--muted);font:10px ui-monospace,monospace;
letter-spacing:.11em;text-transform:uppercase}.complete{display:flex;align-items:center;gap:7px;
color:#c7f0d5}.complete:before{content:"";width:6px;height:6px;border-radius:50%;
background:var(--green);box-shadow:0 0 12px var(--green)}main{max-width:1360px;margin:auto;
padding:30px 26px 64px}.hero{display:grid;grid-template-columns:minmax(0,1.15fr)
minmax(380px,.85fr);border:1px solid var(--line);border-radius:18px;overflow:hidden;
background:linear-gradient(145deg,rgba(27,30,21,.98),rgba(13,15,10,.98));box-shadow:var(--shadow)}
.hero-copy{padding:36px 38px}.eyebrow,.section-label{margin:0 0 13px;color:var(--yellow);
font:750 10px ui-monospace,monospace;text-transform:uppercase;letter-spacing:.16em}
.eyebrow:before{content:"";display:inline-block;width:24px;height:1px;background:currentColor;
vertical-align:middle;margin-right:9px}h1{font-size:clamp(36px,4.7vw,62px);line-height:1;
letter-spacing:-.05em;margin:0}.lede{font-size:17px;color:#c0c0ad;max-width:740px;margin:20px 0 0}
.band-panel{border-left:1px solid var(--line);padding:29px;background:rgba(8,9,6,.28)}
.band-value{font-size:40px;line-height:1;letter-spacing:-.045em;font-weight:780}
.band-value span{color:var(--muted);font-size:14px;font-weight:500}.band-track{height:14px;
position:relative;border:1px solid var(--line);border-radius:999px;background:#0b0c09;margin:27px 0 9px}
.band-range{position:absolute;top:2px;bottom:2px;border-radius:999px;
background:linear-gradient(90deg,var(--coral),var(--yellow));box-shadow:0 0 16px rgba(232,238,114,.2)}
.band-marker{position:absolute;top:50%;width:12px;height:20px;border:3px solid #15170f;
border-radius:5px;background:#fff;transform:translate(-50%,-50%);box-shadow:0 0 0 1px #696d55}
.scale{display:flex;justify-content:space-between;color:var(--faint);font:9px ui-monospace,monospace}
.band-panel p{color:var(--muted);font-size:11px;margin:20px 0 0}.audit-strip{display:grid;
grid-template-columns:repeat(5,minmax(0,1fr));gap:1px;background:var(--line);border:1px solid var(--line);
border-radius:13px;overflow:hidden;margin:17px 0}.audit-metric{background:#12140e;padding:15px}
.audit-metric strong{display:block;font-size:20px;line-height:1.15}.audit-metric span{display:block;
color:var(--muted);font-size:9px;text-transform:uppercase;letter-spacing:.1em;margin-top:7px}
.section-head{display:flex;align-items:end;justify-content:space-between;gap:20px;margin:28px 0 12px}
.section-head h2{margin:0;font-size:22px}.section-head>p{margin:0;color:var(--muted)}
.grid{display:grid;grid-template-columns:repeat(5,minmax(190px,1fr));gap:10px}.card{border:1px
solid var(--line);border-radius:14px;background:linear-gradient(180deg,rgba(21,23,16,.98),
rgba(13,15,10,.98));padding:16px;min-height:245px;display:flex;flex-direction:column}
.finding-top{display:flex;align-items:center;justify-content:space-between;gap:8px}.task-id{color:var(--faint);
font:700 9px ui-monospace,monospace;text-transform:uppercase;letter-spacing:.09em}.severity{padding:4px 7px;
border-radius:999px;font:750 8px ui-monospace,monospace;text-transform:uppercase;letter-spacing:.08em;
border:1px solid #613126;background:#371b17;color:#ffa192}.card h3{font-size:16px;line-height:1.25;
letter-spacing:-.015em;margin:19px 0 11px;color:var(--yellow)}.card p{color:#bfc0aa;margin:0 0 13px}
.evidence{display:grid;gap:5px;margin-top:auto;color:var(--muted);font:9px ui-monospace,monospace;
text-transform:uppercase;letter-spacing:.07em}.evidence span{display:flex;justify-content:space-between;
gap:10px}.evidence strong{color:#d6d8c3}.card code{display:block;margin-top:13px;padding:8px;
border:1px solid var(--line);border-radius:7px;background:#0b0c09;color:#adb09a;font:9px/1.45
ui-monospace,monospace;overflow-wrap:anywhere}.panel{border:1px solid var(--line);border-radius:15px;
background:linear-gradient(180deg,rgba(21,23,16,.98),rgba(12,14,9,.98));overflow:hidden}
.panel-head{padding:18px 20px;border-bottom:1px solid var(--line);display:flex;align-items:end;
justify-content:space-between;gap:16px}.panel-head h2{margin:0;font-size:21px}.panel-head span{color:var(--muted);
font-size:11px}.scroll{overflow:auto;max-height:570px}table{border-collapse:collapse;width:100%;
font-size:12px}th,td{border-bottom:1px solid var(--line);padding:11px 13px;text-align:left}
th{position:sticky;top:0;background:#191c13;color:var(--faint);font:700 9px
ui-monospace,monospace;text-transform:uppercase;letter-spacing:.1em}tbody tr:hover{background:
rgba(232,238,114,.03)}.rate{font:700 11px ui-monospace,monospace}.footer{display:flex;
justify-content:space-between;gap:20px;border-top:1px solid var(--line);margin-top:22px;
padding-top:17px;color:var(--muted);font-size:12px}@media(max-width:1150px){.grid{
grid-template-columns:repeat(3,1fr)}}@media(max-width:900px){.hero{grid-template-columns:1fr}
.band-panel{border-left:0;border-top:1px solid var(--line)}.audit-strip{grid-template-columns:
repeat(3,1fr)}}@media(max-width:650px){.topbar{padding:0 14px}.topmeta>span:first-child{display:none}
main{padding:18px 14px 42px}.hero-copy,.band-panel{padding:24px 20px}.audit-strip{
grid-template-columns:1fr 1fr}.grid{grid-template-columns:1fr}.section-head,.footer{
align-items:start;flex-direction:column}}
"""


def render(result: AuditResult, output: str | Path) -> Path:
    finding_cards = "".join(
        f"""<article class="card"><div class="finding-top">
        <span class="task-id">{html.escape(item.task_id)}</span>
        <span class="severity">{html.escape(item.severity)}</span></div>
        <h3>{html.escape(item.verdict)}</h3><p>{html.escape(item.detail)}</p>
        <div class="evidence"><span>secondary <strong>{html.escape(', '.join(item.secondary) or '—')}</strong></span>
        <span>evidence <strong>{html.escape(item.evidence_tier)}</strong></span>
        <span>FP lower bound <strong>{'yes' if item.fp_lower_bound else 'no'}</strong></span></div>
        <code>{html.escape(item.reproducer)}</code></article>"""
        for item in result.findings
    )
    rows = "".join(
        "<tr>"
        f"<td>{html.escape(task_id)}</td>"
        f"<td>{values['fp'].failures}/{values['fp'].trials}</td>"
        f"<td class='rate'>{values['fp'].rate:.1%} [{values['fp'].low:.1%}, {values['fp'].high:.1%}]</td>"
        f"<td>{values['fn'].failures}/{values['fn'].trials}</td>"
        f"<td class='rate'>{values['fn'].rate:.1%} [{values['fn'].low:.1%}, {values['fn'].high:.1%}]</td>"
        "</tr>"
        for task_id, values in result.grader_rates.items()
    )
    band = result.trust_band
    document = f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width"><title>SIEVE · {html.escape(result.suite_name)}</title>
<style>{STYLE}</style></head><body><header class="topbar"><div class="brand">
<span class="brand-mark">S</span>SIEVE</div><div class="topmeta">
<span>evaluator assurance / audit 001</span><span class="complete">audit complete</span>
</div></header><main><section class="hero"><div class="hero-copy">
<p class="eyebrow">Eval infrastructure audit · Journey 0</p>
<h1>{html.escape(result.suite_name)} under evidence.</h1>
<p class="lede">{result.task_count} tasks were challenged for solvability,
failability, label quality, and grader behavior. Every finding below retains
its evidence tier and exact reproducer.</p></div><aside class="band-panel">
<p class="section-label">Trust-adjusted sensitivity</p><div class="band-value">
{band['low']:.0%}–{band['high']:.0%} <span>from reported {band['reported']:.0%}</span></div>
<div class="band-track" aria-label="Reported score and trust-adjusted band">
<span class="band-range" style="left:{band['low'] * 100:.1f}%;width:{(band['high'] - band['low']) * 100:.1f}%"></span>
<span class="band-marker" style="left:{band['reported'] * 100:.1f}%"></span></div>
<div class="scale"><span>0%</span><span>reported score</span><span>100%</span></div>
<p>This is a transparent sensitivity band, not a confidence interval.</p>
</aside></section><section class="audit-strip" aria-label="Audit summary">
<div class="audit-metric"><strong>{len(result.findings)}</strong><span>findings</span></div>
<div class="audit-metric"><strong>{result.budget['used']}/{result.budget['limit']}</strong><span>probe budget</span></div>
<div class="audit-metric"><strong>{result.budget['skipped']}</strong><span>skipped probes</span></div>
<div class="audit-metric"><strong>{result.abstention_rate:.1%}</strong><span>abstention rate</span></div>
<div class="audit-metric"><strong>$0</strong><span>keyless run</span></div>
</section><div class="section-head"><div><p class="section-label">Defect register</p>
<h2>Findings</h2></div><p>Primary verdict · evidence · reproducer</p></div>
<section class="grid">{finding_cards}</section><div class="section-head"><div>
<p class="section-label">Grader calibration</p><h2>Measured FP/FN · Wilson 95% CI</h2>
</div><p>FP is a lower bound over constructed mutations.</p></div>
<section class="panel"><div class="panel-head"><h2>Per-task grader behavior</h2>
<span>counts before rates</span></div><div class="scroll"><table><thead><tr>
<th>task</th><th>FP count</th><th>FP rate [CI]</th><th>FN count</th><th>FN rate [CI]</th>
</tr></thead><tbody>{rows}</tbody></table></div></section>
<footer class="footer"><span>Generated deterministically by local scripted probes.</span>
<span>FlawedBench is synthetic regression evidence, not an external benchmark claim.</span></footer>
</main></body></html>"""
    destination = Path(output)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(document, encoding="utf-8")
    return destination
