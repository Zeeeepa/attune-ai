#!/usr/bin/env python3
"""attune-ai download stats tracker.

Pull PyPI download statistics from multiple sources and display them
in the terminal. Optionally log to CSV for trend tracking.

Usage:
    python scripts/download_stats.py              # quick summary
    python scripts/download_stats.py --log        # summary + append to CSV
    python scripts/download_stats.py --json       # raw JSON output
    python scripts/download_stats.py --watch 300  # refresh every 5 min
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError

PACKAGE = "attune-ai"
LOG_FILE = Path(__file__).resolve().parent.parent / "logs" / "download_stats.csv"

# ── data sources ──────────────────────────────────────────────────


def fetch_json(url: str, timeout: int = 10) -> dict | None:
    """GET a JSON endpoint, return parsed dict or None on failure."""
    try:
        req = Request(url, headers={"User-Agent": "attune-ai-stats/1.0"})
        with urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read())
    except (URLError, HTTPError, json.JSONDecodeError) as exc:
        print(f"  ⚠  {url} → {exc}", file=sys.stderr)
        return None


def get_pypistats(package: str) -> dict:
    """Fetch from pypistats.org API (official BigQuery mirror)."""
    base = f"https://pypistats.org/api/packages/{package}"
    recent = fetch_json(f"{base}/recent")
    overall = fetch_json(f"{base}/overall?mirrors=true")

    result: dict = {}
    if recent and "data" in recent:
        result["last_day"] = recent["data"].get("last_day", 0)
        result["last_week"] = recent["data"].get("last_week", 0)
        result["last_month"] = recent["data"].get("last_month", 0)

    if overall and "data" in overall:
        total = sum(row.get("downloads", 0) for row in overall["data"])
        result["total_overall"] = total

    return result


def get_pepy(package: str) -> dict:
    """Fetch from pepy.tech API."""
    data = fetch_json(f"https://api.pepy.tech/api/v2/projects/{package}")
    if not data:
        return {}
    return {
        "pepy_total": data.get("total_downloads", 0),
        "pepy_versions": {
            v: info.get("downloads", 0) for v, info in (data.get("versions", {}) or {}).items()
        },
    }


def get_pypi_meta(package: str) -> dict:
    """Fetch basic metadata from PyPI JSON API."""
    data = fetch_json(f"https://pypi.org/pypi/{package}/json")
    if not data:
        return {}
    info = data.get("info", {})
    releases = data.get("releases", {})
    return {
        "current_version": info.get("version", "?"),
        "release_count": len(releases),
        "yanked_count": sum(
            1 for files in releases.values() for f in files if f.get("yanked", False)
        ),
    }


# ── display ───────────────────────────────────────────────────────


def fmt(n: int | None) -> str:
    if n is None or n < 0:
        return "n/a"
    return f"{n:,}"


def print_report(stats: dict) -> None:
    ts = stats.get("timestamp", "?")
    ver = stats.get("current_version", "?")
    releases = stats.get("release_count", "?")
    yanked = stats.get("yanked_count", 0)

    print()
    print(f"  ╔══════════════════════════════════════════════╗")
    print(f"  ║  attune-ai download stats  ·  {ts[:16]}  ║")
    print(f"  ╠══════════════════════════════════════════════╣")
    print(f"  ║  Version      │ {ver:<27} ║")
    print(
        f"  ║  Releases     │ {releases} ({yanked} yanked){' ' * (22 - len(str(releases)) - len(str(yanked)))}║"
    )
    print(f"  ╠══════════════════════════════════════════════╣")
    print(f"  ║  pypistats.org (BigQuery)                    ║")
    print(f"  ║    Last day   │ {fmt(stats.get('last_day')):<27} ║")
    print(f"  ║    Last week  │ {fmt(stats.get('last_week')):<27} ║")
    print(f"  ║    Last month │ {fmt(stats.get('last_month')):<27} ║")
    print(f"  ║    All time   │ {fmt(stats.get('total_overall')):<27} ║")
    print(f"  ╠══════════════════════════════════════════════╣")
    print(f"  ║  pepy.tech                                   ║")
    print(f"  ║    Total      │ {fmt(stats.get('pepy_total')):<27} ║")

    versions = stats.get("pepy_versions", {})
    if versions:
        # show top 5 versions by downloads
        top = sorted(versions.items(), key=lambda x: x[1], reverse=True)[:5]
        for v, dl in top:
            label = f"    v{v}"
            print(f"  ║  {label:<12} │ {fmt(dl):<27} ║")

    print(f"  ╚══════════════════════════════════════════════╝")
    print()


# ── CSV logging ───────────────────────────────────────────────────


def log_to_csv(stats: dict) -> None:
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    exists = LOG_FILE.exists()
    fields = [
        "timestamp",
        "current_version",
        "release_count",
        "yanked_count",
        "last_day",
        "last_week",
        "last_month",
        "total_overall",
        "pepy_total",
    ]
    with open(LOG_FILE, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        if not exists:
            writer.writeheader()
        writer.writerow(stats)
    print(f"  ✓ Logged to {LOG_FILE}")


# ── main ──────────────────────────────────────────────────────────


def collect() -> dict:
    stats: dict = {"timestamp": datetime.now(timezone.utc).isoformat()}
    print("  Fetching PyPI metadata…")
    stats.update(get_pypi_meta(PACKAGE))
    print("  Fetching pypistats.org…")
    stats.update(get_pypistats(PACKAGE))
    print("  Fetching pepy.tech…")
    stats.update(get_pepy(PACKAGE))
    return stats


def main() -> None:
    parser = argparse.ArgumentParser(description="attune-ai download stats")
    parser.add_argument("--log", action="store_true", help="append stats to CSV")
    parser.add_argument("--json", action="store_true", help="print raw JSON")
    parser.add_argument("--watch", type=int, metavar="SEC", help="refresh interval")
    args = parser.parse_args()

    while True:
        stats = collect()

        if args.json:
            # strip non-serializable bits
            out = {k: v for k, v in stats.items() if k != "pepy_versions"}
            print(json.dumps(out, indent=2))
        else:
            print_report(stats)

        if args.log:
            log_to_csv(stats)

        if args.watch:
            print(f"  ⏳ Next refresh in {args.watch}s (Ctrl+C to stop)")
            try:
                time.sleep(args.watch)
            except KeyboardInterrupt:
                print("\n  Stopped.")
                break
        else:
            break


if __name__ == "__main__":
    main()
