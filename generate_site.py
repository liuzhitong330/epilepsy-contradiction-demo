"""
generate_site.py
Reads papers.json, claims.json, contradictions.json and produces a
self-contained index.html with all data embedded as JS variables.
"""

import json
from pathlib import Path

BASE = Path(__file__).parent

with open(BASE / "papers.json",         encoding="utf-8") as f: PAPERS         = json.load(f)
with open(BASE / "claims.json",         encoding="utf-8") as f: CLAIMS_RAW     = json.load(f)
with open(BASE / "contradictions.json", encoding="utf-8") as f: CONTRADICTIONS = json.load(f)
with open(BASE / "candidates.json",     encoding="utf-8") as f: CANDIDATES     = json.load(f)

FLAT_CLAIMS = []
for paper in CLAIMS_RAW:
    for claim in paper.get("claims", []):
        FLAT_CLAIMS.append({
            "pmid":          paper["pmid"],
            "subject":       claim.get("subject", ""),
            "direction":     claim.get("direction", ""),
            "effect":        claim.get("effect", ""),
            "model":         claim.get("condition", {}).get("model", "unknown"),
            "cell_type":     claim.get("condition", {}).get("cell_type", "unknown"),
            "epilepsy_type": claim.get("condition", {}).get("epilepsy_type", "unknown"),
            "confidence":    claim.get("confidence", ""),
            "method":        ", ".join(claim.get("method", [])),
        })

n_papers         = len(PAPERS)
n_claims         = len(FLAT_CLAIMS)
n_candidates     = len(CANDIDATES)
n_contradictions = len(CONTRADICTIONS)

j_claims         = json.dumps(FLAT_CLAIMS,    ensure_ascii=False)
j_contradictions = json.dumps(CONTRADICTIONS, ensure_ascii=False)

HTML = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>EpiContradiction</title>
<style>
*,*::before,*::after{{box-sizing:border-box;margin:0;padding:0}}
:root{{
  --accent:#1D9E75;--accent-light:#e8f7f2;--accent-dark:#16795a;
  --text:#1a1a1a;--muted:#6b7280;--border:#e5e7eb;--bg:#fff;
  --radius:10px;--shadow:0 2px 16px rgba(0,0,0,.07);
  --code-bg:#0f1117;--code-text:#e2e8f0;
}}
html{{scroll-behavior:smooth;font-family:system-ui,-apple-system,sans-serif;color:var(--text);font-size:16px}}
body{{background:var(--bg);line-height:1.65}}
a{{color:var(--accent);text-decoration:none}}
a:hover{{text-decoration:underline}}

/* NAV */
nav{{
  position:sticky;top:0;z-index:200;background:rgba(255,255,255,.93);
  backdrop-filter:blur(10px);border-bottom:1px solid var(--border);
  padding:0 2rem;display:flex;align-items:center;justify-content:space-between;height:54px;
}}
.nav-brand{{font-weight:800;font-size:1rem;color:var(--accent);letter-spacing:-.4px}}
.nav-links{{display:flex;gap:1.6rem;list-style:none}}
.nav-links a{{font-size:.85rem;color:var(--muted);transition:color .15s;font-weight:500}}
.nav-links a:hover{{color:var(--accent);text-decoration:none}}
@media(max-width:640px){{.nav-links{{gap:.8rem}}.nav-links a{{font-size:.78rem}}}}

/* SECTIONS */
section{{padding:5rem 1.5rem}}
.container{{max-width:1060px;margin:0 auto}}
.section-label{{
  font-size:.72rem;font-weight:700;text-transform:uppercase;letter-spacing:.1em;
  color:var(--accent);margin-bottom:.7rem;
}}
h2{{font-size:1.9rem;font-weight:800;letter-spacing:-.5px;margin-bottom:.5rem;line-height:1.2}}
.section-sub{{color:var(--muted);margin-bottom:2.5rem;font-size:1rem;max-width:640px}}

