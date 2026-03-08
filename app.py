import streamlit as st
import json
import pandas as pd
# from scanner import analyze_target  # Uncomment when scanner module is available

# ─── Mock scanner for demo purposes ───────────────────────────────────────────
def analyze_target(target, port):
    """Mock function - replace with real scanner import"""
    return {
        "target": target,
        "port": port,
        "tls_version": "TLSv1.3",
        "cipher_suite": "TLS_AES_256_GCM_SHA384",
        "key_exchange": "X25519",
        "certificate": {
            "public_key_algorithm": "RSA",
            "key_size": 2048,
            "signature_algorithm": "sha256WithRSAEncryption",
            "issuer": "CN=R3, O=Let's Encrypt, C=US",
            "expiry": "2025-12-31 00:00:00"
        },
        "quantum_risk": {
            "risk_score": 7.5,
            "findings": [
                "RSA-2048 public key is vulnerable to Shor's algorithm on a sufficiently powerful quantum computer.",
                "X25519 key exchange provides no post-quantum security.",
                "Recommend migrating to CRYSTALS-Kyber (ML-KEM) for key exchange."
            ]
        }
    }
# ──────────────────────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="CypherQube — Quantum TLS Scanner",
    page_icon="🔐",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ─── Global CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Rajdhani:wght@400;500;600;700&family=Exo+2:wght@300;400;600;800&display=swap');

/* ── Root palette ── */
:root {
    --bg-primary:   #030a0f;
    --bg-card:      #071018;
    --bg-glass:     rgba(0, 200, 255, 0.04);
    --border:       rgba(0, 200, 255, 0.15);
    --border-glow:  rgba(0, 200, 255, 0.5);
    --cyan:         #00c8ff;
    --cyan-dim:     #0077aa;
    --green:        #00ff88;
    --orange:       #ff8c00;
    --red:          #ff2b4e;
    --text-primary: #e0f4ff;
    --text-muted:   #4a7a8a;
    --font-mono:    'Share Tech Mono', monospace;
    --font-display: 'Exo 2', sans-serif;
    --font-body:    'Rajdhani', sans-serif;
}

/* ── Global reset ── */
html, body, [class*="css"] {
    background-color: var(--bg-primary) !important;
    color: var(--text-primary) !important;
    font-family: var(--font-body) !important;
}

.stApp {
    background: var(--bg-primary) !important;
    background-image:
        radial-gradient(ellipse 80% 40% at 50% -10%, rgba(0, 200, 255, 0.08) 0%, transparent 70%),
        repeating-linear-gradient(0deg, transparent, transparent 39px, rgba(0,200,255,0.03) 39px, rgba(0,200,255,0.03) 40px),
        repeating-linear-gradient(90deg, transparent, transparent 39px, rgba(0,200,255,0.03) 39px, rgba(0,200,255,0.03) 40px) !important;
    min-height: 100vh;
}

/* ── Main container ── */
.main .block-container {
    padding: 1.5rem 2.5rem 3rem !important;
    max-width: 1400px !important;
}

/* ── Hide Streamlit chrome ── */
#MainMenu, footer, .stDeployButton { display: none !important; }

/* ── HEADER ── */
.cq-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 1.8rem 0 1rem;
    border-bottom: 1px solid var(--border);
    margin-bottom: 2.5rem;
    position: relative;
}
.cq-header::after {
    content: '';
    position: absolute;
    bottom: -1px; left: 0;
    width: 180px; height: 2px;
    background: linear-gradient(90deg, var(--cyan), transparent);
}
.cq-logo {
    display: flex;
    flex-direction: column;
    gap: 2px;
}
.cq-logo-title {
    font-family: var(--font-display);
    font-weight: 800;
    font-size: 2rem;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: var(--cyan);
    text-shadow: 0 0 24px rgba(0,200,255,0.5), 0 0 48px rgba(0,200,255,0.2);
    line-height: 1;
}
.cq-logo-sub {
    font-family: var(--font-mono);
    font-size: 0.65rem;
    color: var(--text-muted);
    letter-spacing: 0.3em;
    text-transform: uppercase;
}
.cq-badge {
    font-family: var(--font-mono);
    font-size: 0.65rem;
    color: var(--cyan);
    border: 1px solid var(--border);
    padding: 4px 12px;
    letter-spacing: 0.2em;
    background: var(--bg-glass);
    display: flex;
    align-items: center;
    gap: 8px;
}
.cq-badge::before {
    content: '';
    display: inline-block;
    width: 6px; height: 6px;
    border-radius: 50%;
    background: var(--green);
    box-shadow: 0 0 8px var(--green);
    animation: pulse 2s infinite;
}
@keyframes pulse {
    0%, 100% { opacity: 1; }
    50%       { opacity: 0.4; }
}

