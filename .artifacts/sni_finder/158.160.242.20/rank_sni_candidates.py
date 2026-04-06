#!/usr/bin/env python3
import argparse
import json
import socket
import ssl
import time


def unique_domains(path):
    domains = []
    seen = set()
    with open(path, "r", encoding="utf-8") as handle:
        for raw_line in handle:
            domain = raw_line.strip()
            if domain and domain not in seen:
                domains.append(domain)
                seen.add(domain)
    return domains


def measure(domain, port, timeout):
    started = time.perf_counter()
    context = ssl.create_default_context()
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE
    context.set_alpn_protocols(["h2", "http/1.1"])
    with socket.create_connection((domain, port), timeout=timeout) as sock:
        with context.wrap_socket(sock, server_hostname=domain):
            elapsed_ms = (time.perf_counter() - started) * 1000
            return True, round(elapsed_ms, 2)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--port", type=int, default=443)
    parser.add_argument("--timeout", type=float, default=5.0)
    parser.add_argument("--top", type=int, default=10)
    args = parser.parse_args()

    domains = unique_domains(args.input)
    results = []
    for domain in domains:
        try:
            ok, elapsed_ms = measure(domain, args.port, args.timeout)
        except Exception:
            continue
        if ok:
            results.append({"domain": domain, "elapsed_ms": elapsed_ms})

    results.sort(key=lambda item: item["elapsed_ms"])
    best = min(results, key=lambda item: item["elapsed_ms"]) if results else None
    print(json.dumps({
        "tested": len(domains),
        "successful": len(results),
        "best_domain": best["domain"] if best else "",
        "best_elapsed_ms": best["elapsed_ms"] if best else None,
        "top_results": results[: max(args.top, 0)],
    }))


if __name__ == "__main__":
    main()
