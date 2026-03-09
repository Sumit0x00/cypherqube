# =============================================================================
# risk_engine.py — CypherQube Quantum Risk Engine
# =============================================================================
# Scoring logic:
#   Key Exchange vulnerable      → +3
#   TLS Signature vulnerable     → +3
#   Certificate Public Key vuln  → +3
#   Hash Function weak           → +1
#   Any of the above PQC-safe    →  0 (PASS finding, no score added)
#   Unrecognised algorithm       → +1 (UNKNOWN, flagged for review)
#   Max score capped at 10
# =============================================================================


# ─── Algorithms broken by Shor's Algorithm (quantum computer) ─────────────────
# These are factoring / discrete-log based — all broken by a CRQC

QUANTUM_VULNERABLE = [
    # RSA family
    "RSA",
    # Elliptic curve family
    "ECDSA", "ECDH", "ECDHE",
    "id-ecPublicKey",
    # Specific named curves (as OpenSSL may report them)
    "X25519", "X448",
    "P-256", "P-384", "P-521",
    "prime256v1", "secp384r1", "secp521r1",
    # DH / DSA (classical)
    "DH", "DHE", "DSA",
]

# ─── Hash functions weakened by Grover's Algorithm ────────────────────────────
# Grover halves effective bit security: SHA-256 → 128-bit PQ security (borderline)
# SHA-1 / SHA-224 are already weak classically too

PARTIAL_RISK = [
    "SHA1", "SHA-1",
    "SHA224", "SHA-224",
    "SHA256", "SHA-256",   # borderline — still used but weakened
    "MD5",                 # classically broken, definitely flag
]

# ─── Hash functions safe post-quantum ─────────────────────────────────────────
# SHA-384 / SHA-512 retain 192 / 256 bit PQ security under Grover

HASH_SAFE = [
    "SHA384", "SHA-384",
    "SHA512", "SHA-512",
    "SHA3-256", "SHA3-384", "SHA3-512",
    "SHAKE128", "SHAKE256",
]

# ─── Symmetric ciphers safe post-quantum ──────────────────────────────────────
# AES-256 → 128-bit PQ security (acceptable). AES-128 is borderline.

CIPHER_SAFE = [
    "AES_256", "AES256", "AES-256",
    "TLS_AES_256",
    "CHACHA20",            # 256-bit key, 128-bit PQ security
]

CIPHER_WEAK = [
    "AES_128", "AES128", "AES-128",
    "TLS_AES_128",
    "3DES", "DES", "RC4",
]

# ─── NIST PQC Standard Algorithms (FIPS 203 / 204 / 205 / 206) ───────────────
# If a site is already using these, it's PQC-ready — score 0, PASS finding.

# Key Encapsulation (replaces key exchange)
PQC_KEM = [
    # ML-KEM (CRYSTALS-Kyber) — FIPS 203
    "ML-KEM", "MLKEM",
    "Kyber", "kyber",
    "kyber512", "kyber768", "kyber1024",
    "ML-KEM-512", "ML-KEM-768", "ML-KEM-1024",
    # Hybrid schemes (classical + PQC)
    "X25519Kyber768",
    "X25519MLKEM768",
    "p256_kyber512",
    "SecP256r1Kyber768",
]

# Digital Signatures
PQC_SIG = [
    # ML-DSA (CRYSTALS-Dilithium) — FIPS 204
    "ML-DSA", "MLDSA",
    "Dilithium", "dilithium",
    "dilithium2", "dilithium3", "dilithium5",
    "ML-DSA-44", "ML-DSA-65", "ML-DSA-87",

    # SLH-DSA (SPHINCS+) — FIPS 205
    "SLH-DSA", "SLHDSA",
    "SPHINCS", "sphincs",
    "SPHINCS+",
    "SLH-DSA-SHA2-128s", "SLH-DSA-SHA2-128f",
    "SLH-DSA-SHA2-192s", "SLH-DSA-SHA2-256s",

    # FN-DSA (FALCON) — FIPS 206
    "FN-DSA", "FNDSA",
    "FALCON", "falcon",
    "falcon512", "falcon1024",
    "FN-DSA-512", "FN-DSA-1024",
]

# All PQC algorithms combined for generic checks
PQC_ALL = PQC_KEM + PQC_SIG


# ─── Remediation Map ──────────────────────────────────────────────────────────