/* ── SECTION LABEL ── */
.cq-section-label {
    font-family: var(--font-mono);
    font-size: 0.6rem;
    letter-spacing: 0.3em;
    text-transform: uppercase;
    color: var(--cyan);
    margin-bottom: 0.75rem;
    display: flex;
    align-items: center;
    gap: 10px;
}
.cq-section-label::before {
    content: '//';
    color: var(--cyan-dim);
}

/* ── INPUT PANEL ── */
.cq-input-panel {
    background: var(--bg-card);
    border: 1px solid var(--border);
    padding: 1.5rem 2rem;
    margin-bottom: 2rem;
    position: relative;
    overflow: hidden;
}
.cq-input-panel::before {
    content: '';
    position: absolute;
    top: 0; left: 0;
    width: 3px; height: 100%;
    background: linear-gradient(180deg, var(--cyan), var(--cyan-dim), transparent);
}
.cq-corner {
    position: absolute;
    top: 0; right: 0;
    width: 40px; height: 40px;
    border-top: 2px solid var(--cyan);
    border-right: 2px solid var(--cyan);
    opacity: 0.5;
}

/* ── Streamlit input overrides ── */
.stTextInput input, .stNumberInput input {
    background: rgba(0,200,255,0.04) !important;
    border: 1px solid var(--border) !important;
    border-radius: 0 !important;
    color: var(--text-primary) !important;
    font-family: var(--font-mono) !important;
    font-size: 0.9rem !important;
    letter-spacing: 0.05em !important;
    transition: border-color 0.2s, box-shadow 0.2s !important;
}
.stTextInput input:focus, .stNumberInput input:focus {
    border-color: var(--cyan) !important;
    box-shadow: 0 0 12px rgba(0,200,255,0.15) !important;
    outline: none !important;
}
.stTextInput label, .stNumberInput label {
    font-family: var(--font-mono) !important;
    font-size: 0.65rem !important;
    letter-spacing: 0.25em !important;
    text-transform: uppercase !important;
    color: var(--text-muted) !important;
}

/* ── BUTTON ── */
.stButton > button {
    background: transparent !important;
    border: 1px solid var(--cyan) !important;
    color: var(--cyan) !important;
    font-family: var(--font-mono) !important;
    font-size: 0.75rem !important;
    letter-spacing: 0.25em !important;
    text-transform: uppercase !important;
    padding: 0.65rem 2rem !important;
    border-radius: 0 !important;
    transition: all 0.2s !important;
    position: relative !important;
    overflow: hidden !important;
}
.stButton > button::before {
    content: '';
    position: absolute;
    top: 0; left: -100%;
    width: 100%; height: 100%;
    background: linear-gradient(90deg, transparent, rgba(0,200,255,0.12), transparent);
    transition: left 0.4s !important;
}
.stButton > button:hover::before { left: 100% !important; }
.stButton > button:hover {
    box-shadow: 0 0 20px rgba(0,200,255,0.3), inset 0 0 20px rgba(0,200,255,0.05) !important;
    color: #fff !important;
}

