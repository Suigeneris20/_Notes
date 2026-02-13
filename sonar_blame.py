"""
sonar_issue_blame.py

Given a SonarQube issues URL, fetches all issues with full commit blame info.
Uses only the SonarQube Web API (no sonar-tools dependency needed).

Usage:
    python sonar_issue_blame.py \
        --url "https://sonar.example.com/project/issues?id=my-project&resolved=false" \
        --token "squ_xxxxxxxxxxxxxxxxxxxx" \
        --output report.csv
"""

import argparse
import csv
import json
import sys
from dataclasses import dataclass, field, asdict
from typing import Optional
from urllib.parse import urlparse, parse_qs

import requests


# ──────────────────────────────────────────────
# Data Models
# ──────────────────────────────────────────────

@dataclass
class BlameInfo:
    """Per-line SCM blame detail from /api/sources/scm."""
    revision: str = ""          # commit hash
    commit_author: str = ""     # author email from git
    commit_date: str = ""       # commit timestamp


@dataclass
class EnrichedIssue:
    """An issue merged with its SCM blame info."""
    key: str
    rule: str
    severity: str
    type: str
    component: str              # full SonarQube component key
    file_path: str              # human-readable file path
    line: Optional[int]
    message: str
    author: str                 # SCM author returned by issues/search
    assignee: str
    status: str
    creation_date: str
    update_date: str
    effort: str                 # remediation effort
    tags: str
    # Blame-enriched fields (from /api/sources/scm)
    blame_revision: str = ""
    blame_author: str = ""
    blame_date: str = ""


# ──────────────────────────────────────────────
# URL Parsing
# ──────────────────────────────────────────────

def parse_sonarqube_url(url: str) -> tuple[str, dict]:
    """
    Parse a SonarQube issues URL into (base_url, query_params).

    Handles both formats:
      • .../project/issues?id=proj&resolved=false
      • .../issues?projects=proj&types=BUG
    """
    parsed = urlparse(url)
    base_url = f"{parsed.scheme}://{parsed.netloc}"
    params = {k: v[0] if len(v) == 1 else ",".join(v)
              for k, v in parse_qs(parsed.query).items()}

    # Normalize: SonarQube UI uses 'id' but API uses 'componentKeys' / 'projects'
    if "id" in params and "componentKeys" not in params:
        params["componentKeys"] = params.pop("id")
    if "projects" in params and "componentKeys" not in params:
        params["componentKeys"] = params.pop("projects")

    return base_url, params


# ──────────────────────────────────────────────
# SonarQube API Client
# ──────────────────────────────────────────────

class SonarQubeClient:
    """Lightweight client for the SonarQube Web API."""

    # Maximum page size allowed by SonarQube
    MAX_PAGE_SIZE = 500

    def __init__(self, base_url: str, token: str, verify_ssl: bool = True):
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()
        # Token auth: pass token as username with blank password
        self.session.auth = (token, "")
        self.session.verify = verify_ssl
        self.session.headers.update({"Accept": "application/json"})

    # ── Issues ────────────────────────────────

    def get_issues(self, params: dict) -> list[dict]:
        """
        Paginate through /api/issues/search and return ALL matching issues.

        `params` should include at least 'componentKeys'.
        The 'author' field in each issue is the SCM committer who
        *introduced* the problematic line (populated via git blame).
        """
        endpoint = f"{self.base_url}/api/issues/search"
        all_issues: list[dict] = []
        page = 1

        # Ensure we ask for extra useful fields
        params.setdefault("ps", str(self.MAX_PAGE_SIZE))
        params.setdefault("additionalFields", "comments,rules")
        # s = sort by FILE_LINE for deterministic pagination
        params.setdefault("s", "FILE_LINE")

        while True:
            params["p"] = str(page)
            resp = self.session.get(endpoint, params=params)
            resp.raise_for_status()
            data = resp.json()

            issues = data.get("issues", [])
            all_issues.extend(issues)

            total = data.get("total", 0)
            print(f"  [issues] page {page}: fetched {len(issues)} "
                  f"(total so far: {len(all_issues)}/{total})")

            if len(all_issues) >= total:
                break
            page += 1

        return all_issues

    # ── SCM Blame ─────────────────────────────

    def get_scm_blame(self, component_key: str,
                      from_line: int = 1,
                      to_line: Optional[int] = None) -> dict[int, BlameInfo]:
        """
        Call /api/sources/scm to get per-line blame info for a component.

        Returns {line_number: BlameInfo}.
        """
        endpoint = f"{self.base_url}/api/sources/scm"
        params = {"key": component_key, "from": from_line}
        if to_line:
            params["to"] = to_line

        try:
            resp = self.session.get(endpoint, params=params)
            resp.raise_for_status()
        except requests.HTTPError:
            # SCM data may not exist (e.g., file not in repo, or blame disabled)
            return {}

        scm_data = resp.json().get("scm", [])
        result: dict[int, BlameInfo] = {}
        for entry in scm_data:
            # Each entry: [line_number, commit_hash, author, date]
            line_no = int(entry[0])
            result[line_no] = BlameInfo(
                revision=entry[1] if len(entry) > 1 else "",
                commit_author=entry[2] if len(entry) > 2 else "",
                commit_date=entry[3] if len(entry) > 3 else "",
            )
        return result


