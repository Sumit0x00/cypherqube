import subprocess
import re
from risk_engine import analyze_quantum_risk, print_risk_report


# ─── OpenSSL Raw Output ───────────────────────────────────────────────────────

def run_openssl(target, port):
    try:
        cmd = [
            "openssl", "s_client",
            "-connect", f"{target}:{port}",
            "-servername", target,
            "-brief"
        ]
        result = subprocess.run(
            cmd,
            input="Q\n",
            capture_output=True,
            text=True,
            timeout=15
        )
        return result.stdout + result.stderr

    except subprocess.TimeoutExpired:
        print(f"[scanner] Timeout connecting to {target}:{port}")
        return None
    except Exception as e:
        print(f"[scanner] OpenSSL error: {e}")
        return None


# ─── TLS Field Extractors ─────────────────────────────────────────────────────

def extract_tls_version(output):
    match = re.search(r"Protocol\s*version:\s*(TLSv[\d.]+)", output, re.IGNORECASE)
    return match.group(1) if match else "Unknown"


def extract_cipher(output):
    match = re.search(r"Ciphersuite:\s*([A-Z0-9_\-]+)", output, re.IGNORECASE)
    return match.group(1) if match else "Unknown"


def extract_signature(output):
    match = re.search(r"Signature\s*type:\s*([A-Za-z0-9\-_]+)", output, re.IGNORECASE)
    return match.group(1) if match else "Unknown"


def extract_hash(output):
    match = re.search(r"Hash\s*used:\s*([A-Za-z0-9\-_]+)", output, re.IGNORECASE)
    return match.group(1) if match else "Unknown"


def extract_key_exchange(output):
    """
    Parses 'Server Temp Key: X25519, 253 bits'
    Returns just the algorithm name e.g. 'X25519'
    """
    match = re.search(r"Server Temp Key:\s*([A-Za-z0-9\-_]+)", output, re.IGNORECASE)
    return match.group(1) if match else "Unknown"


# ─── Certificate Fetching & Parsing ──────────────────────────────────────────

def get_certificate(target, port):
    try:
        cmd = f"echo Q | openssl s_client -connect {target}:{port} -servername {target} -showcerts 2>/dev/null"
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=15
        )
        return result.stdout if result.stdout else None

    except subprocess.TimeoutExpired:
        print(f"[scanner] Timeout fetching certificate from {target}:{port}")
        return None
    except Exception as e:
        print(f"[scanner] Certificate fetch error: {e}")
        return None


def parse_certificate(cert_output):
    """Parse raw PEM output through openssl x509 -text."""
    if not cert_output:
        return None
    try:
        proc = subprocess.run(
            ["openssl", "x509", "-text", "-noout"],
            input=cert_output,
            text=True,
            capture_output=True,
            timeout=10
        )
        return proc.stdout if proc.stdout else None

    except Exception as e:
        print(f"[scanner] Certificate parse error: {e}")
        return None


# ─── Certificate Field Extractors ────────────────────────────────────────────

def extract_cert_public_key(cert_text):
    if not cert_text:
        return "Unknown", "Unknown"

    algo = re.search(r"Public Key Algorithm:\s*(.*)", cert_text)
    size = re.search(r"Public-Key:\s*\((\d+)\s*bit\)", cert_text)

    algo_val = algo.group(1).strip() if algo else "Unknown"
    size_val = size.group(1) if size else "Unknown"

    return algo_val, size_val


def extract_cert_signature(cert_text):
    if not cert_text:
        return "Unknown"
    match = re.search(r"Signature Algorithm:\s*(.*)", cert_text)
    return match.group(1).strip() if match else "Unknown"


def extract_cert_issuer(cert_text):
    if not cert_text:
        return "Unknown"
    match = re.search(r"Issuer:\s*(.*)", cert_text)
    return match.group(1).strip() if match else "Unknown"