/* ── METRIC CARDS ── */
.cq-metric-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 1px;
    background: var(--border);
    border: 1px solid var(--border);
    margin-bottom: 2rem;
}
.cq-metric-card {
    background: var(--bg-card);
    padding: 1.2rem 1.5rem;
    position: relative;
    overflow: hidden;
}
.cq-metric-card::after {
    content: '';
    position: absolute;
    bottom: 0; left: 0;
    width: 100%; height: 2px;
    background: linear-gradient(90deg, var(--cyan-dim), transparent);
    opacity: 0.4;
}
.cq-metric-label {
    font-family: var(--font-mono);
    font-size: 0.58rem;
    letter-spacing: 0.3em;
    color: var(--text-muted);
    text-transform: uppercase;
    margin-bottom: 0.5rem;
}
.cq-metric-value {
    font-family: var(--font-display);
    font-weight: 600;
    font-size: 1.1rem;
    color: var(--text-primary);
    letter-spacing: 0.04em;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}
.cq-metric-value.risk-score {
    font-size: 1.6rem;
    font-weight: 800;
}
.risk-high  { color: var(--red)    !important; text-shadow: 0 0 16px rgba(255,43,78,0.5); }
.risk-med   { color: var(--orange) !important; text-shadow: 0 0 16px rgba(255,140,0,0.5); }
.risk-low   { color: var(--green)  !important; text-shadow: 0 0 16px rgba(0,255,136,0.5); }

/* ── RISK BANNER ── */
.cq-risk-banner {
    padding: 0.9rem 1.5rem;
    border: 1px solid;
    display: flex;
    align-items: center;
    gap: 16px;
    margin-bottom: 2rem;
    font-family: var(--font-mono);
    font-size: 0.75rem;
    letter-spacing: 0.15em;
    text-transform: uppercase;
}
.cq-risk-banner.high   { border-color: var(--red);    background: rgba(255,43,78,0.06);   color: var(--red); }
.cq-risk-banner.medium { border-color: var(--orange);  background: rgba(255,140,0,0.06);  color: var(--orange); }
.cq-risk-banner.low    { border-color: var(--green);   background: rgba(0,255,136,0.06);  color: var(--green); }
.cq-risk-banner-icon { font-size: 1.2rem; }

/* ── DATA PANELS ── */
.cq-panel {
    background: var(--bg-card);
    border: 1px solid var(--border);
    padding: 1.5rem;
    margin-bottom: 1.5rem;
    position: relative;
}
.cq-panel-title {
    font-family: var(--font-mono);
    font-size: 0.65rem;
    letter-spacing: 0.3em;
    text-transform: uppercase;
    color: var(--cyan);
    margin-bottom: 1.2rem;
    padding-bottom: 0.75rem;
    border-bottom: 1px solid var(--border);
}

/* ── FINDING ITEMS ── */
.cq-finding {
    display: flex;
    gap: 12px;
    padding: 0.8rem 1rem;
    border: 1px solid rgba(255,140,0,0.2);
    background: rgba(255,140,0,0.04);
    margin-bottom: 0.6rem;
    font-family: var(--font-body);
    font-size: 0.9rem;
    font-weight: 500;
    color: #d4a060;
    line-height: 1.4;
}
.cq-finding-icon { color: var(--orange); flex-shrink: 0; margin-top: 1px; }
.cq-finding.safe {
    border-color: rgba(0,255,136,0.2);
    background: rgba(0,255,136,0.04);
    color: #5ad4a0;
}
.cq-finding.safe .cq-finding-icon { color: var(--green); }

/* ── CERT GRID ── */
.cq-cert-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 1px;
    background: var(--border);
    margin-bottom: 1rem;
}
.cq-cert-item {
    background: var(--bg-card);
    padding: 1rem 1.2rem;
}
.cq-cert-label {
    font-family: var(--font-mono);
    font-size: 0.55rem;
    letter-spacing: 0.3em;
    color: var(--text-muted);
    text-transform: uppercase;
    margin-bottom: 0.4rem;
}
.cq-cert-value {
    font-family: var(--font-mono);
    font-size: 0.85rem;
    color: var(--text-primary);
}

/* ── JSON BLOCK ── */
.stJson, .stJson > div {
    background: rgba(0,200,255,0.03) !important;
    border: 1px solid var(--border) !important;
    border-radius: 0 !important;
    font-family: var(--font-mono) !important;
    font-size: 0.78rem !important;
}

