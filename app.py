import streamlit as st
import json
import pandas as pd
from pdf_report import generate_pdf_report
# from scanner import analyze_target  # Uncomment when scanner module is available

# ─── Mock scanner ─────────────────────────────────────────────────────────────
def analyze_target(target, port):
    return {
        "target": f"{target}:{port}",
        "port": port,
        "tls_version": "TLSv1.3",
        "cipher_suite": "TLS_AES_256_GCM_SHA384",
        "key_exchange": "X25519",
        "hash_function": "SHA256",
        "tls_signature": "ECDSA",
        "certificate": {
            "public_key_algorithm": "id-ecPublicKey",
            "key_size": 256,
            "signature_algorithm": "sha256WithECDSAEncryption",
            "issuer": "CN=R3, O=Let's Encrypt, C=US",
            "expiry": "2025-12-31 00:00:00"
        },
        "quantum_risk": {
            "risk_score": 7,
            "findings": [
                {
                    "category": "Key Exchange",
                    "finding": "X25519 is vulnerable to Shor's Algorithm",
                    "severity": "CRITICAL",
                    "remediation": "Migrate key exchange to a post-quantum algorithm. NIST-recommended options: CRYSTALS-Kyber (ML-KEM, FIPS 203) for key encapsulation, or hybrid X25519+Kyber schemes supported in OpenSSL 3.x / BoringSSL. Prioritise this — key exchange is exposed to 'harvest now, decrypt later' attacks."
                },
                {
                    "category": "TLS Signature",
                    "finding": "ECDSA signature is vulnerable to Shor's Algorithm",
                    "severity": "HIGH",
                    "remediation": "Replace TLS handshake signature with a post-quantum algorithm. NIST-standardised: CRYSTALS-Dilithium (ML-DSA, FIPS 204) or FALCON (FN-DSA, FIPS 206). Ensure your TLS library (OpenSSL 3.3+, liboqs) supports the chosen scheme."
                },
                {
                    "category": "Certificate Public Key",
                    "finding": "id-ecPublicKey public key is vulnerable to Shor's Algorithm",
                    "severity": "HIGH",
                    "remediation": "Reissue the certificate with a post-quantum public key algorithm. Use ML-DSA (Dilithium) or SLH-DSA (SPHINCS+, FIPS 205) for the certificate signature. Co-ordinate with your CA — most major CAs are rolling out PQC certificate support in 2024-2025."
                },
                {
                    "category": "Hash Function",
                    "finding": "SHA256 has reduced strength under Grover's Algorithm",
                    "severity": "MEDIUM",
                    "remediation": "Upgrade the hash function to SHA-384 or SHA-512. SHA-256 has its effective security halved by Grover's algorithm (128-bit post-quantum). SHA-384 / SHA-512 retain acceptable post-quantum security margins."
                },
                {
                    "category": "Cipher Suite",
                    "finding": "TLS_AES_256_GCM_SHA384 cipher is Grover-resistant (AES-256)",
                    "severity": "INFO",
                    "remediation": "AES-256 cipher is acceptable. Grover's algorithm reduces effective key length to 128 bits, which remains within acceptable security margins for the foreseeable future. No action required."
                }
            ]
        }
    }
# ──────────────────────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="CypherQube — Post-Quantum Risk Assessment",
    page_icon="🔒",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>

/* ── GLOBAL ── */
html, body, [class*="css"] {
    background-color: #f5f6f8 !important;
    color: #1a2332 !important;
    font-family: Arial, Helvetica, sans-serif !important;
}
.stApp {
    background: #f5f6f8 !important;
}
.main .block-container {
    padding: 0 2.5rem 5rem !important;
    max-width: 1380px !important;
}
#MainMenu, footer, .stDeployButton { display: none !important; }

/* ── TOP HEADER BANNER ── */
.cq-header-banner {
    background: #0a2352;
    margin: 0 -2.5rem 0;
    padding: 0 2.5rem;
    height: 56px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    position: sticky;
    top: 0;
    z-index: 300;
    border-bottom: 3px solid #1a56db;
}
.cq-header-left {
    display: flex;
    align-items: center;
    gap: 16px;
}
.cq-header-logo {
    display: flex;
    align-items: center;
    gap: 10px;
}
.cq-header-logo-mark {
    width: 30px;
    height: 30px;
    background: #1a56db;
    border: 2px solid rgba(255,255,255,0.2);
    border-radius: 5px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 14px;
    color: white;
    font-weight: bold;
    font-family: Arial, Helvetica, sans-serif;
    letter-spacing: -1px;
}
.cq-header-title {
    font-family: Arial, Helvetica, sans-serif;
    font-size: 1rem;
    font-weight: 700;
    color: #ffffff;
    letter-spacing: 0.02em;
}
.cq-header-title span {
    color: #7ab3ff;
    font-weight: 400;
}
.cq-header-divider {
    width: 1px;
    height: 22px;
    background: rgba(255,255,255,0.2);
    margin: 0 4px;
}
.cq-header-subtitle {
    font-family: Arial, Helvetica, sans-serif;
    font-size: 0.72rem;
    color: rgba(255,255,255,0.5);
    letter-spacing: 0.01em;
}
.cq-header-right {
    display: flex;
    align-items: center;
    gap: 0;
}
.cq-header-stat {
    display: flex;
    flex-direction: column;
    align-items: flex-end;
    padding: 0 18px;
    border-left: 1px solid rgba(255,255,255,0.1);
}
.cq-header-stat-label {
    font-family: Arial, Helvetica, sans-serif;
    font-size: 0.5rem;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: rgba(255,255,255,0.4);
    margin-bottom: 2px;
}
.cq-header-stat-value {
    font-family: Arial, Helvetica, sans-serif;
    font-size: 0.68rem;
    color: rgba(255,255,255,0.75);
    font-weight: 600;
}
.cq-header-stat-value.live {
    color: #4ade80;
}
.cq-live-dot {
    display: inline-block;
    width: 5px;
    height: 5px;
    border-radius: 50%;
    background: #4ade80;
    margin-right: 5px;
    animation: blink 2.5s ease-in-out infinite;
}
@keyframes blink { 0%,100%{opacity:1} 50%{opacity:0.2} }