# ──────────────────────────────────────────────
# Enrichment Logic
# ──────────────────────────────────────────────

def _file_path_from_component(component_key: str) -> str:
    """Extract the file path portion from a SonarQube component key.

    Component keys look like:  my-project:src/main/java/Foo.java
    """
    parts = component_key.split(":", 1)
    return parts[1] if len(parts) > 1 else component_key


def enrich_issues(client: SonarQubeClient,
                  raw_issues: list[dict],
                  fetch_blame: bool = True) -> list[EnrichedIssue]:
    """
    Convert raw API issues into EnrichedIssue objects.
    Optionally call /api/sources/scm per file to get commit hashes.
    """
    enriched: list[EnrichedIssue] = []

    # Cache blame per component so we don't re-fetch the same file
    blame_cache: dict[str, dict[int, BlameInfo]] = {}

    for i, issue in enumerate(raw_issues, 1):
        component = issue.get("component", "")
        line = issue.get("line") or issue.get("textRange", {}).get("startLine")

        # Build base enriched issue
        ei = EnrichedIssue(
            key=issue.get("key", ""),
            rule=issue.get("rule", ""),
            severity=issue.get("severity", ""),
            type=issue.get("type", ""),
            component=component,
            file_path=_file_path_from_component(component),
            line=line,
            message=issue.get("message", ""),
            author=issue.get("author", ""),        # ← KEY: SCM blame author
            assignee=issue.get("assignee", ""),
            status=issue.get("status", ""),
            creation_date=issue.get("creationDate", ""),
            update_date=issue.get("updateDate", ""),
            effort=issue.get("effort", ""),
            tags=",".join(issue.get("tags", [])),
        )

        # Fetch detailed blame for the specific line
        if fetch_blame and line and component:
            if component not in blame_cache:
                print(f"  [blame] ({i}/{len(raw_issues)}) fetching SCM for {ei.file_path}")
                blame_cache[component] = client.get_scm_blame(
                    component, from_line=1
                )

            blame = blame_cache.get(component, {}).get(line)
            if blame:
                ei.blame_revision = blame.revision
                ei.blame_author = blame.commit_author
                ei.blame_date = blame.commit_date

        enriched.append(ei)

    return enriched


# ──────────────────────────────────────────────
# Output Formatters
# ──────────────────────────────────────────────

def write_csv(issues: list[EnrichedIssue], path: str) -> None:
    if not issues:
        print("No issues to write.")
        return
    fieldnames = list(asdict(issues[0]).keys())
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for issue in issues:
            writer.writerow(asdict(issue))
    print(f"\n✅ Wrote {len(issues)} issues to {path}")


def write_json(issues: list[EnrichedIssue], path: str) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump([asdict(i) for i in issues], f, indent=2)
    print(f"\n✅ Wrote {len(issues)} issues to {path}")


def print_summary(issues: list[EnrichedIssue]) -> None:
    """Print a human-readable summary grouped by committer."""
    from collections import Counter

    print("\n" + "=" * 70)
    print("ISSUES BY COMMITTER (author who introduced the issue)")
    print("=" * 70)

    author_counts = Counter(
        i.blame_author or i.author or "unknown" for i in issues
    )
    for author, count in author_counts.most_common():
        print(f"  {author:<40s}  {count:>5d} issues")

    severity_counts = Counter(i.severity for i in issues)
    print(f"\nSeverity breakdown: {dict(severity_counts)}")
    type_counts = Counter(i.type for i in issues)
    print(f"Type breakdown:     {dict(type_counts)}")
    print(f"Total issues:       {len(issues)}")


# ──────────────────────────────────────────────
# CLI Entry Point
# ──────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Fetch SonarQube issues with git blame commit info."
    )
    parser.add_argument(
        "--url", required=True,
        help="Full SonarQube issues URL from your browser."
    )
    parser.add_argument(
        "--token", required=True,
        help="SonarQube user token (generate at User > My Account > Security)."
    )
    parser.add_argument(
        "--output", default="sonar_issues_blame.csv",
        help="Output file path (.csv or .json)."
    )
    parser.add_argument(
        "--no-blame", action="store_true",
        help="Skip fetching per-line SCM blame (faster, less detail)."
    )
    parser.add_argument(
        "--no-verify-ssl", action="store_true",
        help="Disable SSL certificate verification."
    )
    args = parser.parse_args()

    # 1. Parse the URL
    base_url, params = parse_sonarqube_url(args.url)
    project = params.get("componentKeys", "unknown")
    print(f"🔍 SonarQube server : {base_url}")
    print(f"   Project          : {project}")
    print(f"   Filters          : {params}\n")

    # 2. Connect & fetch issues
    client = SonarQubeClient(base_url, args.token,
                             verify_ssl=not args.no_verify_ssl)
    raw_issues = client.get_issues(params)

    if not raw_issues:
        print("No issues found. Check your URL / filters / permissions.")
        sys.exit(0)

    # 3. Enrich with SCM blame
    enriched = enrich_issues(client, raw_issues,
                             fetch_blame=not args.no_blame)

    # 4. Output
    if args.output.endswith(".json"):
        write_json(enriched, args.output)
    else:
        write_csv(enriched, args.output)

    print_summary(enriched)


if __name__ == "__main__":
    main()
