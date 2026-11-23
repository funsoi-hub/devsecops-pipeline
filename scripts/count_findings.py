#!/usr/bin/env python3
"""Count high-severity findings in a scanner report and print a Markdown table.

Usage: count_findings.py <tool> <report.json> [summary.md]
Prints the count on stdout's last line; appends a findings table to summary.md.
Kept dependency-free so it runs on any runner.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path


def semgrep(data):
    for r in data.get("results", []):
        yield r["check_id"].split(".")[-1], f'{r["path"]}:{r["start"]["line"]}', r["extra"]["message"]


def bandit(data):
    for r in data.get("results", []):
        yield f'{r["test_id"]} {r["test_name"]}', f'{r["filename"]}:{r["line_number"]}', r["issue_text"]


def gitleaks(data):
    for r in data or []:
        yield r["RuleID"], f'{r["File"]}:{r["StartLine"]} ({r["Commit"][:7]})', "Secret committed to git history"


def trivy(data):
    for result in data.get("Results", []) or []:
        for v in result.get("Vulnerabilities") or []:
            fix = v.get("FixedVersion") or "no fix yet"
            yield v["VulnerabilityID"], f'{v["PkgName"]} {v["InstalledVersion"]} -> {fix}', \
                f'{v["Severity"]}: {(v.get("Title") or "")[:90]}'
        for m in result.get("Misconfigurations") or []:
            if m.get("Status") == "FAIL":
                yield m["ID"], result.get("Target", ""), f'{m["Severity"]}: {m["Title"]}'


def zap(data):
    for site in data.get("site", []):
        for a in site.get("alerts", []):
            if int(a.get("riskcode", 0)) >= 3:  # 3 = High
                yield f'{a["pluginid"]} {a["name"]}', f'{a.get("count", "?")} instance(s)', "High risk"


PARSERS = {"semgrep": semgrep, "bandit": bandit, "gitleaks": gitleaks, "trivy": trivy, "zap": zap}


def main() -> None:
    tool, report = sys.argv[1], Path(sys.argv[2])
    summary = Path(sys.argv[3]) if len(sys.argv) > 3 else None
    data = json.loads(report.read_text()) if report.exists() and report.stat().st_size else {}
    rows = list(PARSERS[tool](data))
    if summary:
        with summary.open("a") as f:
            f.write(f"\n#### {tool}: {len(rows)} high-severity finding(s)\n")
            if rows:
                f.write("\n| Rule | Location | Detail |\n|---|---|---|\n")
                for rule, loc, detail in rows[:50]:
                    clean = lambda s: str(s).replace("|", "\\|").replace("\n", " ")  # noqa: E731
                    f.write(f"| {clean(rule)} | `{clean(loc)}` | {clean(detail)} |\n")
                if len(rows) > 50:
                    f.write(f"\n_...and {len(rows) - 50} more. Download the report artifact for all of them._\n")
    print(len(rows))


if __name__ == "__main__":
    main()