/* HERO */
#hero{{
  min-height:calc(100vh - 54px);display:flex;align-items:center;
  background:linear-gradient(160deg,#f0faf6 0%,#fff 55%);
  padding:4rem 1.5rem;
}}
.hero-inner{{max-width:820px}}
.hero-tag{{
  display:inline-block;background:var(--accent-light);color:var(--accent-dark);
  font-size:.78rem;font-weight:700;padding:.3rem .8rem;border-radius:999px;
  text-transform:uppercase;letter-spacing:.07em;margin-bottom:1.5rem;
}}
#hero h1{{
  font-size:clamp(2.4rem,6vw,4rem);font-weight:900;letter-spacing:-2px;line-height:1.05;
  background:linear-gradient(135deg,var(--accent) 0%,#0f6b4e 100%);
  -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;
  margin-bottom:1.4rem;
}}
.hero-desc{{
  font-size:clamp(.95rem,2vw,1.15rem);color:#374151;max-width:680px;
  margin-bottom:1.2rem;line-height:1.7;
}}
.hero-meta{{
  font-size:.9rem;color:var(--muted);display:flex;flex-wrap:wrap;gap:.4rem .6rem;
  align-items:center;
}}
.hero-dot{{color:var(--border)}}
.hero-meta strong{{color:var(--text);font-weight:600}}
.hero-ctas{{display:flex;gap:.8rem;flex-wrap:wrap;margin-top:2.2rem}}
.btn-primary{{
  padding:.65rem 1.5rem;background:var(--accent);color:#fff;border-radius:8px;
  font-weight:600;font-size:.9rem;transition:background .15s;
}}
.btn-primary:hover{{background:var(--accent-dark);text-decoration:none}}
.btn-secondary{{
  padding:.65rem 1.5rem;background:#fff;color:var(--text);border-radius:8px;
  border:1.5px solid var(--border);font-weight:600;font-size:.9rem;transition:all .15s;
}}
.btn-secondary:hover{{border-color:var(--accent);color:var(--accent);text-decoration:none}}

