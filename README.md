<div align="center">

# ⬡ CypherQube
### TLS / Quantum Risk Scanner

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-1.x-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![OpenSSL](https://img.shields.io/badge/OpenSSL-3.x-721412?style=for-the-badge&logo=openssl&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)
![Hackathon](https://img.shields.io/badge/PNB%20CyberSecurity-Hackathon%202026-gold?style=for-the-badge)

**A proof-of-concept security tool that scans TLS services, builds a 
cryptographic inventory, and assesses post-quantum risk based on 
NIST PQC standards (FIPS 203/204/205/206).**

> *"95% of servers still use quantum-vulnerable encryption.  
> CypherQube finds them — before attackers exploit them."*

[🚀 Quick Start](#installation) • [📊 Dashboard](#usage) • [🔬 Risk Scoring](#risk-scoring) • [👥 Team](#team)

</div>

---

## 🧠 Why CypherQube?

Quantum computers running **Shor's Algorithm** will break RSA, ECDSA,
and Diffie-Hellman — the algorithms powering ~99% of HTTPS today.
Adversaries are already collecting encrypted traffic now to decrypt
later (**Harvest Now, Decrypt Later** attacks).

CypherQube gives security teams a **one-command audit** of any
public-facing TLS server — identifying quantum-vulnerable algorithms
and providing specific NIST PQC migration guidance before Q-Day arrives.

---

## ✨ Features

| Feature | Description |
|---|---|
| 🔍 **TLS Scanning** | Connects via OpenSSL, extracts TLS version, cipher suite, key exchange, hash & signature algorithms |
| 📜 **Certificate Analysis** | Parses X.509 — public key algorithm, key size, issuer, expiry dates |
| ⚛️ **Quantum Risk Scoring** | Scores 0–10 based on vulnerability to Shor's and Grover's algorithms |
| ✅ **PQC Recognition** | Detects NIST-standard ML-KEM, ML-DSA, SLH-DSA, FN-DSA — marks as PASS |
| 🛠️ **Remediation Guidance** | Per-finding migration advice to post-quantum alternatives |
| 📊 **Streamlit Dashboard** | Dark SIEM-style web UI with real-time scan results |
| 📄 **PDF Export** | Professional dark-themed report with full findings |
| 🖥️ **CLI Mode** | Scan from terminal, export JSON or PDF |
| 🔁 **Bulk Scanning** | Scan multiple domains at once via batch mode |

---

## 📁 Project Structure
```
cypherQube/
├── app.py            # Streamlit web dashboard
├── cli.py            # CLI entry point
├── scanner.py        # OpenSSL TLS scanner & certificate parser
├── risk_engine.py    # Quantum risk scoring engine
├── pdf_report.py     # PDF report generator (ReportLab)
└── requirements.txt  # Python dependencies
```

---

## ⚙️ Installation
```bash
git clone https://github.com/Sumit0x00/cypherqube.git
cd cypherqube

python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

pip install -r requirements.txt
```

> **Requirement:** OpenSSL must be installed on your system.
```bash
# Ubuntu / Debian
sudo apt install openssl

# macOS
brew install openssl
```

---

## 🚀 Usage

### Web Dashboard
```bash
streamlit run app.py
```
Then open **http://localhost:8501** in your browser.

### CLI — Single Target
```bash
python main.py github.com
python main.py github.com --port 443 --json report.json
python main.py github.com --pdf report.pdf
```

### CLI — JSON + PDF Together
```bash
python main.py example.com --json out.json --pdf out.pdf
```

---

## 📊 Risk Scoring

| Score | Level | Meaning |
|---|---|---|
| 7–10 | 🔴 **CRITICAL** | Multiple components vulnerable to Shor's algorithm |
| 4–6  | 🟠 **MODERATE** | Partial vulnerability, migration recommended |
| 0–3  | 🟢 **LOW** | Minimal quantum risk |

### Severity Levels

| Severity | Description | Score Impact |
|---|---|---|
| 🔴 CRITICAL | Key exchange broken by Shor's algorithm | +3 |
| 🟠 HIGH | Signature / cert public key broken by Shor's | +3 each |
| 🟡 MEDIUM | Hash / cipher weakened by Grover's algorithm | +1 |
| 🟢 PASS | NIST PQC algorithm detected — post-quantum safe | 0 |
| 🔵 INFO | Informational, no score impact | 0 |
| ⚪ UNKNOWN | Unrecognised algorithm, manual review needed | +1 |

---

## 🔐 NIST PQC Algorithms Recognised

| Standard | Algorithm | Type |
|---|---|---|
| FIPS 203 | ML-KEM (CRYSTALS-Kyber) | Key Encapsulation |
| FIPS 204 | ML-DSA (CRYSTALS-Dilithium) | Digital Signature |
| FIPS 205 | SLH-DSA (SPHINCS+) | Digital Signature |
| FIPS 206 | FN-DSA (FALCON) | Digital Signature |

> Hybrid schemes (`X25519MLKEM768`, `X25519Kyber768`) are also recognised.

---

## 📦 Requirements
```
streamlit
reportlab
pandas
```

---

## 👥 Team

<div align="center">
```
╔══════════════════════════════════════════════════════════════╗
║                    ⬡  TEAM THREAT LAB                       ║
║              PNB CyberSecurity Hackathon 2026                ║
╠══════════════╦══════════════════╦═══════════════════════════╣
║  👑 LEADER   ║  💻 DEVELOPER    ║  🧪 TESTER               ║
║              ║                  ║                           ║
║    Sumit     ║ Sidharth Kumar   ║    Rahul Rajak            ║
║              ║                  ║   Roshan Pandit           ║
╚══════════════╩══════════════════╩═══════════════════════════╝
```

📍 Indian Institute of Technology, Kanpur  
🔗 [github.com/Sumit0x00/cypherqube](https://github.com/Sumit0x00/cypherqube)

</div>

---

## 📄 License
```
MIT License — Built for educational and security research purposes.
Free to use, modify, and distribute with attribution.
```

---

<div align="center">

**⬡ CypherQube** — *Scan today. Migrate before Q-Day.*

Made with ❤️ by Team Threat Lab | IIT Kanpur

</div>