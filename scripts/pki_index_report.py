#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
import json
from pathlib import Path
from typing import Dict, List, Optional


def parse_openssl_time(raw: str) -> Optional[dt.datetime]:
    value = raw.strip()
    if not value:
        return None
    return dt.datetime.strptime(value, "%y%m%d%H%M%SZ").replace(tzinfo=dt.timezone.utc)


def extract_cn(subject: str) -> str:
    marker = "/CN="
    if marker not in subject:
        return subject.strip("/")
    return subject.split(marker, 1)[1]


def parse_index(path: Path) -> List[Dict[str, object]]:
    rows: List[Dict[str, object]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
      if not line.strip():
          continue
      parts = line.split("\t")
      if len(parts) < 6:
          continue
      raw_status, not_after_raw, revoked_raw, serial, _, subject = parts[:6]
      not_after = parse_openssl_time(not_after_raw)
      revoked_at = parse_openssl_time(revoked_raw) if revoked_raw else None
      cn = extract_cn(subject)
      expired = bool(not_after and not_after < dt.datetime.now(dt.timezone.utc))
      if raw_status == "R":
          status = "revoked"
      elif expired:
          status = "expired"
      elif raw_status == "V":
          status = "valid"
      else:
          status = raw_status.lower()
      rows.append(
          {
              "raw_status": raw_status,
              "status": status,
              "cn": cn,
              "subject": subject,
              "serial": serial,
              "not_after": not_after,
              "revoked_at": revoked_at,
          }
      )
    return rows


def latest_by_cn(rows: List[Dict[str, object]]) -> List[Dict[str, object]]:
    latest: Dict[str, Dict[str, object]] = {}
    for row in rows:
        latest[str(row["cn"])] = row
    return sorted(latest.values(), key=lambda item: str(item["cn"]))


def render_list(rows: List[Dict[str, object]]) -> str:
    latest_rows = latest_by_cn(rows)
    if not latest_rows:
        return "No PKI entries found."
    headers = ["CN", "STATUS", "EXPIRES_AT_UTC", "SERIAL"]
    table = [headers]
    for row in latest_rows:
        expires_at = row["not_after"].strftime("%Y-%m-%d %H:%M:%S") if row["not_after"] else "-"
        table.append([str(row["cn"]), str(row["status"]), expires_at, str(row["serial"])])
    widths = [max(len(line[idx]) for line in table) for idx in range(len(headers))]
    return "\n".join("  ".join(cell.ljust(widths[idx]) for idx, cell in enumerate(line)) for line in table)


def render_summary(rows: List[Dict[str, object]]) -> str:
    latest_rows = latest_by_cn(rows)
    summary = {"valid": 0, "revoked": 0, "expired": 0, "other": 0, "total_identities": len(latest_rows)}
    for row in latest_rows:
        status = str(row["status"])
        if status in summary:
            summary[status] += 1
        else:
            summary["other"] += 1
    return "\n".join(f"{key}={value}" for key, value in summary.items())


def render_status(rows: List[Dict[str, object]], cn: str) -> str:
    latest_rows = {str(row["cn"]): row for row in latest_by_cn(rows)}
    if cn not in latest_rows:
        return "absent"
    return str(latest_rows[cn]["status"])


def main() -> int:
    parser = argparse.ArgumentParser(description="Parse Easy-RSA/OpenSSL index.txt")
    parser.add_argument("--index", required=True, help="Path to index.txt")
    parser.add_argument("--mode", choices=["list", "summary", "status", "json"], default="list")
    parser.add_argument("--cn", help="Client CN for --mode status")
    args = parser.parse_args()

    rows = parse_index(Path(args.index))

    if args.mode == "list":
        print(render_list(rows))
        return 0

    if args.mode == "summary":
        print(render_summary(rows))
        return 0

    if args.mode == "status":
        if not args.cn:
            raise SystemExit("--cn is required for --mode status")
        print(render_status(rows, args.cn))
        return 0

    latest_rows = latest_by_cn(rows)
    normalized = []
    for row in latest_rows:
        normalized.append(
            {
                "cn": row["cn"],
                "status": row["status"],
                "serial": row["serial"],
                "subject": row["subject"],
                "not_after": row["not_after"].isoformat() if row["not_after"] else None,
                "revoked_at": row["revoked_at"].isoformat() if row["revoked_at"] else None,
            }
        )
    print(json.dumps(normalized, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