REMEDIATION = {
    "key_exchange_vuln": (
        "Migrate key exchange to a post-quantum algorithm. "
        "NIST standard: CRYSTALS-Kyber (ML-KEM, FIPS 203). "
        "For a smooth transition, deploy a hybrid scheme (X25519+ML-KEM-768) "
        "supported in OpenSSL 3.x with liboqs, or BoringSSL. "
        "This is the highest priority fix — key exchange traffic is vulnerable "
        "to 'harvest now, decrypt later' attacks today."
    ),
    "tls_sig_vuln": (
        "Replace the TLS handshake signature algorithm with a NIST PQC standard. "
        "Options: ML-DSA (CRYSTALS-Dilithium, FIPS 204) for general use, "
        "or FN-DSA (FALCON, FIPS 206) for bandwidth-constrained environments. "
        "Requires OpenSSL 3.3+ with liboqs or a TLS library with PQC support."
    ),
    "cert_pubkey_vuln": (
        "Reissue the certificate with a post-quantum signature algorithm. "
        "Recommended: ML-DSA-65 (Dilithium) or SLH-DSA (SPHINCS+, FIPS 205) — "
        "SPHINCS+ is stateless and simpler to deploy. "
        "Co-ordinate with your CA; Let's Encrypt and major CAs are rolling out "
        "PQC certificate issuance. Until then, use a self-signed PQC cert in testing."
    ),
    "hash_weak": (
        "Upgrade hash function to SHA-384 or SHA-512. "
        "SHA-256 retains only ~128-bit security under Grover's algorithm — borderline. "
        "SHA-384 gives 192-bit and SHA-512 gives 256-bit post-quantum security. "
        "SHA3-256/384/512 are also acceptable alternatives."
    ),
    "cipher_weak": (
        "Upgrade cipher to AES-256-GCM or ChaCha20-Poly1305. "
        "AES-128 drops to 64-bit effective security under Grover's algorithm — "
        "below recommended thresholds. AES-256 retains 128-bit PQ security."
    ),
    "cipher_safe": (
        "Cipher suite is post-quantum acceptable. AES-256 retains 128-bit "
        "effective security under Grover's algorithm. No action required."
    ),
    "pqc_kem_pass": (
        "Key exchange is using a NIST PQC key encapsulation mechanism. "
        "This is post-quantum safe. Ensure you are using the latest parameter "
        "set (ML-KEM-768 or ML-KEM-1024) and keep the library updated."
    ),
    "pqc_sig_pass": (
        "Signature algorithm is a NIST PQC standard. "
        "Ensure parameter sets are at security level 2 or above "
        "(e.g. ML-DSA-65, ML-DSA-87, FN-DSA-1024). Keep the library updated."
    ),
    "unknown": (
        "Algorithm was not recognised in the vulnerability or PQC-safe lists. "
        "Manually verify whether this algorithm is post-quantum safe. "
        "Check NIST PQC standards (FIPS 203-206) and IETF PQC working group drafts."
    ),
}


# ─── Core Analysis ────────────────────────────────────────────────────────────

def _check_component(value, category, vuln_list, pqc_list, remediation_vuln, remediation_pass, severity_vuln):
    """
    Check a single crypto component.
    Returns (finding_dict_or_None, score_delta)
    """
    if not value or value in ("Unknown", "—", ""):
        return None, 0

    # PQC safe — recognised NIST PQC algorithm
    if any(p.lower() in value.lower() for p in pqc_list):
        return {
            "category":    category,
            "finding":     f"{value} — NIST PQC algorithm detected (post-quantum safe)",
            "severity":    "PASS",
            "remediation": remediation_pass,
        }, 0

    # Classically vulnerable
    if any(v.lower() in value.lower() for v in vuln_list):
        return {
            "category":    category,
            "finding":     f"{value} is vulnerable to Shor's Algorithm on a cryptographically relevant quantum computer",
            "severity":    severity_vuln,
            "remediation": remediation_vuln,
        }, 3 if severity_vuln in ("CRITICAL", "HIGH") else 1

    # Unrecognised
    return {
        "category":    category,
        "finding":     f"{value} — algorithm not recognised, manual review recommended",
        "severity":    "UNKNOWN",
        "remediation": REMEDIATION["unknown"],
    }, 1


