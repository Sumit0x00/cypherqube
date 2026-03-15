import streamlit as st
import json
import pandas as pd
from pdf_report import generate_pdf_report
from PIL import Image

from scanner import analyze_target

# ─── Page Config (must be first Streamlit call) ───────────────────────────────

favicon = Image.open("favicon.png")

st.set_page_config(
    page_title="CypherQube — TLS Scanner",
    page_icon=favicon,
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ─── Global CSS ───────────────────────────────────────────────────────────────

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@300;400;500&family=IBM+Plex+Sans:wght@300;400;500;600&family=IBM+Plex+Sans+Condensed:wght@600;700&display=swap');

:root {
    --bg0:           #141414;
    --bg1:           #1c1c1c;
    --bg2:           #222222;
    --bg3:           #2a2a2a;
    --border:        #333333;
    --border-hi:     #444444;
    --text-1:        #e8e8e8;
    --text-2:        #a0a0a0;
    --text-3:        #606060;
    --red:           #e05252;
    --red-dim:       rgba(224,82,82,0.1);
    --red-border:    rgba(224,82,82,0.25);
    --amber:         #d4903a;
    --amber-dim:     rgba(212,144,58,0.09);
    --amber-border:  rgba(212,144,58,0.28);
    --green:         #52a878;
    --green-dim:     rgba(82,168,120,0.09);
    --green-border:  rgba(82,168,120,0.28);
    --blue:          #5b8db8;
    --blue-dim:      rgba(91,141,184,0.09);
    --blue-border:   rgba(91,141,184,0.28);
    --font-sans:     'IBM Plex Sans', sans-serif;
    --font-cond:     'IBM Plex Sans Condensed', sans-serif;
    --font-mono:     'IBM Plex Mono', monospace;
}

html, body, [class*="css"] {
    background-color: var(--bg0) !important;
    color: var(--text-1) !important;
    font-family: var(--font-sans) !important;
}
.stApp { background: var(--bg0) !important; }
.main .block-container { padding: 0 2.5rem 3rem !important; max-width: 1360px !important; }
#MainMenu, footer, .stDeployButton { display: none !important; }

/* Top bar */
.cq-topbar {
    background: var(--bg1);
    border-bottom: 1px solid var(--border);
    padding: 0 2.5rem;
    display: flex; align-items: center; justify-content: space-between;
    height: 52px; margin: 0 -2.5rem 2rem;
    position: sticky; top: 0; z-index: 100;
}
.cq-brand {
    font-family: var(--font-cond); font-weight: 700; font-size: 1.1rem;
    color: var(--text-1); text-transform: uppercase; letter-spacing: 0.08em;
    display: flex; align-items: center; gap: 10px;
}
.cq-dot {
    width: 8px; height: 8px; border-radius: 50%;
    background: var(--green); box-shadow: 0 0 6px var(--green);
    animation: blink 3s ease-in-out infinite;
}
@keyframes blink { 0%,100%{opacity:1} 50%{opacity:0.3} }
.cq-topbar-meta { display:flex; align-items:center; gap:24px; }
.cq-topbar-item {
    font-family: var(--font-mono); font-size: 0.65rem; color: var(--text-3);
    letter-spacing: 0.08em; display:flex; align-items:center; gap:6px;
}
.cq-topbar-item span { color: var(--text-2); }

/* Section */
.cq-section { display:flex; align-items:center; gap:10px; margin-bottom:0.75rem; }
.cq-section-title { font-family:var(--font-mono); font-size:0.6rem; letter-spacing:0.3em; text-transform:uppercase; color:var(--text-3); white-space:nowrap; }
.cq-section-line  { flex:1; height:1px; background:var(--border); }

/* Card */
.cq-card { background:var(--bg1); border:1px solid var(--border); padding:1.2rem 1.4rem; margin-bottom:1rem; }
.cq-card-header {
    font-family:var(--font-mono); font-size:0.6rem; letter-spacing:0.25em; text-transform:uppercase;
    color:var(--text-3); padding-bottom:0.75rem; margin-bottom:1rem;
    border-bottom:1px solid var(--border);
    display:flex; justify-content:space-between; align-items:center;
}

/* Inputs */
.stTextInput input, .stNumberInput input {
    background:var(--bg2) !important; border:1px solid var(--border) !important;
    border-radius:2px !important; color:var(--text-1) !important;
    font-family:var(--font-mono) !important; font-size:0.85rem !important;
    transition:border-color 0.15s !important;
}
.stTextInput input:focus, .stNumberInput input:focus {
    border-color:var(--border-hi) !important; box-shadow:none !important;
}
.stTextInput label, .stNumberInput label {
    font-family:var(--font-mono) !important; font-size:0.6rem !important;
    letter-spacing:0.2em !important; text-transform:uppercase !important; color:var(--text-3) !important;
}

/* Textarea */
.stTextArea textarea {
    background:var(--bg2) !important; border:1px solid var(--border) !important;
    border-radius:2px !important; color:var(--text-1) !important;
    font-family:var(--font-mono) !important; font-size:0.83rem !important;
    transition:border-color 0.15s !important; line-height:1.6 !important;
}
.stTextArea textarea:focus {
    border-color:var(--border-hi) !important; box-shadow:none !important;
}
.stTextArea label {
    font-family:var(--font-mono) !important; font-size:0.6rem !important;
    letter-spacing:0.2em !important; text-transform:uppercase !important; color:var(--text-3) !important;
}

/* Button */
.stButton > button {
    background:var(--bg3) !important; border:1px solid var(--border-hi) !important;
    color:var(--text-1) !important; font-family:var(--font-mono) !important;
    font-size:0.7rem !important; letter-spacing:0.2em !important; text-transform:uppercase !important;
    border-radius:2px !important; padding:0.6rem 1.6rem !important; transition:background 0.15s !important;
}
.stButton > button:hover { background:#2e2e2e !important; border-color:#555 !important; }

/* Stat row */
.cq-stat-row { display:grid; grid-template-columns:repeat(4,1fr); gap:1px; background:var(--border); border:1px solid var(--border); margin-bottom:1.5rem; }
.cq-stat { background:var(--bg1); padding:1.1rem 1.3rem; }
.cq-stat-label { font-family:var(--font-mono); font-size:0.58rem; letter-spacing:0.22em; text-transform:uppercase; color:var(--text-3); margin-bottom:0.45rem; }
.cq-stat-value { font-family:var(--font-cond); font-weight:600; font-size:1.05rem; color:var(--text-1); white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
.cq-stat-value.large { font-size:1.55rem; font-weight:700; }
.val-red   { color:var(--red)   !important; }
.val-amber { color:var(--amber) !important; }
.val-green { color:var(--green) !important; }

/* Risk banner */
.cq-risk-row { display:flex; align-items:center; gap:12px; padding:0.8rem 1.2rem; border:1px solid; margin-bottom:1.5rem; font-family:var(--font-mono); font-size:0.7rem; letter-spacing:0.12em; }
.cq-risk-row.high   { border-color:var(--red-border);   background:var(--red-dim);   color:var(--red); }
.cq-risk-row.medium { border-color:var(--amber-border); background:var(--amber-dim); color:var(--amber); }
.cq-risk-row.low    { border-color:var(--green-border); background:var(--green-dim); color:var(--green); }
.cq-risk-badge { font-family:var(--font-cond); font-weight:700; font-size:0.7rem; letter-spacing:0.15em; padding:2px 8px; border:1px solid currentColor; }

/* Finding cards */
.cq-finding-card {
    border:1px solid var(--border);
    background:var(--bg1);
    margin-bottom:0.6rem;
    overflow:hidden;
}
.cq-finding-top {
    display:flex; align-items:flex-start; gap:12px;
    padding:0.9rem 1rem 0.75rem;
}
.cq-sev-pill {
    font-family:var(--font-mono); font-size:0.6rem; letter-spacing:0.12em;
    padding:2px 7px; border:1px solid; flex-shrink:0; margin-top:2px;
    text-transform:uppercase;
}
.sev-CRITICAL, .sev-HIGH   { border-color:var(--red-border);   color:var(--red);   background:var(--red-dim); }
.sev-MEDIUM                 { border-color:var(--amber-border); color:var(--amber); background:var(--amber-dim); }
.sev-INFO                   { border-color:var(--blue-border);  color:var(--blue);  background:var(--blue-dim); }
.sev-LOW                    { border-color:var(--green-border); color:var(--green); background:var(--green-dim); }

.cq-finding-category { font-family:var(--font-sans); font-weight:600; font-size:0.85rem; color:var(--text-1); margin-bottom:3px; }
.cq-finding-text     { font-family:var(--font-sans); font-size:0.83rem; color:var(--text-2); line-height:1.45; }

.cq-remediation {
    background:var(--bg2);
    border-top:1px solid var(--border);
    padding:0.75rem 1rem;
}
.cq-rem-label { font-family:var(--font-mono); font-size:0.56rem; letter-spacing:0.25em; text-transform:uppercase; color:var(--text-3); margin-bottom:4px; }
.cq-rem-text  { font-family:var(--font-sans); font-size:0.82rem; color:var(--text-2); line-height:1.5; }

/* KV table */
.cq-kv-table { width:100%; border-collapse:collapse; }
.cq-kv-table tr { border-bottom:1px solid var(--border); }
.cq-kv-table tr:last-child { border-bottom:none; }
.cq-kv-table td { padding:0.55rem 0; vertical-align:top; }
.cq-kv-key { font-family:var(--font-mono); font-size:0.64rem; letter-spacing:0.15em; text-transform:uppercase; color:var(--text-3); width:38%; padding-right:1rem; }
.cq-kv-val { font-family:var(--font-mono); font-size:0.8rem; color:var(--text-1); }

/* Download */
.stDownloadButton > button {
    background:transparent !important; border:1px solid var(--border) !important;
    color:var(--text-2) !important; font-family:var(--font-mono) !important;
    font-size:0.65rem !important; letter-spacing:0.18em !important; text-transform:uppercase !important;
    border-radius:2px !important;
}
.stDownloadButton > button:hover { border-color:var(--border-hi) !important; color:var(--text-1) !important; }

/* JSON */
.stJson > div { background:var(--bg2) !important; border:1px solid var(--border) !important; border-radius:2px !important; font-family:var(--font-mono) !important; font-size:0.76rem !important; }

/* Dataframe */
.stDataFrame { border:1px solid var(--border) !important; }
.stDataFrame th { background:var(--bg2) !important; color:var(--text-3) !important; font-family:var(--font-mono) !important; font-size:0.6rem !important; letter-spacing:0.18em !important; text-transform:uppercase !important; border:none !important; border-bottom:1px solid var(--border) !important; }
.stDataFrame td { font-family:var(--font-mono) !important; font-size:0.78rem !important; color:var(--text-2) !important; border-color:var(--border) !important; }

/* Progress */
.stProgress > div > div { background:var(--bg3) !important; border:1px solid var(--border) !important; border-radius:2px !important; }
.stProgress > div > div > div { background:var(--blue) !important; border-radius:1px !important; }

hr { border:none !important; border-top:1px solid var(--border) !important; margin:1.8rem 0 !important; }
::-webkit-scrollbar { width:5px; }
::-webkit-scrollbar-track { background:var(--bg0); }
::-webkit-scrollbar-thumb { background:var(--border); border-radius:2px; }
</style>
""", unsafe_allow_html=True)


# ─── Helpers ──────────────────────────────────────────────────────────────────

def normalize_target(t):
    return t.replace("https://", "").replace("http://", "").split("/")[0].strip()

def risk_meta(score):
    if score >= 7:   return "CRITICAL", "high",   "val-red"
    elif score >= 4: return "MODERATE", "medium",  "val-amber"
    else:            return "LOW",      "low",     "val-green"


# ─── Top bar ──────────────────────────────────────────────────────────────────

st.markdown("""
<div class="cq-topbar">
    <div class="cq-brand">
        <div class="cq-dot"></div>
        CypherQube
        <span style="font-weight:300;color:#555;font-size:0.75rem;margin-left:4px;">
            TLS / Quantum Risk Scanner
        </span>
    </div>
    <div class="cq-topbar-meta">
        <div class="cq-topbar-item">ENGINE <span>OpenSSL 3.x</span></div>
        <div class="cq-topbar-item">MODE <span>ACTIVE</span></div>
        <div class="cq-topbar-item">VERSION <span>2.1.0</span></div>
    </div>
</div>
""", unsafe_allow_html=True)


# ─── Single Scan Input ────────────────────────────────────────────────────────

st.markdown('<div class="cq-section"><div class="cq-section-title">Target</div><div class="cq-section-line"></div></div>', unsafe_allow_html=True)

c1, c2, c3 = st.columns([4, 1, 1])
with c1:
    raw_target = st.text_input("DOMAIN", placeholder="e.g. github.com")
with c2:
    port = st.number_input("PORT", min_value=1, max_value=65535, value=443)
with c3:
    st.markdown("<br>", unsafe_allow_html=True)
    scan_button = st.button("Run Scan", use_container_width=True)


# ─── Single Scan Results ──────────────────────────────────────────────────────

if scan_button:
    if not raw_target:
        st.error("Enter a target domain to continue.")
    else:
        # Warn if plain http — no TLS expected
        if raw_target.startswith("http://") and not raw_target.startswith("https://"):
            st.warning(f"⚠ Input uses http:// — scanning port {port} for TLS anyway. Plain HTTP sites have no TLS and the scan will fail.")

        target = normalize_target(raw_target)

        with st.spinner(f"Scanning {target}:{port}..."):
            report = analyze_target(target, port)

        if report:
            tls          = report.get("tls_version", "—")
            cipher       = report.get("cipher_suite", "—")
            key_exchange = report.get("key_exchange", "—")
            cert         = report.get("certificate", {})
            risk         = report.get("quantum_risk", {})
            score        = risk.get("risk_score", 0)
            findings     = risk.get("findings", [])

            label, css, val_cls = risk_meta(score)

            st.markdown('<div class="cq-section" style="margin-top:1.5rem;"><div class="cq-section-title">Results</div><div class="cq-section-line"></div></div>', unsafe_allow_html=True)

            # Stat row
            st.markdown(f"""
            <div class="cq-stat-row">
                <div class="cq-stat">
                    <div class="cq-stat-label">TLS Version</div>
                    <div class="cq-stat-value">{tls}</div>
                </div>
                <div class="cq-stat">
                    <div class="cq-stat-label">Cipher Suite</div>
                    <div class="cq-stat-value" style="font-size:0.82rem;">{cipher}</div>
                </div>
                <div class="cq-stat">
                    <div class="cq-stat-label">Key Exchange</div>
                    <div class="cq-stat-value">{key_exchange}</div>
                </div>
                <div class="cq-stat">
                    <div class="cq-stat-label">Quantum Risk Score</div>
                    <div class="cq-stat-value large {val_cls}">{score}<span style="font-size:0.85rem;font-weight:400;color:#555">/10</span></div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # Risk banner
            desc = {
                "high":   f"Post-quantum vulnerabilities detected on {target}:{port}. Immediate remediation recommended.",
                "medium": f"Moderate quantum risk on {target}:{port}. Plan migration to PQC algorithms.",
                "low":    f"No significant quantum vulnerabilities found on {target}:{port}.",
            }
            st.markdown(f"""
            <div class="cq-risk-row {css}">
                <span class="cq-risk-badge">{label}</span>
                <span style="font-size:0.72rem;letter-spacing:0.06em;">{desc[css]}</span>
            </div>
            """, unsafe_allow_html=True)

            # Two columns: findings + cert
            left, right = st.columns([5, 4])

            with left:
                st.markdown(f"""
                <div class="cq-card">
                    <div class="cq-card-header">
                        <span>Quantum Risk Findings</span>
                        <span style="color:var(--text-3)">{len(findings)} finding(s)</span>
                    </div>
                """, unsafe_allow_html=True)

                if findings:
                    for f in findings:
                        sev      = f.get("severity", "INFO")
                        category = f.get("category", "")
                        finding  = f.get("finding", "")
                        rem      = f.get("remediation", "")
                        sev_css  = f"sev-{sev}"

                        st.markdown(f"""
                        <div class="cq-finding-card">
                            <div class="cq-finding-top">
                                <span class="cq-sev-pill {sev_css}">{sev}</span>
                                <div>
                                    <div class="cq-finding-category">{category}</div>
                                    <div class="cq-finding-text">{finding}</div>
                                </div>
                            </div>
                            <div class="cq-remediation">
                                <div class="cq-rem-label">Remediation</div>
                                <div class="cq-rem-text">{rem}</div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.markdown("""
                    <div class="cq-finding-card">
                        <div class="cq-finding-top">
                            <span class="cq-sev-pill sev-LOW">PASS</span>
                            <div class="cq-finding-text">No quantum vulnerabilities detected. Configuration appears post-quantum safe.</div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                st.markdown('</div>', unsafe_allow_html=True)

            with right:
                pub_alg  = cert.get("public_key_algorithm", "—")
                key_size = cert.get("key_size", "—")
                sig_alg  = cert.get("signature_algorithm", "—")
                issuer   = cert.get("issuer", "—")
                expiry   = cert.get("expiry", "—")

                st.markdown(f"""
                <div class="cq-card">
                    <div class="cq-card-header"><span>Certificate Details</span></div>
                    <table class="cq-kv-table">
                        <tr><td class="cq-kv-key">Public Key Algo</td><td class="cq-kv-val">{pub_alg}</td></tr>
                        <tr><td class="cq-kv-key">Key Size</td><td class="cq-kv-val">{key_size} bits</td></tr>
                        <tr><td class="cq-kv-key">Signature Algo</td><td class="cq-kv-val" style="font-size:0.72rem;">{sig_alg}</td></tr>
                        <tr><td class="cq-kv-key">Issuer</td><td class="cq-kv-val" style="font-size:0.72rem;word-break:break-all;">{issuer}</td></tr>
                        <tr><td class="cq-kv-key">Expiry</td><td class="cq-kv-val">{expiry}</td></tr>
                    </table>
                </div>
                """, unsafe_allow_html=True)

            # Export buttons
            st.markdown('<div class="cq-section" style="margin-top:0.5rem;"><div class="cq-section-title">Export</div><div class="cq-section-line"></div></div>', unsafe_allow_html=True)

            col_json, col_pdf, _ = st.columns([1, 1, 4])

            with col_json:
                st.download_button(
                    label="↓ JSON Report",
                    data=json.dumps(report, indent=4),
                    file_name=f"cypherqube_{target.replace(':','_')}.json",
                    mime="application/json",
                    use_container_width=True
                )

            with col_pdf:
                pdf_bytes = generate_pdf_report(report)
                st.download_button(
                    label="↓ PDF Report",
                    data=pdf_bytes,
                    file_name=f"cypherqube_{target.replace(':','_')}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )

            with st.expander("Raw Crypto Inventory (JSON)"):
                st.json(report)


# ─── Bulk Scanner ─────────────────────────────────────────────────────────────

MAX_BULK = 5

st.markdown("<hr>", unsafe_allow_html=True)
st.markdown('<div class="cq-section"><div class="cq-section-title">Bulk Scan</div><div class="cq-section-line"></div></div>', unsafe_allow_html=True)

# Info banner
st.markdown(f"""
<div style="
    background:var(--bg1);
    border:1px solid var(--border);
    border-left:3px solid var(--blue);
    padding:0.75rem 1.1rem;
    margin-bottom:1rem;
    font-family:var(--font-mono);
    font-size:0.72rem;
    color:var(--text-2);
    letter-spacing:0.04em;
">
    <span style="color:var(--blue);font-weight:600;">BULK MODE</span>
    &nbsp;—&nbsp;
    Paste up to <strong style="color:var(--text-1);">{MAX_BULK} URLs</strong>, one per line.
    If more than {MAX_BULK} are provided, only the first {MAX_BULK} will be scanned.
    Accepts plain domains, <code>http://</code> or <code>https://</code> prefixes.
</div>
""", unsafe_allow_html=True)

# Paste zone
bulk_input = st.text_area(
    "TARGETS  —  one URL / domain per line",
    placeholder="github.com\nhttps://cloudflare.com\nbank.example.com\ngoogle.com\nexample.org",
    height=160,
    key="bulk_textarea"
)

# Scan button
bcol1, _ = st.columns([1, 6])
with bcol1:
    bulk_run = st.button("⬡ RUN BULK SCAN", use_container_width=True, key="bulk_run_btn")

# Processing
if bulk_run:
    raw_lines = [l.strip() for l in bulk_input.splitlines() if l.strip() and not l.strip().startswith("#")]

    if not raw_lines:
        st.error("⚠ No targets entered. Paste at least one URL or domain above.")
    else:
        total_provided = len(raw_lines)
        targets        = raw_lines[:MAX_BULK]
        trimmed        = total_provided - len(targets)

        # Trim notice
        if trimmed > 0:
            st.markdown(f"""
            <div style="
                background:var(--amber-dim);
                border:1px solid var(--amber-border);
                padding:0.65rem 1.1rem;
                margin-bottom:1rem;
                font-family:var(--font-mono);
                font-size:0.72rem;
                color:var(--amber);
                letter-spacing:0.04em;
            ">
                ⚠ &nbsp;<strong>{total_provided} URLs provided</strong> — limit is {MAX_BULK}.
                Scanning first {MAX_BULK} only.
                <span style="color:var(--text-3);">
                    Ignored: {", ".join(raw_lines[MAX_BULK:])}
                </span>
            </div>
            """, unsafe_allow_html=True)

        # Queue display
        queue_html = "".join([
            f'<div style="font-family:var(--font-mono);font-size:0.78rem;color:var(--text-2);'
            f'padding:0.3rem 0;border-bottom:1px solid var(--border);">'
            f'<span style="color:var(--text-3);margin-right:12px;">{i+1:02d}</span>{t}'
            f'</div>'
            for i, t in enumerate(targets)
        ])
        st.markdown(f"""
        <div style="background:var(--bg1);border:1px solid var(--border);
                    padding:0.8rem 1.1rem;margin-bottom:1rem;">
            <div style="font-family:var(--font-mono);font-size:0.6rem;letter-spacing:0.25em;
                        text-transform:uppercase;color:var(--text-3);margin-bottom:0.6rem;">
                Scan Queue — {len(targets)} target(s)
            </div>
            {queue_html}
        </div>
        """, unsafe_allow_html=True)

        # Scan loop
        results  = []
        errors   = []
        progress = st.progress(0)
        status   = st.empty()

        for i, raw in enumerate(targets):
            domain = normalize_target(raw)
            status.markdown(
                f'<div style="font-family:var(--font-mono);font-size:0.7rem;color:var(--text-3);">'
                f'Scanning <span style="color:var(--text-1);">{domain}</span>'
                f'&nbsp;[{i+1}/{len(targets)}]</div>',
                unsafe_allow_html=True
            )
            try:
                r = analyze_target(domain, 443)
                if r:
                    results.append(r)
            except Exception as e:
                errors.append({"target": domain, "error": str(e)})

            progress.progress((i + 1) / len(targets))

        status.empty()
        progress.empty()

        # Results header
        ok_count  = len(results)
        err_count = len(errors)

        st.markdown(
            f'<div class="cq-section" style="margin-top:1rem;">'
            f'<div class="cq-section-title">Bulk Results — {ok_count} scanned'
            f'{f", {err_count} failed" if err_count else ""}'
            f'</div><div class="cq-section-line"></div></div>',
            unsafe_allow_html=True
        )

        # Error rows
        if errors:
            for e in errors:
                st.markdown(f"""
                <div style="background:var(--red-dim);border:1px solid var(--red-border);
                            padding:0.55rem 1rem;margin-bottom:0.4rem;
                            font-family:var(--font-mono);font-size:0.75rem;color:var(--red);">
                    ✗ &nbsp;<strong>{e['target']}</strong>
                    <span style="color:var(--text-3);margin-left:12px;">{e['error']}</span>
                </div>
                """, unsafe_allow_html=True)

        # Results table + score cards
        if results:
            table = []
            for r in results:
                s = r["quantum_risk"]["risk_score"]
                lbl, _, _ = risk_meta(s)
                table.append({
                    "Target":       r["target"],
                    "TLS":          r.get("tls_version", "—"),
                    "Cipher":       r.get("cipher_suite", "—"),
                    "Key Exchange": r.get("key_exchange", "—"),
                    "Risk Score":   s,
                    "Risk Level":   lbl,
                })

            st.dataframe(pd.DataFrame(table), use_container_width=True)

            # Per-target mini score cards
            st.markdown(
                '<div class="cq-section" style="margin-top:1rem;">'
                '<div class="cq-section-title">Per-Target Risk</div>'
                '<div class="cq-section-line"></div></div>',
                unsafe_allow_html=True
            )

            cols = st.columns(min(len(results), 5))
            for idx, r in enumerate(results):
                s = r["quantum_risk"]["risk_score"]
                lbl, css, _ = risk_meta(s)
                findings_count = len(r["quantum_risk"].get("findings", []))
                color = "var(--red)" if css == "high" else "var(--amber)" if css == "medium" else "var(--green)"
                with cols[idx]:
                    st.markdown(f"""
                    <div style="background:var(--bg1);border:1px solid var(--border);
                                border-top:2px solid {color};
                                padding:0.9rem 1rem;text-align:center;">
                        <div style="font-family:var(--font-mono);font-size:0.58rem;
                                    letter-spacing:0.2em;color:var(--text-3);
                                    margin-bottom:0.4rem;text-transform:uppercase;
                                    white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">
                            {r["target"].split(":")[0]}
                        </div>
                        <div style="font-family:var(--font-cond);font-size:1.6rem;font-weight:700;color:{color};">
                            {s}<span style="font-size:0.8rem;color:var(--text-3)">/10</span>
                        </div>
                        <div style="font-family:var(--font-mono);font-size:0.6rem;
                                    color:var(--text-3);margin-top:0.3rem;">
                            {lbl} · {findings_count} finding(s)
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

            # Export
            st.markdown(
                '<div class="cq-section" style="margin-top:1rem;">'
                '<div class="cq-section-title">Export</div>'
                '<div class="cq-section-line"></div></div>',
                unsafe_allow_html=True
            )
            ecol1, _ = st.columns([1, 5])
            with ecol1:
                st.download_button(
                    "↓ Bulk JSON",
                    data=json.dumps(results, indent=4),
                    file_name="cypherqube_bulk.json",
                    mime="application/json",
                    use_container_width=True
                )


# ─── Footer ───────────────────────────────────────────────────────────────────

st.markdown("""
<div style="margin-top:2.5rem;padding-top:1rem;border-top:1px solid var(--border);
    display:flex;justify-content:space-between;">
    <span style="font-family:var(--font-mono);font-size:0.55rem;color:var(--text-3);letter-spacing:0.2em;">CYPHERCUBE © 2025</span>
    <span style="font-family:var(--font-mono);font-size:0.55rem;color:var(--text-3);letter-spacing:0.2em;">POST-QUANTUM CRYPTOGRAPHY READINESS</span>
</div>
""", unsafe_allow_html=True)