/* ── DATAFRAME ── */
.stDataFrame, .stDataFrame > div {
    border: 1px solid var(--border) !important;
}
.stDataFrame th {
    background: rgba(0,200,255,0.08) !important;
    color: var(--cyan) !important;
    font-family: var(--font-mono) !important;
    font-size: 0.65rem !important;
    letter-spacing: 0.2em !important;
    text-transform: uppercase !important;
    border: none !important;
}
.stDataFrame td {
    font-family: var(--font-mono) !important;
    font-size: 0.8rem !important;
    border-color: var(--border) !important;
}

/* ── PROGRESS BAR ── */
.stProgress > div > div {
    background: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    border-radius: 0 !important;
}
.stProgress > div > div > div {
    background: linear-gradient(90deg, var(--cyan-dim), var(--cyan)) !important;
    border-radius: 0 !important;
    box-shadow: 0 0 12px rgba(0,200,255,0.4) !important;
}

/* ── DOWNLOAD BUTTON ── */
.stDownloadButton > button {
    background: rgba(0,200,255,0.06) !important;
    border: 1px solid var(--cyan-dim) !important;
    color: var(--cyan) !important;
    font-family: var(--font-mono) !important;
    font-size: 0.7rem !important;
    letter-spacing: 0.2em !important;
    text-transform: uppercase !important;
    border-radius: 0 !important;
}
.stDownloadButton > button:hover {
    border-color: var(--cyan) !important;
    box-shadow: 0 0 14px rgba(0,200,255,0.25) !important;
}

/* ── FILE UPLOADER ── */
.stFileUploader {
    border: 1px dashed var(--border) !important;
    background: rgba(0,200,255,0.02) !important;
    padding: 1rem !important;
}
.stFileUploader label {
    font-family: var(--font-mono) !important;
    font-size: 0.65rem !important;
    letter-spacing: 0.25em !important;
    color: var(--text-muted) !important;
    text-transform: uppercase !important;
}

/* ── DIVIDER ── */
hr {
    border: none !important;
    border-top: 1px solid var(--border) !important;
    margin: 2rem 0 !important;
}

/* ── SPINNER ── */
.stSpinner > div {
    border-color: var(--cyan) transparent transparent transparent !important;
}

/* ── ALERTS ── */
.stAlert {
    border-radius: 0 !important;
    font-family: var(--font-body) !important;
    font-weight: 600 !important;
    border-left-width: 3px !important;
}

/* ── SCROLLBAR ── */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: var(--bg-primary); }
::-webkit-scrollbar-thumb { background: var(--border); }
::-webkit-scrollbar-thumb:hover { background: var(--cyan-dim); }

</style>
""", unsafe_allow_html=True)


# ─── Helper Functions ──────────────────────────────────────────────────────────

def normalize_target(target):
    target = target.replace("https://", "").replace("http://", "")
    return target.split("/")[0]

def risk_label(score):
    if score >= 7:
        return "CRITICAL QUANTUM RISK", "high"
    elif score >= 4:
        return "MODERATE QUANTUM RISK", "medium"
    else:
        return "LOW QUANTUM RISK", "low"

def risk_color_class(score):
    if score >= 7:   return "risk-high"
    elif score >= 4: return "risk-med"
    else:            return "risk-low"


# ─── Header ───────────────────────────────────────────────────────────────────

st.markdown("""
<div class="cq-header">
    <div class="cq-logo">
        <div class="cq-logo-title">⬡ CypherQube</div>
        <div class="cq-logo-sub">TLS Cryptography & Quantum Risk Intelligence Platform</div>
    </div>
    <div style="display:flex; gap:12px; align-items:center;">
        <div class="cq-badge">SYSTEM ONLINE</div>
        <div class="cq-badge" style="border-color:rgba(0,200,255,0.08); color:var(--text-muted);">v2.0.0</div>
    </div>