def analyze_quantum_risk(inventory):
    """
    Analyse a crypto inventory dict and return (findings, score).
    Each finding: { category, finding, severity, remediation }
    Severity values: CRITICAL | HIGH | MEDIUM | PASS | INFO | UNKNOWN
    """
    findings = []
    score    = 0

    key_exchange = inventory.get("key_exchange", "")
    tls_sig      = inventory.get("tls_signature", "")
    cipher       = inventory.get("cipher_suite",  "")
    hash_algo    = inventory.get("hash_function",  "")
    cert_algo    = inventory.get("certificate", {}).get("public_key_algorithm", "")

    # ── 1. Key Exchange ───────────────────────────────────────────────────────
    f, s = _check_component(
        key_exchange, "Key Exchange",
        QUANTUM_VULNERABLE, PQC_KEM,
        REMEDIATION["key_exchange_vuln"],
        REMEDIATION["pqc_kem_pass"],
        "CRITICAL"
    )
    if f: findings.append(f); score += s

    # ── 2. TLS Signature ──────────────────────────────────────────────────────
    f, s = _check_component(
        tls_sig, "TLS Signature",
        QUANTUM_VULNERABLE, PQC_SIG,
        REMEDIATION["tls_sig_vuln"],
        REMEDIATION["pqc_sig_pass"],
        "HIGH"
    )
    if f: findings.append(f); score += s

    # ── 3. Certificate Public Key ─────────────────────────────────────────────
    f, s = _check_component(
        cert_algo, "Certificate Public Key",
        QUANTUM_VULNERABLE, PQC_SIG,
        REMEDIATION["cert_pubkey_vuln"],
        REMEDIATION["pqc_sig_pass"],
        "HIGH"
    )
    if f: findings.append(f); score += s

    # ── 4. Hash Function ──────────────────────────────────────────────────────
    if hash_algo and hash_algo not in ("Unknown", "—"):
        if any(h.lower() in hash_algo.lower() for h in HASH_SAFE):
            findings.append({
                "category":    "Hash Function",
                "finding":     f"{hash_algo} — post-quantum safe hash (SHA-384/512 range)",
                "severity":    "PASS",
                "remediation": "No action required. SHA-384+ retains strong post-quantum security margins.",
            })
        elif any(h.lower() in hash_algo.lower() for h in PARTIAL_RISK):
            findings.append({
                "category":    "Hash Function",
                "finding":     f"{hash_algo} has reduced strength under Grover's Algorithm (~128-bit PQ security)",
                "severity":    "MEDIUM",
                "remediation": REMEDIATION["hash_weak"],
            })
            score += 1
        else:
            findings.append({
                "category":    "Hash Function",
                "finding":     f"{hash_algo} — hash algorithm not recognised, manual review recommended",
                "severity":    "UNKNOWN",
                "remediation": REMEDIATION["unknown"],
            })
            score += 1

    # ── 5. Cipher Suite ───────────────────────────────────────────────────────
    if cipher and cipher not in ("Unknown", "—"):
        if any(c.lower() in cipher.lower() for c in CIPHER_SAFE):
            findings.append({
                "category":    "Cipher Suite",
                "finding":     f"{cipher} — Grover-resistant cipher (AES-256 / ChaCha20)",
                "severity":    "INFO",
                "remediation": REMEDIATION["cipher_safe"],
            })
        elif any(c.lower() in cipher.lower() for c in CIPHER_WEAK):
            findings.append({
                "category":    "Cipher Suite",
                "finding":     f"{cipher} provides insufficient post-quantum symmetric security",
                "severity":    "MEDIUM",
                "remediation": REMEDIATION["cipher_weak"],
            })
            score += 1

    return findings, min(score, 10)


# ─── CLI Print Helper ─────────────────────────────────────────────────────────

SEV_ORDER = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "UNKNOWN": 3, "INFO": 4, "PASS": 5}

def print_risk_report(findings, score):
    print("\n==============================")
    print("    QUANTUM RISK REPORT")
    print("==============================")
    print(f"Risk Score: {score}/10")
    print()

    if not findings:
        print("No findings generated.")
        return

    sorted_findings = sorted(findings, key=lambda f: SEV_ORDER.get(f["severity"], 9))

    for f in sorted_findings:
        print(f"[{f['severity']}] {f['category']}")
        print(f"  Finding:     {f['finding']}")
        print(f"  Remediation: {f['remediation']}")
        print()