/* PROBLEM */
#problem{{background:#f9fafb}}
.problem-paras{{display:grid;grid-template-columns:1fr 1fr 1fr;gap:2rem}}
@media(max-width:700px){{.problem-paras{{grid-template-columns:1fr}}}}
.problem-para{{border-top:3px solid var(--accent);padding-top:1rem}}
.problem-para p{{font-size:.95rem;color:#374151;line-height:1.7}}

/* ARCHITECTURE */
.arch-stages{{display:flex;flex-direction:column;gap:0;margin-bottom:2.5rem}}
.arch-stage{{
  display:grid;grid-template-columns:180px 1fr;
  border:1px solid var(--border);border-radius:var(--radius);
  overflow:hidden;background:#fff;box-shadow:var(--shadow);
}}
.arch-stage+.arch-stage{{margin-top:-1px;border-radius:0}}
.arch-stage:first-child{{border-radius:var(--radius) var(--radius) 0 0}}
.arch-stage:last-child{{border-radius:0 0 var(--radius) var(--radius)}}
.stage-num{{
  background:var(--accent-light);display:flex;flex-direction:column;
  align-items:center;justify-content:center;padding:1.4rem 1rem;
  border-right:1px solid var(--border);
}}
.stage-num-n{{
  font-size:1.6rem;font-weight:900;color:var(--accent);line-height:1;
}}
.stage-num-label{{font-size:.72rem;color:var(--accent-dark);font-weight:600;margin-top:.2rem;text-align:center}}
.stage-body{{padding:1.2rem 1.5rem}}
.stage-title{{font-size:1rem;font-weight:700;margin-bottom:.3rem}}
.stage-method{{
  font-size:.78rem;background:#f3f4f6;color:var(--muted);
  display:inline-block;padding:.15rem .5rem;border-radius:4px;margin-bottom:.7rem;
}}
.stage-io{{display:flex;flex-direction:column;gap:.3rem}}
.stage-io-row{{display:flex;gap:.5rem;align-items:baseline;font-size:.88rem}}
.io-label{{
  font-size:.7rem;font-weight:700;text-transform:uppercase;letter-spacing:.07em;
  color:var(--muted);min-width:44px;
}}
.io-val{{color:#374151}}
.substages{{display:flex;flex-direction:column;gap:.5rem;margin-top:.6rem}}
.substage{{
  background:#f9fafb;border-radius:6px;padding:.6rem .9rem;
  font-size:.84rem;border-left:3px solid var(--border);
}}
.substage strong{{color:var(--text)}}
@media(max-width:560px){{
  .arch-stage{{grid-template-columns:60px 1fr}}
  .stage-num-label{{display:none}}
}}

.tech-stack{{
  display:flex;flex-wrap:wrap;gap:.5rem;margin-top:1.5rem;
  padding:1rem 1.2rem;background:#f9fafb;border-radius:var(--radius);
  border:1px solid var(--border);align-items:center;
}}
.tech-label{{font-size:.78rem;font-weight:700;color:var(--muted);margin-right:.3rem;text-transform:uppercase;letter-spacing:.06em}}
.tech-tag{{
  background:#fff;border:1px solid var(--border);border-radius:999px;
  padding:.25rem .7rem;font-size:.8rem;color:var(--text);
}}

/* METRICS */
#metrics{{background:#f9fafb}}
.metrics-grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(210px,1fr));gap:1.2rem}}
.metric-card{{
  background:#fff;border:1px solid var(--border);border-radius:var(--radius);
  padding:1.6rem 1.4rem;box-shadow:var(--shadow);
}}
.metric-num{{font-size:2.6rem;font-weight:900;color:var(--accent);line-height:1;font-variant-numeric:tabular-nums}}
.metric-label{{font-size:.85rem;color:var(--muted);margin-top:.4rem}}

/* DEMO CASE */
#demo{{background:#f9fafb;color:var(--text)}}
#demo .section-label{{color:var(--accent)}}
#demo h2{{color:var(--text)}}
#demo .section-sub{{color:var(--muted)}}

.trace{{display:flex;flex-direction:column;gap:0;max-width:860px}}
.trace-step{{
  background:#fff;border:1px solid var(--border);border-radius:var(--radius);
  padding:1.4rem 1.6rem;position:relative;box-shadow:var(--shadow);
}}
.trace-step-header{{
  display:flex;align-items:center;gap:.8rem;margin-bottom:1rem;
}}
.trace-step-num{{
  width:28px;height:28px;border-radius:50%;background:var(--accent);
  color:#fff;font-weight:800;font-size:.85rem;display:flex;align-items:center;
  justify-content:center;flex-shrink:0;
}}
.trace-step-title{{font-size:.95rem;font-weight:700;color:var(--text)}}
.trace-step-method{{font-size:.75rem;color:var(--muted);font-family:monospace;margin-left:.3rem}}

.trace-arrow{{
  display:flex;justify-content:center;align-items:center;
  padding:.5rem 0;color:var(--accent);font-size:1.4rem;font-weight:700;
}}

/* abstract excerpts */
.abstract-grid{{display:grid;grid-template-columns:1fr 1fr;gap:1rem}}
@media(max-width:640px){{.abstract-grid{{grid-template-columns:1fr}}}}
.abstract-box{{
  background:#f9fafb;border-radius:8px;padding:1rem 1.2rem;
  border:1px solid var(--border);
}}
.abstract-box-label{{
  font-size:.7rem;font-weight:700;text-transform:uppercase;letter-spacing:.08em;
  color:var(--muted);margin-bottom:.5rem;
}}
.abstract-pmid{{
  font-size:.78rem;font-family:monospace;color:var(--accent);margin-bottom:.5rem;display:block;
}}
.abstract-text{{font-size:.85rem;color:#374151;line-height:1.65;font-style:italic}}

/* code blocks in demo */
.code-grid{{display:grid;grid-template-columns:1fr 1fr;gap:1rem}}
@media(max-width:640px){{.code-grid{{grid-template-columns:1fr}}}}
.code-block{{background:#1e2a3a;border-radius:8px;overflow:hidden;border:1px solid #2d3748}}
.code-block-label{{
  background:#162032;padding:.5rem 1rem;font-size:.72rem;font-weight:700;
  text-transform:uppercase;letter-spacing:.08em;color:#6b7280;border-bottom:1px solid #2d3748;
}}
.code-block pre{{
  padding:1rem 1.2rem;font-size:.82rem;line-height:1.7;
  color:#e2e8f0;overflow-x:auto;margin:0;background:transparent;border-radius:0;
}}

/* rule engine output */
.rule-output{{display:flex;flex-direction:column;gap:.6rem}}
.rule-row{{
  display:flex;align-items:center;gap:.8rem;flex-wrap:wrap;
  background:#f9fafb;border-radius:6px;padding:.7rem 1rem;
  border:1px solid var(--border);font-size:.88rem;
}}
.rule-key{{color:var(--muted);font-family:monospace;min-width:130px;font-size:.8rem}}
.rule-val{{color:var(--text);font-family:monospace}}
.rule-pass{{
  margin-left:auto;background:#dcfce7;color:#15803d;
  padding:.15rem .6rem;border-radius:4px;font-size:.72rem;font-weight:700;
}}

/* final LLM output */
.llm-output{{background:#1e2a3a;border-radius:8px;padding:1.2rem 1.5rem;border:1px solid #2d3748}}
.llm-output pre{{font-size:.85rem;line-height:1.8;color:#e2e8f0;overflow-x:auto}}
.json-key{{color:#93c5fd}}
.json-str{{color:#86efac}}
.json-num{{color:#fbbf24}}

/* CLAIMS */
#claims{{background:#f9fafb}}
.explorer-controls{{display:flex;gap:.8rem;flex-wrap:wrap;margin-bottom:1rem;align-items:center}}
.search-box{{
  flex:1;min-width:200px;padding:.5rem .9rem;border:1.5px solid var(--border);
  border-radius:8px;font-size:.9rem;outline:none;transition:border-color .15s;background:#fff;
}}
.search-box:focus{{border-color:var(--accent)}}
.select-filter{{
  padding:.5rem .9rem;border:1.5px solid var(--border);border-radius:8px;
  font-size:.85rem;background:#fff;outline:none;cursor:pointer;
}}
.row-count{{font-size:.83rem;color:var(--muted);margin-bottom:.6rem}}
.claims-table-wrap{{
  overflow-x:auto;background:#fff;border-radius:var(--radius);
  border:1px solid var(--border);box-shadow:var(--shadow);
}}
table{{width:100%;border-collapse:collapse;font-size:.85rem}}
thead{{background:#f9fafb;position:sticky;top:54px}}
th{{
  padding:.7rem 1rem;text-align:left;font-weight:700;font-size:.75rem;
  text-transform:uppercase;letter-spacing:.06em;color:var(--muted);
  border-bottom:1px solid var(--border);
}}
td{{padding:.6rem 1rem;border-bottom:1px solid var(--border);vertical-align:top;max-width:240px}}
tr:last-child td{{border-bottom:none}}
tr:hover td{{background:#f9fafb}}
.pmid-link{{font-family:monospace;font-size:.8rem}}
.effect-cell{{white-space:normal;word-break:break-word}}
.dir-badge{{
  display:inline-block;padding:.1rem .5rem;border-radius:4px;
  font-size:.75rem;font-weight:600;white-space:nowrap;
}}
.dir-increases{{background:#dcfce7;color:#15803d}}
.dir-decreases{{background:#fee2e2;color:#dc2626}}
.dir-activates{{background:#dbeafe;color:#2563eb}}
.dir-inhibits{{background:#fed7aa;color:#c2410c}}
.dir-no-effect{{background:#f3f4f6;color:#6b7280}}
.dir-bidirectional{{background:#ede9fe;color:#7c3aed}}
.load-more-btn{{
  display:block;margin:1.2rem auto 0;padding:.6rem 2rem;
  background:var(--accent);color:#fff;border:none;border-radius:8px;
  font-size:.9rem;cursor:pointer;font-weight:600;transition:background .15s;
}}
.load-more-btn:hover{{background:var(--accent-dark)}}
.load-more-btn:disabled{{background:var(--border);cursor:default;color:var(--muted)}}

/* LIMITATIONS */
#limitations{{background:#fff}}
.lim-grid{{display:grid;grid-template-columns:1fr 1fr;gap:3rem}}
@media(max-width:640px){{.lim-grid{{grid-template-columns:1fr}}}}
.lim-col h3{{font-size:1.05rem;font-weight:700;margin-bottom:1rem;color:var(--text)}}
.lim-list{{list-style:none;display:flex;flex-direction:column;gap:.65rem}}
.lim-list li{{
  display:flex;gap:.7rem;align-items:flex-start;
  font-size:.9rem;color:#374151;line-height:1.5;
}}
.lim-icon{{flex-shrink:0;margin-top:.1rem;font-size:.9rem}}

/* FOOTER */
footer{{
  background:#0f1117;color:#6b7280;text-align:center;
  padding:2.5rem 1.5rem;font-size:.88rem;
}}
footer strong{{color:#e2e8f0}}
footer a{{color:var(--accent)}}
</style>
</head>
<body>

<!-- NAV -->
<nav>
  <span class="nav-brand">EpiContradiction</span>
  <ul class="nav-links">
    <li><a href="#problem">Problem</a></li>
    <li><a href="#architecture">Architecture</a></li>
    <li><a href="#demo">Demo</a></li>
    <li><a href="#claims">Claims</a></li>
    <li><a href="#limitations">Limitations</a></li>
  </ul>
</nav>

<!-- 1. HERO -->
<section id="hero">
  <div class="hero-inner container">
    <span class="hero-tag">Research Demo</span>
    <h1>EpiContradiction</h1>
    <p class="hero-desc">
      An automated pipeline that reads epilepsy research papers and surfaces
      contradictory findings using LLM-based claim extraction and rule-based
      contradiction detection.
    </p>
    <div class="hero-meta">
      <strong>{n_papers} papers</strong>
      <span class="hero-dot">·</span>
      <strong>{n_claims} claims extracted</strong>
      <span class="hero-dot">·</span>
      <strong>{n_contradictions} confirmed contradiction</strong>
      <span class="hero-dot">·</span>
      Built by Cathy Liu
    </div>
    <div class="hero-ctas">
      <a class="btn-primary" href="#demo">See it in action</a>
      <a class="btn-secondary" href="#claims">Explore claims</a>
    </div>
  </div>
</section>

<!-- 2. PROBLEM -->
<section id="problem">
  <div class="container">
    <div class="section-label">Background</div>
    <h2>The problem</h2>
    <div class="problem-paras" style="margin-top:2rem">
      <div class="problem-para">
        <p>Epilepsy research spans thousands of papers across different model organisms, cell types, and disease subtypes. A finding in mouse granule cells may directly contradict a finding in human TSC tissue — but no human researcher reads everything.</p>
      </div>
      <div class="problem-para">
        <p>Contradictions between published findings represent the most valuable signal in a literature: they point to unknown variables, boundary conditions, and unresolved mechanisms. But they are nearly impossible to find manually at scale.</p>
      </div>
      <div class="problem-para">
        <p>EpiContradiction automates this process: structured claim extraction → pairwise contradiction detection → ranked output with experiment suggestions.</p>
      </div>
    </div>
  </div>
</section>

<!-- 3. ARCHITECTURE -->
<section id="architecture">
  <div class="container">
    <div class="section-label">System Design</div>
    <h2>How it works</h2>
    <p class="section-sub">Four automated stages from raw literature search to ranked, verified contradictions.</p>

    <div class="arch-stages">
      <div class="arch-stage">
        <div class="stage-num">
          <div class="stage-num-n">1</div>
          <div class="stage-num-label">Retrieval</div>
        </div>
        <div class="stage-body">
          <div class="stage-title">Literature Retrieval</div>
          <span class="stage-method">PubMed Entrez API · Biopython · Rate-limited (3 req/s) · Parallel threads</span>
          <div class="stage-io">
            <div class="stage-io-row"><span class="io-label">Input</span><span class="io-val">7 domain-specific search queries · last 10 years · abstracts ≥ 150 words</span></div>
            <div class="stage-io-row"><span class="io-label">Output</span><span class="io-val"><strong>{n_papers} deduplicated papers</strong> tagged with matched search terms (papers.json)</span></div>
          </div>
        </div>
      </div>

      <div class="arch-stage">
        <div class="stage-num">
          <div class="stage-num-n">2</div>
          <div class="stage-num-label">Extraction</div>
        </div>
        <div class="stage-body">
          <div class="stage-title">Claim Extraction</div>
          <span class="stage-method">Claude Sonnet · JSON schema enforcement · Batched (10/batch) · Resumable</span>
          <div class="stage-io">
            <div class="stage-io-row"><span class="io-label">Input</span><span class="io-val">Abstract text per paper with structured system prompt</span></div>
            <div class="stage-io-row"><span class="io-label">Output</span><span class="io-val"><strong>{n_claims} mechanistic claims</strong> — each with subject / direction / effect / condition / confidence (claims.json)</span></div>
          </div>
        </div>
      </div>

      <div class="arch-stage">
        <div class="stage-num">
          <div class="stage-num-n">3</div>
          <div class="stage-num-label">Detection</div>
        </div>
        <div class="stage-body">
          <div class="stage-title">Contradiction Detection</div>
          <span class="stage-method">2-stage: rule-based pre-filter + LLM judge</span>
          <div class="substages">
            <div class="substage">
              <strong>3a — Rule engine:</strong> subject fuzzy match (substring) + opposing direction pairs (increases↔decreases, activates↔inhibits) + effect word overlap filter. Deduplicates by PMID pair, keeps highest-scoring claim match.
            </div>
            <div class="substage">
              <strong>3b — LLM judge:</strong> each candidate pair classified as <em>true_contradiction / conditional_contradiction / terminology_mismatch / not_contradictory</em> with explanation and resolving experiment suggestion.
            </div>
          </div>
          <div class="stage-io" style="margin-top:.7rem">
            <div class="stage-io-row"><span class="io-label">Input</span><span class="io-val">1,634 × 1,634 claim comparisons → {n_candidates} candidates after filters</span></div>
            <div class="stage-io-row"><span class="io-label">Output</span><span class="io-val"><strong>{n_contradictions} confirmed contradiction</strong> (contradictions.json)</span></div>
          </div>
        </div>
      </div>

      <div class="arch-stage">
        <div class="stage-num">
          <div class="stage-num-n">4</div>
          <div class="stage-num-label">Output</div>
        </div>
        <div class="stage-body">
          <div class="stage-title">Ranked Output</div>
          <span class="stage-method">Interest scoring · match score + LLM confidence + experiment feasibility</span>
          <div class="stage-io">
            <div class="stage-io-row"><span class="io-label">Output</span><span class="io-val">contradiction_report.md · this interactive web report</span></div>
          </div>
        </div>
      </div>
    </div>

    <div class="tech-stack">
      <span class="tech-label">Tech stack</span>
      <span class="tech-tag">PubMed API</span>
      <span class="tech-tag">Biopython</span>
      <span class="tech-tag">Claude Sonnet (Anthropic)</span>
      <span class="tech-tag">Python</span>
      <span class="tech-tag">Rule-based NLP</span>
      <span class="tech-tag">JSON schema extraction</span>
    </div>
  </div>
</section>

<!-- 4. METRICS -->
<section id="metrics">
  <div class="container">
    <div class="section-label">By the numbers</div>
    <h2>Pipeline output</h2>
    <p class="section-sub" style="margin-bottom:2rem">Results from a single run against 7 epilepsy search terms, 2025–2026 publications.</p>
    <div class="metrics-grid">
      <div class="metric-card">
        <div class="metric-num" data-target="{n_papers}">0</div>
        <div class="metric-label">Papers fetched from PubMed</div>
      </div>
      <div class="metric-card">
        <div class="metric-num" data-target="{n_claims}">0</div>
        <div class="metric-label">Mechanistic claims extracted</div>
      </div>
      <div class="metric-card">
        <div class="metric-num" data-target="{n_candidates}">0</div>
        <div class="metric-label">Candidate contradiction pairs</div>
      </div>
      <div class="metric-card">
        <div class="metric-num" data-target="{n_contradictions}">0</div>
        <div class="metric-label">Contradictions confirmed by LLM</div>
      </div>
    </div>
  </div>
</section>

<!-- 5. DEMO CASE -->
<section id="demo">
  <div class="container">
    <div class="section-label">End-to-end trace</div>
    <h2>A real contradiction, found automatically</h2>
    <p class="section-sub">
      Every step the pipeline executed to surface this finding — from raw abstract to classified contradiction.
    </p>

    <div class="trace">

      <!-- STEP 1: raw abstracts -->
      <div class="trace-step">
        <div class="trace-step-header">
          <div class="trace-step-num">1</div>
          <span class="trace-step-title">Raw input</span>
          <span class="trace-step-method">fetch_pubmed.py → papers.json</span>
        </div>
        <div class="abstract-grid">
          <div class="abstract-box">
            <div class="abstract-box-label">Paper A abstract</div>
            <a class="abstract-pmid" href="https://pubmed.ncbi.nlm.nih.gov/41835966" target="_blank">PMID 41835966 · Front Cell Neurosci 2026</a>
            <p class="abstract-text">"Down syndrome is the most common genetic neurodevelopmental disorder associated with mild-to-moderate intellectual disability. A disturbed excitation-inhibition balance is thought to be a major cause for the intellectual deficits in DS. In this study, we used patch-clamp electrophysiology, optogenetic stimulation and immunohistochemistry to investigate synaptic inhibition from specific interneuron subpopulations onto granule cells of the dentate gyrus in Ts65Dn mice."</p>
          </div>
          <div class="abstract-box">
            <div class="abstract-box-label">Paper B abstract</div>
            <a class="abstract-pmid" href="https://pubmed.ncbi.nlm.nih.gov/41352576" target="_blank">PMID 41352576 · Prog Neurobiol 2026</a>
            <p class="abstract-text">"Somatostatin (SST), a neuropeptide primarily synthesized by GABAergic interneurons, modulates neuronal excitability and synaptic transmission through its interaction with somatostatin receptors (SSTRs). Dysregulation of SST signaling has been implicated in neurodevelopmental disorders, including tuberous sclerosis complex (TSC). However, its precise role in these pathologies remains incompletely understood."</p>
          </div>
        </div>
      </div>

      <div class="trace-arrow">↓</div>

      <!-- STEP 2: extracted claims -->
      <div class="trace-step">
        <div class="trace-step-header">
          <div class="trace-step-num">2</div>
          <span class="trace-step-title">Extracted claims</span>
          <span class="trace-step-method">extract_claims.py → Claude Sonnet → claims.json</span>
        </div>
        <div class="code-grid">
          <div class="code-block">
            <div class="code-block-label">Paper A claim</div>
            <pre><span class="json-key">"subject"</span>:   <span class="json-str">"somatostatin interneurons"</span>,
<span class="json-key">"direction"</span>: <span class="json-str">"no-effect"</span>,
<span class="json-key">"effect"</span>:    <span class="json-str">"inhibitory postsynaptic
             currents onto granule cells"</span>,
<span class="json-key">"condition"</span>: &#123;
  <span class="json-key">"model"</span>:         <span class="json-str">"mouse"</span>,
  <span class="json-key">"cell_type"</span>:     <span class="json-str">"granule cells"</span>,
  <span class="json-key">"epilepsy_type"</span>: <span class="json-str">"unknown"</span>
&#125;,
<span class="json-key">"confidence"</span>: <span class="json-str">"primary finding"</span></pre>
          </div>
          <div class="code-block">
            <div class="code-block-label">Paper B claim</div>
            <pre><span class="json-key">"subject"</span>:   <span class="json-str">"somatostatin"</span>,
<span class="json-key">"direction"</span>: <span class="json-str">"decreases"</span>,
<span class="json-key">"effect"</span>:    <span class="json-str">"suppression of
             GABAergic currents"</span>,
<span class="json-key">"condition"</span>: &#123;
  <span class="json-key">"model"</span>:         <span class="json-str">"in-vitro"</span>,
  <span class="json-key">"cell_type"</span>:     <span class="json-str">"unknown"</span>,
  <span class="json-key">"epilepsy_type"</span>: <span class="json-str">"tuberous sclerosis
                   complex"</span>
&#125;,
<span class="json-key">"confidence"</span>: <span class="json-str">"primary finding"</span></pre>
          </div>
        </div>
      </div>

      <div class="trace-arrow">↓</div>

      <!-- STEP 3: rule engine -->
      <div class="trace-step">
        <div class="trace-step-header">
          <div class="trace-step-num">3</div>
          <span class="trace-step-title">Rule engine output</span>
          <span class="trace-step-method">detect_contradictions.py → Stage 3a</span>
        </div>
        <div class="rule-output">
          <div class="rule-row">
            <span class="rule-key">subject_match</span>
            <span class="rule-val">"somatostatin interneurons" ⊇ "somatostatin" (substring match)</span>
            <span class="rule-pass">✓ PASS</span>
          </div>
          <div class="rule-row">
            <span class="rule-key">direction_pair</span>
            <span class="rule-val">no-effect ↔ decreases (opposing)</span>
            <span class="rule-pass">✓ PASS</span>
          </div>
          <div class="rule-row">
            <span class="rule-key">effect_overlap</span>
            <span class="rule-val">shared word: "currents" (GABAergic / inhibitory)</span>
            <span class="rule-pass">✓ PASS</span>
          </div>
          <div class="rule-row">
            <span class="rule-key">match_score</span>
            <span class="rule-val">+2 same model organism · +0 cell type · <strong style="color:var(--accent)">score = 1 / 6</strong></span>
          </div>
        </div>
      </div>

      <div class="trace-arrow">↓</div>

      <!-- STEP 4: LLM output -->
      <div class="trace-step">
        <div class="trace-step-header">
          <div class="trace-step-num">4</div>
          <span class="trace-step-title">LLM classification</span>
          <span class="trace-step-method">detect_contradictions.py → Stage 3b → Claude Sonnet</span>
        </div>
        <div class="llm-output">
          <pre>&#123;
  <span class="json-key">"contradiction_type"</span>: <span class="json-str">"conditional_contradiction"</span>,
  <span class="json-key">"confidence"</span>:         <span class="json-str">"medium"</span>,
  <span class="json-key">"explanation"</span>:       <span class="json-str">"The findings differ in experimental systems —
                        Paper A shows somatostatin interneurons have no
                        effect on inhibitory currents in mouse granule
                        cells, while Paper B shows somatostatin decreases
                        GABAergic currents in human TSC pathological tissue.
                        Somatostatin's GABAergic modulatory role may be
                        specifically disrupted in TSC."</span>,
  <span class="json-key">"resolving_experiment"</span>: <span class="json-str">"Patch-clamp recordings on granule
                           cells from TSC mouse models vs wild-type
                           controls using identical protocol to Paper A."</span>,
  <span class="json-key">"interest_score"</span>:    <span class="json-num">7</span>
&#125;</pre>
        </div>
      </div>

    </div><!-- /trace -->
  </div>
</section>

<!-- 6. CLAIMS EXPLORER -->
<section id="claims">
  <div class="container">
    <div class="section-label">Data</div>
    <h2>Claims explorer</h2>
    <p class="section-sub">Browse all {n_claims} mechanistic claims extracted from the corpus.</p>
    <div class="explorer-controls">
      <input class="search-box" id="claim-search" type="text" placeholder="Search subject, effect, PMID…">
      <select class="select-filter" id="dir-filter">
        <option value="">All directions</option>
        <option value="increases">increases</option>
        <option value="decreases">decreases</option>
        <option value="activates">activates</option>
        <option value="inhibits">inhibits</option>
        <option value="no-effect">no-effect</option>
        <option value="bidirectional">bidirectional</option>
      </select>
      <select class="select-filter" id="model-filter">
        <option value="">All models</option>
        <option value="mouse">mouse</option>
        <option value="human">human</option>
        <option value="rat">rat</option>
        <option value="in-vitro">in-vitro</option>
        <option value="computational">computational</option>
      </select>
    </div>
    <div class="row-count" id="row-count"></div>
    <div class="claims-table-wrap">
      <table>
        <thead>
          <tr>
            <th>PMID</th><th>Subject</th><th>Direction</th>
            <th>Effect</th><th>Model</th><th>Epilepsy type</th>
          </tr>
        </thead>
        <tbody id="claims-tbody"></tbody>
      </table>
    </div>
    <button class="load-more-btn" id="load-more">Load more</button>
  </div>
</section>

<!-- 7. LIMITATIONS -->
<section id="limitations">
  <div class="container">
    <div class="section-label">Honest assessment</div>
    <h2>Limitations &amp; future work</h2>
    <p class="section-sub">What this system does well and where it falls short.</p>
    <div class="lim-grid">
      <div>
        <h3>Current limitations</h3>
        <ul class="lim-list">
          <li><span class="lim-icon">⚠️</span><span>Abstract-only analysis — full text not accessed, missing methods sections and results tables</span></li>
          <li><span class="lim-icon">⚠️</span><span>2025–2026 publication window only — insufficient time for contradictions to accumulate in the literature</span></li>
          <li><span class="lim-icon">⚠️</span><span>Fuzzy substring matching misses synonyms (Nav1.1 vs SCN1A, GABA-A vs GABA receptor)</span></li>
          <li><span class="lim-icon">⚠️</span><span>No embedding-based semantic similarity — entity resolution is purely lexical</span></li>
          <li><span class="lim-icon">⚠️</span><span>Single domain (epilepsy only) — cross-disease signal not captured</span></li>
        </ul>
      </div>
      <div>
        <h3>Planned extensions</h3>
        <ul class="lim-list">
          <li><span class="lim-icon">→</span><span>Full-text PDF parsing via PubMed Central Open Access API</span></li>
          <li><span class="lim-icon">→</span><span>Embedding-based entity resolution with BioBERT for synonym handling</span></li>
          <li><span class="lim-icon">→</span><span>Expand to 10-year window for richer contradiction mining</span></li>
          <li><span class="lim-icon">→</span><span>Cross-disease contradiction detection (epilepsy ↔ Alzheimer's, ASD)</span></li>
          <li><span class="lim-icon">→</span><span>Knowledge graph visualization of the full claim network</span></li>
        </ul>
      </div>
    </div>
  </div>
</section>

<!-- FOOTER -->
<footer>
  <p>
    <strong>EpiContradiction</strong> — Cathy Liu ·
    Built with PubMed API + <strong>Claude Sonnet</strong> (Anthropic)
  </p>
  <p style="margin-top:.6rem">
    <a href="contradiction_report.md">View full contradiction report →</a>
  </p>
</footer>

<!-- DATA + JS -->
<script>
const CLAIMS = {j_claims};
const CONTRADICTIONS = {j_contradictions};

// animated counters
function animateCounter(el) {{
  const target = +el.dataset.target;
  const dur = 1400, start = performance.now();
  const tick = now => {{
    const p = Math.min((now-start)/dur,1);
    const e = 1-Math.pow(1-p,3);
    el.textContent = Math.floor(e*target).toLocaleString();
    if(p<1) requestAnimationFrame(tick);
    else el.textContent = target.toLocaleString();
  }};
  requestAnimationFrame(tick);
}}
const obs = new IntersectionObserver(entries => {{
  entries.forEach(e => {{ if(e.isIntersecting){{ animateCounter(e.target); obs.unobserve(e.target); }} }});
}}, {{threshold:0.5}});
document.querySelectorAll('.metric-num[data-target]').forEach(el => obs.observe(el));

// direction badge
function dirBadge(dir) {{
  const map = {{
    increases:'dir-increases',decreases:'dir-decreases',
    activates:'dir-activates',inhibits:'dir-inhibits',
    'no-effect':'dir-no-effect',bidirectional:'dir-bidirectional'
  }};
  return `<span class="dir-badge ${{map[dir]||'dir-no-effect'}}">${{dir||'—'}}</span>`;
}}

// claims explorer
let page = 0;
const PG = 50;
let filtered = CLAIMS;

function getFiltered() {{
  const q = document.getElementById('claim-search').value.toLowerCase();
  const d = document.getElementById('dir-filter').value;
  const m = document.getElementById('model-filter').value;
  return CLAIMS.filter(c => {{
    if(d && c.direction!==d) return false;
    if(m && c.model!==m) return false;
    if(q && !(c.pmid+c.subject+c.effect+c.epilepsy_type).toLowerCase().includes(q)) return false;
    return true;
  }});
}}

function renderRows() {{
  const slice = filtered.slice(0,(page+1)*PG);
  document.getElementById('claims-tbody').innerHTML = slice.map(c=>`
    <tr>
      <td><a class="pmid-link" href="https://pubmed.ncbi.nlm.nih.gov/${{c.pmid}}" target="_blank">${{c.pmid}}</a></td>
      <td>${{c.subject||'—'}}</td>
      <td>${{dirBadge(c.direction)}}</td>
      <td class="effect-cell">${{c.effect||'—'}}</td>
      <td>${{c.model||'—'}}</td>
      <td>${{c.epilepsy_type||'—'}}</td>
    </tr>`).join('');
  document.getElementById('row-count').textContent =
    `Showing ${{Math.min(slice.length,filtered.length)}} of ${{filtered.length}} claims`;
  const btn = document.getElementById('load-more');
  btn.disabled = slice.length>=filtered.length;
  btn.textContent = btn.disabled ? 'All claims loaded'
    : `Load more (${{filtered.length-slice.length}} remaining)`;
}}

function refresh(reset) {{
  if(reset) page=0;
  filtered = getFiltered();
  renderRows();
}}

document.getElementById('claim-search').addEventListener('input', ()=>refresh(true));
document.getElementById('dir-filter').addEventListener('change', ()=>refresh(true));
document.getElementById('model-filter').addEventListener('change', ()=>refresh(true));
document.getElementById('load-more').addEventListener('click', ()=>{{page++;renderRows();}});
refresh(true);
</script>
</body>
</html>"""

out = BASE / "index.html"
out.write_text(HTML, encoding="utf-8")
print("Site generated. Open index.html in your browser.")
print(f"  Papers: {n_papers}  |  Claims: {n_claims}  |  Candidates: {n_candidates}  |  Contradictions: {n_contradictions}")
print(f"  Output: {out}")
