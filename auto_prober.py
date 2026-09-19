#!/usr/bin/env python3
"""
Confluence Backend Auto-Prober & Keep-Alive Service
--------------------------------------------------
Periodically sends lightweight health check requests to prevent Render free-tier
spin-downs (which occur after 15 minutes of inactivity).
"""

import sys
import os
import time
import argparse
import datetime
import urllib.request
import urllib.error
import json

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

DEFAULT_TARGET = os.environ.get(
    "PROBER_TARGET_URL", 
    "https://confluence-backend-8334.onrender.com/healthz/"
)
# Render sleeps after 15 minutes of inactivity. 14 minutes minimizes total requests while keeping backend hot.
DEFAULT_INTERVAL_MINUTES = 14

def ping(url: str, timeout: int = 25):
    start = time.time()
    headers = {
        "User-Agent": "Confluence-KeepAlive-Prober/1.0",
        "Accept": "*/*",
    }
    # Uses HTTP HEAD to request headers only (0 bytes body payload)
    req = urllib.request.Request(url, headers=headers, method="HEAD")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            latency = (time.time() - start) * 1000
            status = response.status
            return status, latency, "Headers received (0 bytes body)"
    except urllib.error.HTTPError as e:
        latency = (time.time() - start) * 1000
        # If /healthz returned 404 (e.g. pending deploy), probe /api/users/ as secondary fallback
        if e.code == 404 and "healthz" in url:
            fallback_url = url.replace("healthz/", "api/users/")
            try:
                with urllib.request.urlopen(urllib.request.Request(fallback_url, headers=headers, method="HEAD"), timeout=timeout):
                    pass
            except Exception:
                pass
        return e.code, latency, f"HTTPError: {e.reason}"
    except urllib.error.URLError as e:
        latency = (time.time() - start) * 1000
        return 0, latency, f"URLError: {e.reason}"
    except Exception as e:
        latency = (time.time() - start) * 1000
        return -1, latency, str(e)

def run_prober(target_url: str, interval_minutes: float, once: bool = False):
    interval_seconds = interval_minutes * 60
    print("=" * 65)
    print("  CONFLUENCE BACKEND AUTO-PROBER & KEEP-ALIVE")
    print("=" * 65)
    print(f" Target URL : {target_url}")
    print(f" Interval   : {interval_minutes} minutes ({int(interval_seconds)} seconds)")
    print(f" Purpose    : Keep Render backend hot & prevent 15-min idle spin-down")
    print("=" * 65)
    print(" Press Ctrl+C to stop.\n")

    iteration = 1
    while True:
        now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{now_str}] Probe #{iteration} -> Pinging {target_url}...")
        status, latency, body = ping(target_url)

        if status in (200, 204, 301, 302):
            tag = "[OK]"
            state = "HEALTHY / AWAKE"
        elif status in (401, 403, 404):
            tag = "[ACTIVE]"
            state = f"RESPONDING (HTTP {status})"
        elif status == 0:
            tag = "[FAIL]"
            state = f"CONNECTION FAILED: {body}"
        else:
            tag = "[ERR]"
            state = f"ERROR (HTTP {status}): {body}"

        print(f"  {tag} Result: {state} | Latency: {latency:.1f}ms")
        
        if once:
            break

        iteration += 1
        print(f"  Sleeping for {interval_minutes} minutes until next probe...\n")
        
        try:
            time.sleep(interval_seconds)
        except KeyboardInterrupt:
            print("\nProber stopped by user.")
            break

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Confluence Backend Keep-Alive Auto-Prober")
    parser.add_argument("--url", default=DEFAULT_TARGET, help="Backend URL to probe (default: Render backend)")
    parser.add_argument("--interval", type=float, default=DEFAULT_INTERVAL_MINUTES, help="Interval in minutes (default: 12)")
    parser.add_argument("--once", "-once", action="store_true", help="Send single probe and exit")
    args = parser.parse_args()

    run_prober(args.url, args.interval, args.once)