/* ── SECONDARY NAV STRIP ── */
.cq-nav-strip {
    background: #ffffff;
    border-bottom: 1px solid #dde2ea;
    margin: 0 -2.5rem 2rem;
    padding: 0 2.5rem;
    height: 44px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    box-shadow: 0 1px 4px rgba(0,0,0,0.06);
}
.cq-nav-breadcrumb {
    display: flex;
    align-items: center;
    gap: 6px;
    font-family: Arial, Helvetica, sans-serif;
    font-size: 0.72rem;
    color: #6b7a8d;
}
.cq-nav-breadcrumb .sep { color: #c0c9d4; }
.cq-nav-breadcrumb .active { color: #0a2352; font-weight: 600; }
.cq-compliance-strip {
    display: flex;
    align-items: center;
    gap: 6px;
}
.cq-compliance-tag {
    font-family: Arial, Helvetica, sans-serif;
    font-size: 0.58rem;
    font-weight: 700;
    letter-spacing: 0.06em;
    padding: 3px 9px;
    border-radius: 3px;
    text-transform: uppercase;
    background: #eef2ff;
    color: #3b5adb;
    border: 1px solid #c5d0fa;
}

/* ── PAGE HERO ── */
.cq-page-hero {
    background: #ffffff;
    border: 1px solid #dde2ea;
    border-radius: 8px;
    padding: 2.2rem 2.5rem;
    margin-bottom: 2rem;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 2rem;
    box-shadow: 0 1px 4px rgba(0,0,0,0.05);
    position: relative;
    overflow: hidden;
}
.cq-page-hero::before {
    content: '';
    position: absolute;
    left: 0; top: 0; bottom: 0;
    width: 4px;
    background: linear-gradient(180deg, #1a56db, #0a2352);
    border-radius: 8px 0 0 8px;
}
.cq-hero-text {}
.cq-hero-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: #eef2ff;
    border: 1px solid #c5d0fa;
    border-radius: 20px;
    padding: 3px 12px;
    font-family: Arial, Helvetica, sans-serif;
    font-size: 0.62rem;
    font-weight: 700;
    color: #3b5adb;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin-bottom: 12px;
}
.cq-hero-badge-dot {
    width: 5px;
    height: 5px;
    border-radius: 50%;
    background: #3b5adb;
}
.cq-hero-title {
    font-family: Arial, Helvetica, sans-serif;
    font-size: 1.55rem;
    font-weight: 700;
    color: #0a2352;
    line-height: 1.25;
    margin-bottom: 8px;
    letter-spacing: -0.01em;
}
.cq-hero-desc {
    font-family: Arial, Helvetica, sans-serif;
    font-size: 0.88rem;
    color: #4a5568;
    line-height: 1.65;
    max-width: 580px;
    font-weight: 400;
}
.cq-hero-meta {
    display: flex;
    flex-direction: column;
    gap: 10px;
    align-items: flex-end;
    flex-shrink: 0;
}
.cq-nist-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 6px;
}
.cq-nist-pill {
    font-family: Arial, Helvetica, sans-serif;
    font-size: 0.6rem;
    font-weight: 600;
    padding: 5px 10px;
    border-radius: 4px;
    background: #f8faff;
    border: 1px solid #dde2ea;
    color: #3b5adb;
    text-align: center;
    white-space: nowrap;
}
.cq-version-tag {
    font-family: Arial, Helvetica, sans-serif;
    font-size: 0.6rem;
    color: #9aa5b4;
    text-align: right;
}

/* ── SECTION HEADING ── */
.cq-section {
    display: flex;
    align-items: center;
    gap: 12px;
    margin: 2.2rem 0 1.2rem;
}
.cq-section-num {
    width: 22px;
    height: 22px;
    border-radius: 50%;
    background: #0a2352;
    color: white;
    font-family: Arial, Helvetica, sans-serif;
    font-size: 0.62rem;
    font-weight: 700;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
}
.cq-section-label {
    font-family: Arial, Helvetica, sans-serif;
    font-size: 0.78rem;
    font-weight: 700;
    color: #0a2352;
    text-transform: uppercase;
    letter-spacing: 0.08em;
}
.cq-section-line {
    flex: 1;
    height: 1px;
    background: #dde2ea;
}
.cq-section-tag {
    font-family: Arial, Helvetica, sans-serif;
    font-size: 0.58rem;
    font-weight: 600;
    color: #6b7a8d;
    background: #ffffff;
    border: 1px solid #dde2ea;
    border-radius: 4px;
    padding: 2px 9px;
}

/* ── SCAN PANEL ── */
.cq-scan-card {
    background: #ffffff;
    border: 1px solid #dde2ea;
    border-radius: 8px;
    padding: 2rem 2rem 1.8rem;
    margin-bottom: 1.5rem;
    box-shadow: 0 1px 4px rgba(0,0,0,0.05);
    position: relative;
}
.cq-scan-card-top {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 1.4rem;
    padding-bottom: 1rem;
    border-bottom: 1px solid #f0f3f8;
}
.cq-scan-card-label {
    font-family: Arial, Helvetica, sans-serif;
    font-size: 0.75rem;
    font-weight: 700;
    color: #0a2352;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    display: flex;
    align-items: center;
    gap: 8px;
}
.cq-scan-card-label::before {
    content: '';
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: #1a56db;
    box-shadow: 0 0 0 3px rgba(26,86,219,0.15);
    animation: blink 2s ease-in-out infinite;
    flex-shrink: 0;
}
.cq-scan-hint {
    font-family: Arial, Helvetica, sans-serif;
    font-size: 0.7rem;
    color: #9aa5b4;
}

/* ── INPUTS ── */
.stTextInput input, .stNumberInput input {
    background: #fafbfc !important;
    border: 1px solid #cdd5df !important;
    border-radius: 5px !important;
    color: #1a2332 !important;
    font-family: Arial, Helvetica, sans-serif !important;
    font-size: 0.9rem !important;
    transition: all 0.15s !important;
    box-shadow: inset 0 1px 2px rgba(0,0,0,0.04) !important;
    padding: 10px 14px !important;
}
.stTextInput input:focus, .stNumberInput input:focus {
    border-color: #1a56db !important;
    box-shadow: 0 0 0 3px rgba(26,86,219,0.1), inset 0 1px 2px rgba(0,0,0,0.04) !important;
    outline: none !important;
    background: #ffffff !important;
}
.stTextInput input::placeholder { color: #b0bac8 !important; }
.stTextInput label, .stNumberInput label {
    font-family: Arial, Helvetica, sans-serif !important;
    font-size: 0.72rem !important;
    font-weight: 700 !important;
    color: #374151 !important;
    text-transform: none !important;
    letter-spacing: 0.01em !important;
}

/* ── PRIMARY BUTTON ── */
.stButton > button {
    background: #1a56db !important;
    border: 1px solid #1a56db !important;
    color: #ffffff !important;
    font-family: Arial, Helvetica, sans-serif !important;
    font-weight: 700 !important;
    font-size: 0.82rem !important;
    border-radius: 5px !important;
    padding: 0.65rem 1.8rem !important;
    transition: all 0.15s !important;
    letter-spacing: 0.02em !important;
    box-shadow: 0 1px 3px rgba(0,0,0,0.12), 0 2px 8px rgba(26,86,219,0.2) !important;
}
.stButton > button:hover {
    background: #1448c8 !important;
    border-color: #1448c8 !important;
    box-shadow: 0 2px 6px rgba(0,0,0,0.15), 0 4px 16px rgba(26,86,219,0.3) !important;
    transform: translateY(-1px) !important;
}
.stButton > button:active { transform: translateY(0) !important; }

/* ── METRICS ROW ── */
.cq-metrics-row {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 14px;
    margin-bottom: 1.5rem;
}
.cq-metric-card {
    background: #ffffff;
    border: 1px solid #dde2ea;
    border-radius: 8px;
    padding: 1.3rem 1.5rem;
    box-shadow: 0 1px 4px rgba(0,0,0,0.05);
    position: relative;
    overflow: hidden;
    transition: box-shadow 0.15s, border-color 0.15s;
}
.cq-metric-card:hover {
    box-shadow: 0 3px 12px rgba(0,0,0,0.09);
    border-color: #c0c9d8;
}
.cq-metric-card::after {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
    background: #1a56db;
    border-radius: 8px 8px 0 0;
}
.cq-metric-label {
    font-family: Arial, Helvetica, sans-serif;
    font-size: 0.62rem;
    font-weight: 700;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: #6b7a8d;
    margin-bottom: 8px;
}
.cq-metric-value {
    font-family: Arial, Helvetica, sans-serif;
    font-size: 1rem;
    font-weight: 700;
    color: #0a2352;
    line-height: 1.3;
    word-break: break-word;
}
.cq-metric-value.score {
    font-size: 2.2rem;
    font-weight: 700;
    line-height: 1;
}
.cq-metric-sub {
    font-family: Arial, Helvetica, sans-serif;
    font-size: 0.65rem;
    color: #9aa5b4;
    margin-top: 5px;
}
.score-critical { color: #c81e1e !important; }
.score-medium   { color: #b45309 !important; }
.score-safe     { color: #166534 !important; }

/* ── ALERT BANNER ── */
.cq-alert {
    display: flex;
    align-items: flex-start;
    gap: 14px;
    padding: 1.1rem 1.5rem;
    border-radius: 7px;
    border: 1px solid;
    border-left: 4px solid;
    margin-bottom: 1.5rem;
    background: #ffffff;
    box-shadow: 0 1px 4px rgba(0,0,0,0.05);
}
.cq-alert.critical { border-color: #f87171; border-left-color: #c81e1e; background: #fff5f5; }
.cq-alert.medium   { border-color: #fbbf24; border-left-color: #b45309; background: #fffbeb; }
.cq-alert.safe     { border-color: #6ee7b7; border-left-color: #166534; background: #f0fdf4; }
.cq-alert-icon { font-size: 1.2rem; flex-shrink: 0; margin-top: 1px; }
.cq-alert-content {}
.cq-alert-title {
    font-family: Arial, Helvetica, sans-serif;
    font-size: 0.82rem;
    font-weight: 700;
    margin-bottom: 3px;
}
.critical .cq-alert-title { color: #7f1d1d; }
.medium   .cq-alert-title { color: #78350f; }
.safe     .cq-alert-title { color: #14532d; }
.cq-alert-desc {
    font-family: Arial, Helvetica, sans-serif;
    font-size: 0.8rem;
    line-height: 1.5;
    font-weight: 400;
}
.critical .cq-alert-desc { color: #991b1b; }
.medium   .cq-alert-desc { color: #92400e; }
.safe     .cq-alert-desc { color: #166534; }

/* ── FINDINGS PANEL ── */
.cq-findings-panel {
    background: #ffffff;
    border: 1px solid #dde2ea;
    border-radius: 8px;
    overflow: hidden;
    box-shadow: 0 1px 4px rgba(0,0,0,0.05);
    margin-bottom: 1.2rem;
}
.cq-findings-header {
    background: #f8fafc;
    padding: 0.9rem 1.4rem;
    border-bottom: 1px solid #dde2ea;
    display: flex;
    align-items: center;
    justify-content: space-between;
}
.cq-findings-title {
    font-family: Arial, Helvetica, sans-serif;
    font-size: 0.78rem;
    font-weight: 700;
    color: #0a2352;
    text-transform: uppercase;
    letter-spacing: 0.06em;
}
.cq-findings-badge {
    font-family: Arial, Helvetica, sans-serif;
    font-size: 0.65rem;
    font-weight: 600;
    color: #4a5568;
    background: #edf2f7;
    border: 1px solid #dde2ea;
    border-radius: 12px;
    padding: 2px 10px;
}
.cq-finding-row {
    border-bottom: 1px solid #f0f3f8;
    transition: background 0.1s;
}
.cq-finding-row:last-child { border-bottom: none; }
.cq-finding-row:hover { background: #fafbfd; }
.cq-finding-top {
    display: flex;
    align-items: flex-start;
    gap: 14px;
    padding: 1.1rem 1.4rem 0.9rem;
}
.cq-sev-badge {
    font-family: Arial, Helvetica, sans-serif;
    font-size: 0.6rem;
    font-weight: 700;
    letter-spacing: 0.08em;
    padding: 4px 10px;
    border-radius: 4px;
    flex-shrink: 0;
    margin-top: 1px;
    text-transform: uppercase;
    min-width: 76px;
    text-align: center;
    border: 1px solid;
}
.sev-CRITICAL { color: #7f1d1d; background: #fef2f2; border-color: #fca5a5; }
.sev-HIGH     { color: #78350f; background: #fffbeb; border-color: #fcd34d; }
.sev-MEDIUM   { color: #713f12; background: #fefce8; border-color: #fde68a; }
.sev-INFO     { color: #1e40af; background: #eff6ff; border-color: #93c5fd; }
.sev-LOW      { color: #14532d; background: #f0fdf4; border-color: #86efac; }

.cq-finding-body { flex: 1; }
.cq-finding-cat {
    font-family: Arial, Helvetica, sans-serif;
    font-size: 0.88rem;
    font-weight: 700;
    color: #0a2352;
    margin-bottom: 4px;
}
.cq-finding-desc {
    font-family: Arial, Helvetica, sans-serif;
    font-size: 0.82rem;
    color: #4a5568;
    line-height: 1.55;
    font-weight: 400;
}
.cq-remediation {
    background: #f8faff;
    border-top: 1px solid #e8edf6;
    border-left: 3px solid #1a56db;
    padding: 0.85rem 1.4rem 0.85rem 3.6rem;
}
.cq-rem-title {
    font-family: Arial, Helvetica, sans-serif;
    font-size: 0.62rem;
    font-weight: 700;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: #1a56db;
    margin-bottom: 5px;
}
.cq-rem-body {
    font-family: Arial, Helvetica, sans-serif;
    font-size: 0.81rem;
    color: #374151;
    line-height: 1.65;
    font-weight: 400;
}

/* ── CERT PANEL ── */
.cq-cert-panel {
    background: #ffffff;
    border: 1px solid #dde2ea;
    border-radius: 8px;
    overflow: hidden;
    box-shadow: 0 1px 4px rgba(0,0,0,0.05);
}
.cq-cert-header {
    background: #f8fafc;
    padding: 0.9rem 1.4rem;
    border-bottom: 1px solid #dde2ea;
    display: flex;
    align-items: center;
    gap: 9px;
    font-family: Arial, Helvetica, sans-serif;
    font-size: 0.78rem;
    font-weight: 700;
    color: #0a2352;
    text-transform: uppercase;
    letter-spacing: 0.06em;
}
.cq-cert-icon-wrap {
    width: 24px;
    height: 24px;
    background: #eef2ff;
    border: 1px solid #c5d0fa;
    border-radius: 5px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 12px;
}
.cq-kv-table { width: 100%; border-collapse: collapse; }
.cq-kv-row {
    border-bottom: 1px solid #f0f3f8;
    transition: background 0.1s;
}
.cq-kv-row:last-child { border-bottom: none; }
.cq-kv-row:hover { background: #fafbfd; }
.cq-kv-table td { padding: 0.7rem 1.4rem; vertical-align: top; }
.cq-kv-key {
    font-family: Arial, Helvetica, sans-serif;
    font-size: 0.65rem;
    font-weight: 700;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    color: #6b7a8d;
    width: 45%;
}
.cq-kv-val {
    font-family: Arial, Helvetica, sans-serif;
    font-size: 0.82rem;
    color: #1a2332;
    word-break: break-all;
    font-weight: 400;
}

/* ── INFO SIDEBAR BOX ── */
.cq-info-box {
    background: #f8faff;
    border: 1px solid #dde6fa;
    border-radius: 8px;
    padding: 1.2rem 1.4rem;
    margin-top: 1rem;
}
.cq-info-box-title {
    font-family: Arial, Helvetica, sans-serif;
    font-size: 0.7rem;
    font-weight: 700;
    color: #1a56db;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin-bottom: 10px;
    display: flex;
    align-items: center;
    gap: 7px;
}
.cq-info-box-title::before {
    content: 'ℹ';
    font-size: 0.9rem;
}
.cq-info-row {
    display: flex;
    justify-content: space-between;
    padding: 5px 0;
    border-bottom: 1px solid #e8edf6;
    font-family: Arial, Helvetica, sans-serif;
    font-size: 0.75rem;
}
.cq-info-row:last-child { border-bottom: none; }
.cq-info-row-label { color: #6b7a8d; font-weight: 400; }
.cq-info-row-val { color: #0a2352; font-weight: 600; }

/* ── DOWNLOAD BUTTON ── */
.stDownloadButton > button {
    background: #ffffff !important;
    border: 1px solid #cdd5df !important;
    color: #374151 !important;
    font-family: Arial, Helvetica, sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.78rem !important;
    border-radius: 5px !important;
    padding: 0.55rem 1.2rem !important;
    transition: all 0.15s !important;
    box-shadow: 0 1px 2px rgba(0,0,0,0.06) !important;
}
.stDownloadButton > button:hover {
    background: #f0f7ff !important;
    border-color: #1a56db !important;
    color: #1a56db !important;
    box-shadow: 0 1px 4px rgba(26,86,219,0.15) !important;
}

/* ── FILE UPLOADER ── */
[data-testid="stFileUploader"] {
    background: #ffffff !important;
    border: 1px dashed #c0c9d8 !important;
    border-radius: 7px !important;
}
[data-testid="stFileUploader"]:hover {
    border-color: #1a56db !important;
    background: #f8faff !important;
}

/* ── JSON ── */
.stJson > div {
    background: #fafbfc !important;
    border: 1px solid #dde2ea !important;
    border-radius: 6px !important;
    font-family: 'Courier New', Courier, monospace !important;
    font-size: 0.76rem !important;
}

/* ── DATAFRAME ── */
.stDataFrame { border: 1px solid #dde2ea !important; border-radius: 8px !important; overflow: hidden !important; }
.stDataFrame thead th {
    background: #f8fafc !important;
    color: #374151 !important;
    font-family: Arial, Helvetica, sans-serif !important;
    font-size: 0.65rem !important;
    font-weight: 700 !important;
    letter-spacing: 0.08em !important;
    text-transform: uppercase !important;
    border-bottom: 1px solid #dde2ea !important;
    padding: 11px 14px !important;
}
.stDataFrame td {
    font-family: Arial, Helvetica, sans-serif !important;
    font-size: 0.82rem !important;
    color: #374151 !important;
    border-color: #f0f3f8 !important;
    background: #ffffff !important;
    padding: 9px 14px !important;
}
.stDataFrame tr:hover td { background: #f8fafd !important; }

/* ── PROGRESS ── */
.stProgress > div > div {
    background: #e5e9f0 !important;
    border-radius: 4px !important;
    height: 5px !important;
}
.stProgress > div > div > div {
    background: linear-gradient(90deg, #1a56db, #3b82f6) !important;
    border-radius: 4px !important;
}

/* ── EXPANDER ── */
.streamlit-expanderHeader {
    background: #ffffff !important;
    border: 1px solid #dde2ea !important;
    border-radius: 6px !important;
    color: #374151 !important;
    font-family: Arial, Helvetica, sans-serif !important;
    font-size: 0.8rem !important;
    font-weight: 600 !important;
}
.streamlit-expanderContent {
    border: 1px solid #dde2ea !important;
    border-top: none !important;
    background: #fafbfc !important;
}

/* ── ST ALERTS ── */
.stAlert {
    background: #fff5f5 !important;
    border: 1px solid #fca5a5 !important;
    border-radius: 6px !important;
    color: #7f1d1d !important;
    font-family: Arial, Helvetica, sans-serif !important;
}

/* ── HR ── */
hr { border: none !important; border-top: 1px solid #dde2ea !important; margin: 2.5rem 0 !important; }

/* ── SCROLLBAR ── */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: #f5f6f8; }
::-webkit-scrollbar-thumb { background: #c0c9d8; border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: #9aa5b4; }

/* ── SELECTION ── */
::selection { background: rgba(26,86,219,0.12); color: #0a2352; }

/* ── FOOTER ── */
.cq-footer {
    background: #0a2352;
    margin: 4rem -2.5rem -5rem;
    padding: 3rem 2.5rem 2rem;
    color: rgba(255,255,255,0.7);
}
.cq-footer-top {
    display: grid;
    grid-template-columns: 2fr 1fr 1fr 1fr;
    gap: 2.5rem;
    padding-bottom: 2rem;
    border-bottom: 1px solid rgba(255,255,255,0.1);
    margin-bottom: 1.8rem;
}
.cq-footer-brand-name {
    font-family: Arial, Helvetica, sans-serif;
    font-size: 1rem;
    font-weight: 700;
    color: #ffffff;
    margin-bottom: 8px;
    display: flex;
    align-items: center;
    gap: 8px;
}
.cq-footer-brand-icon {
    width: 26px;
    height: 26px;
    background: #1a56db;
    border-radius: 5px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 12px;
    font-weight: bold;
    color: white;
    font-family: Arial, sans-serif;
}
.cq-footer-brand-desc {
    font-family: Arial, Helvetica, sans-serif;
    font-size: 0.78rem;
    line-height: 1.65;
    color: rgba(255,255,255,0.5);
    max-width: 300px;
    margin-bottom: 14px;
}
.cq-footer-col-title {
    font-family: Arial, Helvetica, sans-serif;
    font-size: 0.65rem;
    font-weight: 700;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: rgba(255,255,255,0.4);
    margin-bottom: 12px;
}
.cq-footer-col-item {
    font-family: Arial, Helvetica, sans-serif;
    font-size: 0.78rem;
    color: rgba(255,255,255,0.6);
    margin-bottom: 7px;
    line-height: 1.4;
}
.cq-footer-bottom {
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 10px;
}
.cq-footer-copyright {
    font-family: Arial, Helvetica, sans-serif;
    font-size: 0.7rem;
    color: rgba(255,255,255,0.35);
}
.cq-footer-bottom-links {
    display: flex;
    gap: 20px;
}
.cq-footer-bottom-link {
    font-family: Arial, Helvetica, sans-serif;
    font-size: 0.7rem;
    color: rgba(255,255,255,0.4);
}
.cq-footer-cert-row {
    display: flex;
    gap: 8px;
    flex-wrap: wrap;
    margin-top: 10px;
}
.cq-footer-cert {
    font-family: Arial, Helvetica, sans-serif;
    font-size: 0.58rem;
    font-weight: 700;
    letter-spacing: 0.08em;
    padding: 3px 8px;
    border: 1px solid rgba(255,255,255,0.15);
    border-radius: 3px;
    color: rgba(255,255,255,0.4);
    text-transform: uppercase;
}
</style>
""", unsafe_allow_html=True)


# ─── Helpers ──────────────────────────────────────────────────────────────────

def normalize_target(t):
    return t.replace("https://","").replace("http://","").split("/")[0].strip()

def risk_meta(score):
    if score >= 7:   return "Critical Risk",  "critical", "score-critical"
    elif score >= 4: return "Moderate Risk",  "medium",   "score-medium"
    else:            return "Low Risk",        "safe",     "score-safe"


# ─── Top Header ───────────────────────────────────────────────────────────────

st.markdown("""
<div class="cq-header-banner">
    <div class="cq-header-left">
        <div class="cq-header-logo">
            <div class="cq-header-logo-mark">CQ</div>
            <div class="cq-header-title">Cypher<span>Qube</span></div>
        </div>
        <div class="cq-header-divider"></div>
        <div class="cq-header-subtitle">Post-Quantum Cryptography Risk Assessment Platform</div>
    </div>
    <div class="cq-header-right">
        <div class="cq-header-stat">
            <div class="cq-header-stat-label">Standards</div>
            <div class="cq-header-stat-value">NIST FIPS 203–206</div>
        </div>
        <div class="cq-header-stat">
            <div class="cq-header-stat-label">Engine</div>
            <div class="cq-header-stat-value">OpenSSL 3.x</div>
        </div>
        <div class="cq-header-stat">
            <div class="cq-header-stat-label">Version</div>
            <div class="cq-header-stat-value">v2.1.0</div>
        </div>
        <div class="cq-header-stat">
            <div class="cq-header-stat-label">System</div>
            <div class="cq-header-stat-value live"><span class="cq-live-dot"></span>Operational</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ─── Secondary nav strip ──────────────────────────────────────────────────────

st.markdown("""
<div class="cq-nav-strip">
    <div class="cq-nav-breadcrumb">
        <span>Security</span>
        <span class="sep">›</span>
        <span>Cryptography</span>
        <span class="sep">›</span>
        <span class="active">TLS Assessment</span>
    </div>
    <div class="cq-compliance-strip">
        <span style="font-family:Arial,sans-serif;font-size:0.62rem;color:#6b7a8d;margin-right:4px;">Compliant with:</span>
        <div class="cq-compliance-tag">ML-KEM · FIPS 203</div>
        <div class="cq-compliance-tag">ML-DSA · FIPS 204</div>
        <div class="cq-compliance-tag">SLH-DSA · FIPS 205</div>
        <div class="cq-compliance-tag">FN-DSA · FIPS 206</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ─── Page Hero ────────────────────────────────────────────────────────────────

st.markdown("""
<div class="cq-page-hero">
    <div class="cq-hero-text">
        <div class="cq-hero-badge">
            <div class="cq-hero-badge-dot"></div>
            Enterprise Security Assessment
        </div>
        <div class="cq-hero-title">TLS Post-Quantum Risk Assessment</div>
        <div class="cq-hero-desc">
            Evaluate your organisation's TLS endpoints against emerging post-quantum threats.
            CypherQube performs deep cryptographic analysis to identify vulnerabilities to
            Shor's and Grover's quantum algorithms, and delivers NIST PQC-compliant
            migration guidance to future-proof your infrastructure.
        </div>
    </div>
    <div class="cq-hero-meta">
        <div class="cq-nist-grid">
            <div class="cq-nist-pill">ML-KEM · FIPS 203</div>
            <div class="cq-nist-pill">ML-DSA · FIPS 204</div>
            <div class="cq-nist-pill">SLH-DSA · FIPS 205</div>
            <div class="cq-nist-pill">FN-DSA · FIPS 206</div>
        </div>
        <div class="cq-version-tag">CypherQube v2.1.0 · MIT License</div>
    </div>
</div>
""", unsafe_allow_html=True)


# ─── Scan Input ───────────────────────────────────────────────────────────────

st.markdown("""
<div class="cq-section">
    <div class="cq-section-num">1</div>
    <div class="cq-section-label">Target Configuration</div>
    <div class="cq-section-line"></div>
    <div class="cq-section-tag">Configure Endpoint</div>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="cq-scan-card">
    <div class="cq-scan-card-top">
        <div class="cq-scan-card-label">TLS Endpoint Scanner</div>
        <div class="cq-scan-hint">Supports domains, IP addresses, and internal hostnames on any port</div>
    </div>
""", unsafe_allow_html=True)

c1, c2, c3 = st.columns([5, 1, 1])
with c1:
    target = st.text_input(
        "Host / IP Address",
        placeholder="e.g.  api.yourbank.com   ·   192.168.1.100   ·   secure.internal"
    )
with c2:
    port = st.number_input("Port", min_value=1, max_value=65535, value=443)
with c3:
    st.markdown("<br>", unsafe_allow_html=True)
    scan_button = st.button("Run Assessment", use_container_width=True)

st.markdown('</div>', unsafe_allow_html=True)


# ─── Results ──────────────────────────────────────────────────────────────────

if scan_button:
    if not target:
        st.error("Please specify a target host to continue.")
    else:
        target = normalize_target(target)
        with st.spinner(f"Analysing {target}:{port} — please wait..."):
            report = analyze_target(target, port)

        if report:
            tls          = report.get("tls_version", "—")
            cipher       = report.get("cipher_suite", "—")
            key_exchange = report.get("key_exchange", "—")
            cert         = report.get("certificate", {})
            risk         = report.get("quantum_risk", {})
            score        = risk.get("risk_score", 0)
            findings     = risk.get("findings", [])

            label, css, score_cls = risk_meta(score)

            st.markdown("""
            <div class="cq-section">
                <div class="cq-section-num">2</div>
                <div class="cq-section-label">Assessment Results</div>
                <div class="cq-section-line"></div>
                <div class="cq-section-tag">Scan Complete</div>
            </div>
            """, unsafe_allow_html=True)

            # Metrics
            st.markdown(f"""
            <div class="cq-metrics-row">
                <div class="cq-metric-card">
                    <div class="cq-metric-label">TLS Protocol</div>
                    <div class="cq-metric-value">{tls}</div>
                    <div class="cq-metric-sub">Negotiated version</div>
                </div>
                <div class="cq-metric-card">
                    <div class="cq-metric-label">Cipher Suite</div>
                    <div class="cq-metric-value" style="font-size:0.82rem;line-height:1.45;">{cipher}</div>
                    <div class="cq-metric-sub">Active cipher</div>
                </div>
                <div class="cq-metric-card">
                    <div class="cq-metric-label">Key Exchange</div>
                    <div class="cq-metric-value">{key_exchange}</div>
                    <div class="cq-metric-sub">Algorithm in use</div>
                </div>
                <div class="cq-metric-card">
                    <div class="cq-metric-label">Quantum Risk Score</div>
                    <div class="cq-metric-value score {score_cls}">{score}<span style="font-size:1rem;font-weight:400;color:#9aa5b4">/10</span></div>
                    <div class="cq-metric-sub">{label}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # Alert banner
            alert_icons   = {"critical": "⚠️", "medium": "⚡", "safe": "✅"}
            alert_titles  = {
                "critical": f"Critical — Post-Quantum Vulnerabilities Detected",
                "medium":   f"Advisory — Moderate Quantum Exposure Identified",
                "safe":     f"Compliant — No Significant Quantum Vulnerabilities Found",
            }
            alert_descs = {
                "critical": f"The endpoint <strong>{target}:{port}</strong> uses cryptographic algorithms vulnerable to quantum attacks. Immediate migration to NIST PQC standards is strongly recommended to protect against 'harvest now, decrypt later' threats.",
                "medium":   f"The endpoint <strong>{target}:{port}</strong> has moderate quantum exposure. A structured migration plan to post-quantum cryptographic standards is recommended within your next refresh cycle.",
                "safe":     f"The endpoint <strong>{target}:{port}</strong> meets current NIST post-quantum cryptography standards. Continue monitoring as standards evolve.",
            }
            st.markdown(f"""
            <div class="cq-alert {css}">
                <span class="cq-alert-icon">{alert_icons[css]}</span>
                <div class="cq-alert-content">
                    <div class="cq-alert-title">{alert_titles[css]}</div>
                    <div class="cq-alert-desc">{alert_descs[css]}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # Two columns
            left, right = st.columns([6, 4])

            with left:
                st.markdown(f"""
                <div class="cq-findings-panel">
                    <div class="cq-findings-header">
                        <span class="cq-findings-title">Quantum Risk Findings</span>
                        <span class="cq-findings-badge">{len(findings)} finding{"s" if len(findings) != 1 else ""}</span>
                    </div>
                """, unsafe_allow_html=True)

                if findings:
                    for f in findings:
                        sev      = f.get("severity", "INFO")
                        category = f.get("category", "")
                        finding  = f.get("finding", "")
                        rem      = f.get("remediation", "")

                        st.markdown(f"""
                        <div class="cq-finding-row">
                            <div class="cq-finding-top">
                                <span class="cq-sev-badge sev-{sev}">{sev}</span>
                                <div class="cq-finding-body">
                                    <div class="cq-finding-cat">{category}</div>
                                    <div class="cq-finding-desc">{finding}</div>
                                </div>
                            </div>
                            <div class="cq-remediation">
                                <div class="cq-rem-title">Recommended Remediation</div>
                                <div class="cq-rem-body">{rem}</div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.markdown("""
                    <div class="cq-finding-row">
                        <div class="cq-finding-top">
                            <span class="cq-sev-badge sev-LOW">PASS</span>
                            <div class="cq-finding-body">
                                <div class="cq-finding-cat">All checks passed</div>
                                <div class="cq-finding-desc">No post-quantum vulnerabilities detected. Cryptographic configuration is compliant with current NIST PQC standards.</div>
                            </div>
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
                <div class="cq-cert-panel">
                    <div class="cq-cert-header">
                        <div class="cq-cert-icon-wrap">🔐</div>
                        Certificate Details
                    </div>
                    <table class="cq-kv-table">
                        <tr class="cq-kv-row">
                            <td class="cq-kv-key">Public Key Algorithm</td>
                            <td class="cq-kv-val">{pub_alg}</td>
                        </tr>
                        <tr class="cq-kv-row">
                            <td class="cq-kv-key">Key Size</td>
                            <td class="cq-kv-val">{key_size} bits</td>
                        </tr>
                        <tr class="cq-kv-row">
                            <td class="cq-kv-key">Signature Algorithm</td>
                            <td class="cq-kv-val" style="font-size:0.75rem;">{sig_alg}</td>
                        </tr>
                        <tr class="cq-kv-row">
                            <td class="cq-kv-key">Issuer</td>
                            <td class="cq-kv-val" style="font-size:0.75rem;">{issuer}</td>
                        </tr>
                        <tr class="cq-kv-row">
                            <td class="cq-kv-key">Expiry Date</td>
                            <td class="cq-kv-val">{expiry}</td>
                        </tr>
                    </table>
                </div>
                <div class="cq-info-box">
                    <div class="cq-info-box-title">Risk Score Reference</div>
                    <div class="cq-info-row">
                        <span class="cq-info-row-label">Score 7–10</span>
                        <span class="cq-info-row-val" style="color:#c81e1e;">Critical Risk</span>
                    </div>
                    <div class="cq-info-row">
                        <span class="cq-info-row-label">Score 4–6</span>
                        <span class="cq-info-row-val" style="color:#b45309;">Moderate Risk</span>
                    </div>
                    <div class="cq-info-row">
                        <span class="cq-info-row-label">Score 0–3</span>
                        <span class="cq-info-row-val" style="color:#166534;">Low Risk</span>
                    </div>
                    <div class="cq-info-row">
                        <span class="cq-info-row-label">Shor's Algorithm</span>
                        <span class="cq-info-row-val">Key / Signature attacks</span>
                    </div>
                    <div class="cq-info-row">
                        <span class="cq-info-row-label">Grover's Algorithm</span>
                        <span class="cq-info-row-val">Hash / Cipher weakening</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

            # Export
            st.markdown("""
            <div class="cq-section">
                <div class="cq-section-num">3</div>
                <div class="cq-section-label">Export Report</div>
                <div class="cq-section-line"></div>
                <div class="cq-section-tag">Download</div>
            </div>
            """, unsafe_allow_html=True)

            col_json, col_pdf, _ = st.columns([1, 1, 5])
            with col_json:
                st.download_button(
                    label="⬇ JSON Report",
                    data=json.dumps(report, indent=4),
                    file_name=f"cypherqube_{target.replace(':','_')}.json",
                    mime="application/json",
                    use_container_width=True
                )
            with col_pdf:
                pdf_bytes = generate_pdf_report(report)
                st.download_button(
                    label="⬇ PDF Report",
                    data=pdf_bytes,
                    file_name=f"cypherqube_{target.replace(':','_')}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )

            with st.expander("Raw Cryptographic Inventory (JSON)"):
                st.json(report)


# ─── Bulk Scanner ─────────────────────────────────────────────────────────────

st.markdown("<hr>", unsafe_allow_html=True)

st.markdown("""
<div class="cq-section">
    <div class="cq-section-num">4</div>
    <div class="cq-section-label">Bulk Target Assessment</div>
    <div class="cq-section-line"></div>
    <div class="cq-section-tag">Batch Mode</div>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div style="background:#ffffff;border:1px solid #dde2ea;border-radius:8px;padding:1.5rem 2rem;margin-bottom:1.2rem;box-shadow:0 1px 4px rgba(0,0,0,0.05);">
    <div style="font-family:Arial,sans-serif;font-size:0.75rem;font-weight:700;color:#0a2352;text-transform:uppercase;letter-spacing:0.08em;margin-bottom:6px;">
        Batch Endpoint Scanner
    </div>
    <div style="font-family:Arial,sans-serif;font-size:0.8rem;color:#6b7a8d;margin-bottom:1.2rem;">
        Upload a plain text file with one hostname or IP address per line. All targets will be scanned on port 443.
    </div>
""", unsafe_allow_html=True)

uploaded_file = st.file_uploader(
    "Upload targets.txt — one domain or IP per line",
    type=["txt"]
)

st.markdown('</div>', unsafe_allow_html=True)

if uploaded_file:
    domains = [d.strip() for d in uploaded_file.read().decode().splitlines() if d.strip()]
    results = []
    progress = st.progress(0)

    for i, d in enumerate(domains):
        r = analyze_target(normalize_target(d), 443)
        if r:
            results.append(r)
        progress.progress((i + 1) / len(domains))

    st.markdown(f"""
    <div class="cq-section">
        <div class="cq-section-num">✓</div>
        <div class="cq-section-label">Batch Complete — {len(results)} Targets Scanned</div>
        <div class="cq-section-line"></div>
    </div>
    """, unsafe_allow_html=True)

    table = []
    for r in results:
        s = r["quantum_risk"]["risk_score"]
        lbl, _, _ = risk_meta(s)
        table.append({
            "Target":       r["target"],
            "TLS Version":  r["tls_version"],
            "Cipher Suite": r["cipher_suite"],
            "Key Exchange": r["key_exchange"],
            "Risk Score":   s,
            "Risk Level":   lbl,
        })

    st.dataframe(pd.DataFrame(table), use_container_width=True)

    bcol1, _ = st.columns([1, 6])
    with bcol1:
        st.download_button(
            "⬇ Bulk JSON Report",
            json.dumps(results, indent=4),
            "cypherqube_bulk.json",
            "application/json",
            use_container_width=True
        )


# ─── Footer ───────────────────────────────────────────────────────────────────

st.markdown("""
<div class="cq-footer">
    <div class="cq-footer-top">
        <div>
            <div class="cq-footer-brand-name">
                <div class="cq-footer-brand-icon">CQ</div>
                CypherQube
            </div>
            <div class="cq-footer-brand-desc">
                CypherQube is an enterprise-grade post-quantum cryptography risk assessment
                platform. Designed for financial institutions, critical infrastructure, and
                regulated industries navigating the transition to NIST PQC standards.
            </div>
            <div class="cq-footer-cert-row">
                <div class="cq-footer-cert">FIPS 203</div>
                <div class="cq-footer-cert">FIPS 204</div>
                <div class="cq-footer-cert">FIPS 205</div>
                <div class="cq-footer-cert">FIPS 206</div>
                <div class="cq-footer-cert">OpenSSL 3.x</div>
                <div class="cq-footer-cert">MIT License</div>
            </div>
        </div>
        <div>
            <div class="cq-footer-col-title">Platform</div>
            <div class="cq-footer-col-item">TLS Assessment</div>
            <div class="cq-footer-col-item">Bulk Scanner</div>
            <div class="cq-footer-col-item">PDF Report Export</div>
            <div class="cq-footer-col-item">JSON Report Export</div>
            <div class="cq-footer-col-item">CLI Interface</div>
        </div>
        <div>
            <div class="cq-footer-col-title">Threat Coverage</div>
            <div class="cq-footer-col-item">Shor's Algorithm</div>
            <div class="cq-footer-col-item">Grover's Algorithm</div>
            <div class="cq-footer-col-item">Key Exchange Risk</div>
            <div class="cq-footer-col-item">Certificate Analysis</div>
            <div class="cq-footer-col-item">Cipher Suite Audit</div>
        </div>
        <div>
            <div class="cq-footer-col-title">NIST PQC Standards</div>
            <div class="cq-footer-col-item">ML-KEM (CRYSTALS-Kyber)</div>
            <div class="cq-footer-col-item">ML-DSA (CRYSTALS-Dilithium)</div>
            <div class="cq-footer-col-item">SLH-DSA (SPHINCS+)</div>
            <div class="cq-footer-col-item">FN-DSA (FALCON)</div>
            <div class="cq-footer-col-item">Hybrid PQC Schemes</div>
        </div>
    </div>
    <div class="cq-footer-bottom">
        <div class="cq-footer-copyright">
            © 2025 CypherQube. Released under the MIT License. Built for educational and research purposes.
            Not a substitute for a formal cryptographic security audit.
        </div>
        <div class="cq-footer-bottom-links">
            <span class="cq-footer-bottom-link">Documentation</span>
            <span class="cq-footer-bottom-link">GitHub</span>
            <span class="cq-footer-bottom-link">NIST PQC Project</span>
            <span class="cq-footer-bottom-link">Report an Issue</span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)
