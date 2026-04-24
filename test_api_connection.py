"""
Diagnostic checks for OpenRouter connectivity.

This script does not print or validate the API key value. It only reports
whether OPENROUTER_API_KEY is present after loading .env.
"""

import os
import socket
from urllib.parse import urlparse

import requests
from dotenv import load_dotenv


OPENROUTER_HOST = "openrouter.ai"
OPENROUTER_MODELS_URL = "https://openrouter.ai/api/v1/models"
OPENROUTER_CHAT_URL = "https://openrouter.ai/api/v1/chat/completions"
INTERNET_TEST_URL = "https://example.com"
TIMEOUT_SECONDS = 10


def print_result(name: str, ok: bool, detail: str) -> None:
    status = "OK" if ok else "FAIL"
    print(f"[{status}] {name}: {detail}")


def check_api_key_loaded() -> bool:
    load_dotenv()
    exists = bool(os.getenv("OPENROUTER_API_KEY"))
    print_result(
        "OPENROUTER_API_KEY loaded",
        exists,
        "present" if exists else "missing",
    )
    return exists


def check_internet_access() -> bool:
    try:
        response = requests.get(INTERNET_TEST_URL, timeout=TIMEOUT_SECONDS)
        print_result(
            "Internet access",
            True,
            f"{INTERNET_TEST_URL} returned HTTP {response.status_code}",
        )
        return True
    except requests.RequestException as exc:
        print_result("Internet access", False, str(exc))
        return False


def check_dns_resolution(hostname: str = OPENROUTER_HOST) -> bool:
    try:
        addresses = socket.getaddrinfo(hostname, 443, type=socket.SOCK_STREAM)
        unique_ips = sorted({item[4][0] for item in addresses})
        print_result(
            "DNS resolution",
            True,
            f"{hostname} resolved to {', '.join(unique_ips[:5])}",
        )
        return True
    except socket.gaierror as exc:
        print_result("DNS resolution", False, f"{hostname}: {exc}")
        return False


def check_endpoint_reachability(url: str, label: str) -> bool:
    try:
        response = requests.get(url, timeout=TIMEOUT_SECONDS)
        reachable = response.status_code < 500
        detail = f"{urlparse(url).path or '/'} returned HTTP {response.status_code}"
        print_result(label, reachable, detail)
        return reachable
    except requests.RequestException as exc:
        print_result(label, False, str(exc))
        return False


def main() -> int:
    print("=" * 70)
    print("OpenRouter Connectivity Diagnostic")
    print("=" * 70)

    results = [
        check_api_key_loaded(),
        check_internet_access(),
        check_dns_resolution(),
        check_endpoint_reachability(OPENROUTER_MODELS_URL, "OpenRouter models endpoint"),
        check_endpoint_reachability(OPENROUTER_CHAT_URL, "OpenRouter chat endpoint"),
    ]

    print("=" * 70)
    if all(results):
        print("All diagnostic checks passed.")
        return 0

    print("One or more diagnostic checks failed.")
    print("If you see WinError 10013, Windows security software, firewall rules,")
    print("VPN/proxy settings, or sandbox permissions may be blocking outbound sockets.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