</div>
""", unsafe_allow_html=True)


# ─── Input Panel ──────────────────────────────────────────────────────────────

st.markdown('<div class="cq-section-label">Target Configuration</div>', unsafe_allow_html=True)

st.markdown('<div class="cq-input-panel"><div class="cq-corner"></div>', unsafe_allow_html=True)

col1, col2, col3 = st.columns([3, 1, 1])

with col1:
    target = st.text_input("Target Domain", placeholder="e.g. google.com", label_visibility="visible")

with col2:
    port = st.number_input("Port", min_value=1, max_value=65535, value=443)

with col3:
    st.markdown("<br>", unsafe_allow_html=True)
    scan_button = st.button("⬡ INITIATE SCAN", use_container_width=True)

st.markdown('</div>', unsafe_allow_html=True)


# ─── Single Target Scan ───────────────────────────────────────────────────────

if scan_button:
    if not target:
        st.error("⚠ No target specified. Enter a domain to begin analysis.")
    else:
        target = normalize_target(target)

        with st.spinner(f"Performing quantum risk analysis on {target}:{port}..."):
            report = analyze_target(target, port)

        if report:
            st.markdown('<div class="cq-section-label">Scan Results</div>', unsafe_allow_html=True)

            tls         = report.get("tls_version", "Unknown")
            cipher      = report.get("cipher_suite", "Unknown")
            key_exchange = report.get("key_exchange", "Unknown")
            cert        = report.get("certificate", {})
            risk        = report.get("quantum_risk", {})
            score       = risk.get("risk_score", 0)
            findings    = risk.get("findings", [])

            level, css_class = risk_label(score)
            rcc = risk_color_class(score)

            # ── Metric Cards ──
            st.markdown(f"""
            <div class="cq-metric-grid">
                <div class="cq-metric-card">
                    <div class="cq-metric-label">TLS Version</div>
                    <div class="cq-metric-value">{tls}</div>
                </div>
                <div class="cq-metric-card">
                    <div class="cq-metric-label">Cipher Suite</div>
                    <div class="cq-metric-value" style="font-size:0.8rem;">{cipher}</div>
                </div>
                <div class="cq-metric-card">
                    <div class="cq-metric-label">Key Exchange</div>
                    <div class="cq-metric-value">{key_exchange}</div>
                </div>
                <div class="cq-metric-card">
                    <div class="cq-metric-label">Quantum Risk Score</div>
                    <div class="cq-metric-value risk-score {rcc}">{score}<span style="font-size:0.9rem;opacity:0.5">/10</span></div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # ── Risk Banner ──
            icons = {"high": "⚠", "medium": "◈", "low": "✓"}
            st.markdown(f"""
            <div class="cq-risk-banner {css_class}">
                <span class="cq-risk-banner-icon">{icons[css_class]}</span>
                <span>{level} — {target}:{port}</span>
            </div>
            """, unsafe_allow_html=True)

            # ── Two column layout ──
            left, right = st.columns([1, 1])

            with left:
                # Findings
                st.markdown("""
                <div class="cq-panel">
                    <div class="cq-panel-title">Quantum Risk Findings</div>
                """, unsafe_allow_html=True)

                if findings:
                    for f in findings:
                        st.markdown(f"""
                        <div class="cq-finding">
                            <span class="cq-finding-icon">▸</span>
                            <span>{f}</span>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.markdown("""
                    <div class="cq-finding safe">
                        <span class="cq-finding-icon">✓</span>
                        <span>No significant quantum vulnerabilities detected.</span>
                    </div>
                    """, unsafe_allow_html=True)

                st.markdown('</div>', unsafe_allow_html=True)

            with right:
                # Certificate Details
                pub_alg  = cert.get("public_key_algorithm", "Unknown")
                key_size = cert.get("key_size", "Unknown")
                sig_alg  = cert.get("signature_algorithm", "Unknown")
                issuer   = cert.get("issuer", "Unknown")
                expiry   = cert.get("expiry", "Unknown")

                st.markdown(f"""
                <div class="cq-panel">
                    <div class="cq-panel-title">Certificate Intelligence</div>
                    <div class="cq-cert-grid">
                        <div class="cq-cert-item">
                            <div class="cq-cert-label">Public Key Algo</div>
                            <div class="cq-cert-value">{pub_alg}</div>
                        </div>
                        <div class="cq-cert-item">
                            <div class="cq-cert-label">Key Size</div>
                            <div class="cq-cert-value">{key_size} bits</div>
                        </div>
                        <div class="cq-cert-item">
                            <div class="cq-cert-label">Sig Algorithm</div>
                            <div class="cq-cert-value" style="font-size:0.7rem;">{sig_alg}</div>
                        </div>
                    </div>
                    <div style="margin-top:1px;">
                        <div class="cq-cert-item" style="background:var(--bg-card); padding:0.9rem 1.2rem; border:1px solid var(--border); margin-bottom:1px;">
                            <div class="cq-cert-label">Issuer</div>
                            <div class="cq-cert-value" style="font-size:0.75rem; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">{issuer}</div>
                        </div>
                        <div class="cq-cert-item" style="background:var(--bg-card); padding:0.9rem 1.2rem; border:1px solid var(--border);">
                            <div class="cq-cert-label">Expiry</div>
                            <div class="cq-cert-value">{expiry}</div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

            # ── Full Crypto Inventory ──
            st.markdown('<div class="cq-section-label" style="margin-top:1rem;">Crypto Inventory — Raw Report</div>', unsafe_allow_html=True)
            st.json(report)

            # ── Download ──
            json_report = json.dumps(report, indent=4)
            st.download_button(
                label="⬇ EXPORT JSON REPORT",
                data=json_report,
                file_name=f"cypherqube_{target}.json",
                mime="application/json"
            )


# ─── Bulk Scanner ─────────────────────────────────────────────────────────────

st.markdown('<hr>', unsafe_allow_html=True)
st.markdown('<div class="cq-section-label">Bulk Domain Analysis</div>', unsafe_allow_html=True)

st.markdown('<div class="cq-input-panel"><div class="cq-corner"></div>', unsafe_allow_html=True)

uploaded_file = st.file_uploader(
    "Upload targets.txt — one domain per line",
    type=["txt"],
    label_visibility="visible"
)

st.markdown('</div>', unsafe_allow_html=True)

if uploaded_file:
    domains = uploaded_file.read().decode().splitlines()
    domains = [d.strip() for d in domains if d.strip()]

    results = []
    progress = st.progress(0)

    for i, d in enumerate(domains):
        d = normalize_target(d)
        r = analyze_target(d, 443)
        if r:
            results.append(r)
        progress.progress((i + 1) / len(domains))

    st.markdown(f'<div class="cq-section-label">Bulk Scan Complete — {len(results)} Targets Analyzed</div>', unsafe_allow_html=True)

    table = []
    for r in results:
        score = r["quantum_risk"]["risk_score"]
        level, _ = risk_label(score)
        table.append({
            "Target":       r["target"],
            "TLS Version":  r["tls_version"],
            "Cipher Suite": r["cipher_suite"],
            "Key Exchange": r["key_exchange"],
            "Risk Score":   score,
            "Risk Level":   level
        })

    df = pd.DataFrame(table)
    st.dataframe(df, use_container_width=True)

    bulk_json = json.dumps(results, indent=4)
    st.download_button(
        "⬇ EXPORT BULK JSON REPORT",
        bulk_json,
        "cypherqube_bulk_report.json",
        "application/json"
    )

# ─── Footer ───────────────────────────────────────────────────────────────────
st.markdown("""
<div style="margin-top:3rem; padding-top:1rem; border-top:1px solid var(--border);
            display:flex; justify-content:space-between; align-items:center;">
    <span style="font-family:var(--font-mono); font-size:0.55rem; color:var(--text-muted); letter-spacing:0.25em;">
        CYPHERCUBE QUANTUM TLS SCANNER © 2025
    </span>
    <span style="font-family:var(--font-mono); font-size:0.55rem; color:var(--text-muted); letter-spacing:0.2em;">
        POST-QUANTUM CRYPTOGRAPHY READINESS PLATFORM
    </span>
</div>
""", unsafe_allow_html=True)