def extract_cert_expiry(cert_text):
    if not cert_text:
        return "Unknown"
    match = re.search(r"Not After\s*:\s*(.*)", cert_text)
    return match.group(1).strip() if match else "Unknown"


# ─── Print Inventory (CLI) ────────────────────────────────────────────────────

def print_crypto_inventory(inventory):
    print("\n==============================")
    print("      CRYPTO INVENTORY")
    print("==============================")
    print(f"Target: {inventory['target']}")

    print("\n--- TLS Configuration ---")
    print(f"TLS Version  : {inventory['tls_version']}")
    print(f"Cipher Suite : {inventory['cipher_suite']}")
    print(f"Hash Function: {inventory['hash_function']}")
    print(f"Key Exchange : {inventory['key_exchange']}")
    print(f"TLS Signature: {inventory['tls_signature']}")

    cert = inventory["certificate"]
    print("\n--- Certificate Details ---")
    print(f"Public Key Algorithm: {cert['public_key_algorithm']}")
    print(f"Key Size            : {cert['key_size']} bits")
    print(f"Cert Signature      : {cert['signature_algorithm']}")
    print(f"Issuer              : {cert['issuer']}")
    print(f"Expiry              : {cert['expiry']}")


# ─── Main Entry Point ─────────────────────────────────────────────────────────

def analyze_target(target, port):
    """
    Full TLS scan pipeline:
      1. Run openssl s_client -brief  → TLS version, cipher, hash, key exchange, signature
      2. Run openssl s_client -showcerts + x509 -text → certificate details
      3. Build crypto inventory dict
      4. Run quantum risk engine → findings + score
      5. Return full report dict
    """

    # ── Step 1: TLS handshake info ────────────────────────────────────────────
    raw_output = run_openssl(target, port)

    if not raw_output:
        print(f"[scanner] Failed to retrieve TLS data from {target}:{port}")
        return None

    tls_version    = extract_tls_version(raw_output)
    cipher         = extract_cipher(raw_output)
    signature_algo = extract_signature(raw_output)
    hash_algo      = extract_hash(raw_output)
    key_exchange   = extract_key_exchange(raw_output)

    # ── Step 2: Certificate details ───────────────────────────────────────────
    cert_raw  = get_certificate(target, port)
    cert_text = parse_certificate(cert_raw)

    pub_algo, key_size = extract_cert_public_key(cert_text)
    cert_signature     = extract_cert_signature(cert_text)
    issuer             = extract_cert_issuer(cert_text)
    expiry             = extract_cert_expiry(cert_text)

    # ── Step 3: Build crypto inventory ───────────────────────────────────────
    crypto_inventory = {
        "target":        f"{target}:{port}",
        "port":          port,
        "tls_version":   tls_version,
        "cipher_suite":  cipher,
        "hash_function": hash_algo,
        "key_exchange":  key_exchange,
        "tls_signature": signature_algo,
        "certificate": {
            "public_key_algorithm": pub_algo,
            "key_size":             key_size,
            "signature_algorithm":  cert_signature,
            "issuer":               issuer,
            "expiry":               expiry,
        }
    }

    # ── Step 4: Quantum risk scoring ──────────────────────────────────────────
    # Score is derived entirely from real scan values above.
    # risk_engine.py checks each algorithm against known vulnerable/safe lists
    # and assigns weighted scores (max 10):
    #   Key Exchange vulnerable  → +3
    #   TLS Signature vulnerable → +2
    #   Cert Public Key vuln.    → +2
    #   Hash weak (Grover)       → +1
    #   Cipher weak (Grover)     → +1
    risks, score = analyze_quantum_risk(crypto_inventory)

    # CLI print
    print_crypto_inventory(crypto_inventory)
    print_risk_report(risks, score)

    # ── Step 5: Return full report ────────────────────────────────────────────
    crypto_inventory["quantum_risk"] = {
        "risk_score": score,
        "findings":   risks,
    }

    return crypto_inventory