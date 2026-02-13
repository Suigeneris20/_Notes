#!/usr/bin/env python3
"""
Fetch SonarQube issues from a UI link and enrich each with SCM commit info (author, revision, date)
using only the SonarQube Web API.

Usage examples:
  export SONAR_TOKEN=your_sonar_token
  python sq_issues_with_commit.py --url "https://sq.example.com/project/issues?id=myproj&resolved=false&branch=main" --out issues.csv
  python sq_issues_with_commit.py --url "https://sq.example.com/project/issues?id=myproj&types=BUG&severities=CRITICAL" --json

Outputs:
  - CSV (default) to stdout or --out file
  - JSON with --json

Notes:
  - Requires SCM blame to be available in your SonarQube server for the relevant project.
  - Branch / pullRequest params are honored so SCM info matches the same context.
"""

import os
import sys
import csv
import json
import argparse
from urllib.parse import urlparse, parse_qs, urlunparse
import requests
from collections import defaultdict

# Increase if you want more per-page results (SonarQube caps this at 500)
MAX_PAGE_SIZE = 500
SESSION = requests.Session()
SESSION.headers.update({"Accept": "application/json"})

# Whitelist of /api/issues/search parameters we'll try to map from the UI link.
ISSUES_SEARCH_ALLOWED_PARAMS = {
    "projects", "componentKeys", "resolved", "severities", "types", "rules", "tags",
    "assignees", "authors", "createdAfter", "createdBefore", "statuses",
    "resolutions", "branch", "pullRequest", "ps", "p", "sinceLeakPeriod",
    "q", "languages", "directories", "files", "impactSeverities", "impactSoftwareQualities",
    "sort", "asc", "s"  # 's' is older sort key; 'sort'/'asc' are newer
}

def parse_issues_url(ui_url: str):
    """
    Parse a SonarQube UI issues URL into:
      - base_url (scheme://host)
      - mapped query params for /api/issues/search
    """
    parsed = urlparse(ui_url)
    base_url = urlunparse((parsed.scheme, parsed.netloc, "", "", "", ""))

    # Convert UI query params to API params
    ui_qs = parse_qs(parsed.query)

    # Map common UI param 'id' to API 'projects'
    mapped = {}
    for k, vals in ui_qs.items():
        if not vals:
            continue
        # Flatten multi-value parameters into comma-separated strings
        val = ",".join(vals)

        if k == "id":
            mapped["projects"] = val
            continue

        # Directly keep if in whitelist
        if k in ISSUES_SEARCH_ALLOWED_PARAMS:
            mapped[k] = val

        # Some UI params differ by name; add a few courteous mappings here:
        elif k == "assignee":  # in case a single 'assignee' is used
            mapped["assignees"] = val
        elif k == "author":    # if UI uses singular author
            mapped["authors"] = val
        # Ignore otherwise

    # Ensure page size
    if "ps" not in mapped:
        mapped["ps"] = str(MAX_PAGE_SIZE)
    if "p" not in mapped:
        mapped["p"] = "1"

    return base_url, mapped


def auth_headers(token: str | None):
    """
    Build basic auth header for SonarQube token.
    SonarQube expects Basic auth with token as username and empty password.
    """
    if not token:
        return {}
    # requests supports passing auth=(token, "") which builds the correct header
    return {"auth": (token, "")}


def fetch_all_issues(base_url: str, params: dict, token: str | None):
    """
    Paginate through /api/issues/search and return a list of issues.
    """
    issues = []
    page = 1
    ps = int(params.get("ps", MAX_PAGE_SIZE))

    while True:
        params["p"] = str(page)
        resp = SESSION.get(f"{base_url}/api/issues/search", params=params, **auth_headers(token))
        if resp.status_code != 200:
            raise RuntimeError(f"Failed to fetch issues (HTTP {resp.status_code}): {resp.text}")

        data = resp.json()
        batch = data.get("issues", [])
        issues.extend(batch)

        paging = data.get("paging", {})
        total = paging.get("total", len(issues))
        pages = (total + ps - 1) // ps if ps else 1

        if page >= pages or not batch:
            break
        page += 1

    return issues


def collect_line_ranges_by_component(issues):
    """
    Build a dict keyed by (componentKey, branch, pullRequest) -> (min_line, max_line)
    Only includes issues that have a line (textRange.startLine or 'line').
    """
    ranges = {}
    for it in issues:
        comp = it.get("component")
        if not comp:
            continue

        # Prefer textRange.startLine; fallback to legacy 'line'
        line = None
        tr = it.get("textRange")
        if tr and isinstance(tr, dict):
            line = tr.get("startLine")
        if line is None:
            line = it.get("line")

        if line is None:
            # No line-level info (e.g., file-level issue)
            continue

        # Try to keep branch/PR context consistent; the search itself scopes to branch/PR,
        # but for sources/scm we include them explicitly if available in params context.
        # The issue object typically doesn’t contain branch/pr directly, so we’ll allow None.
        key = (comp, it.get("branch"), it.get("pullRequest"))
        if key not in ranges:
            ranges[key] = [line, line]
        else:
            if line < ranges[key][0]:
                ranges[key][0] = line
            if line > ranges[key][1]:
                ranges[key][1] = line
    return ranges


def fetch_scm_for_component(base_url: str, token: str | None, component_key: str, line_from: int, line_to: int, branch: str | None, pull_request: str | None):
    """
    Fetch SCM blame info for a component (file) between line_from and line_to inclusive.
    Returns dict: line -> {author, date, revision}
    """
    params = {"key": component_key, "from": line_from, "to": line_to}
    if branch:
        params["branch"] = branch
    if pull_request:
        params["pullRequest"] = pull_request

    resp = SESSION.get(f"{base_url}/api/sources/scm", params=params, **auth_headers(token))
    if resp.status_code != 200:
        # Some SonarQube versions / permissions might not allow SCM; be resilient
        return {}

    data = resp.json()
    # Expecting data like: {"scm":[{"line":123,"author":"...","date":"...","revision":"..."}]}
    entries = data.get("scm") or data.get("lines") or []
    by_line = {}
    for e in entries:
        ln = e.get("line")
        if ln is None:
            continue
        by_line[ln] = {
            "author": e.get("author"),
            "date": e.get("date"),
            "revision": e.get("revision"),
        }
    return by_line


def enrich_with_scm(base_url: str, token: str | None, issues: list, branch_param: str | None, pr_param: str | None):
    """
    For all issues, fetch SCM blame for the needed line intervals per component and add:
      - scm_author
      - scm_revision
      - scm_date
    """
    # Build ranges grouped by component and context
    # Since issues JSON usually does not include branch/pr per issue, use the global params from the query
    # to keep context. This matches the original filter.
    grouped_ranges = defaultdict(lambda: [10**9, -1])  # min, max
    comp_contexts = set()

    for it in issues:
        comp = it.get("component")
        if not comp:
            continue
        # derive line
        line = None
        tr = it.get("textRange")
        if tr and isinstance(tr, dict):
            line = tr.get("startLine")
        if line is None:
            line = it.get("line")
        if line is None:
            continue
        key = (comp, branch_param, pr_param)
        comp_contexts.add(key)
        r = grouped_ranges[key]
        if line < r[0]:
            r[0] = line
        if line > r[1]:
            r[1] = line

    # Fetch blame per component-context range
    blame_cache = {}
    for (comp, br, pr) in comp_contexts:
        r = grouped_ranges[(comp, br, pr)]
        if r[1] < r[0] or r[0] == 10**9:
            continue
        blame_cache[(comp, br, pr)] = fetch_scm_for_component(base_url, token, comp, r[0], r[1], br, pr)

    # Attach SCM info to each issue
    enriched = []
    for it in issues:
        comp = it.get("component")
        tr = it.get("textRange")
        line = None
        if tr and isinstance(tr, dict):
            line = tr.get("startLine")
        if line is None:
            line = it.get("line")

        br = branch_param
        pr = pr_param
        info = None
        if comp and line is not None:
            info = blame_cache.get((comp, br, pr), {}).get(line)

        enriched.append({
            "issueKey": it.get("key"),
            "rule": it.get("rule"),
            "severity": it.get("severity"),
            "type": it.get("type"),
            "message": it.get("message"),
            "project": it.get("project"),
            "component": comp,
            "line": line,
            "scm_author": (info or {}).get("author"),
            "scm_revision": (info or {}).get("revision"),
            "scm_date": (info or {}).get("date"),
            # Also include assignee and status if you want
            "assignee": it.get("assignee"),
            "status": it.get("status"),
        })
    return enriched


def write_csv(rows, out_fp):
    writer = csv.DictWriter(out_fp, fieldnames=[
        "issueKey", "rule", "severity", "type", "message",
        "project", "component", "line",
        "scm_author", "scm_revision", "scm_date",
        "assignee", "status",
    ])
    writer.writeheader()
    writer.writerows(rows)


def main():
    ap = argparse.ArgumentParser(description="Fetch SonarQube issues from a UI link and enrich with SCM commit info.")
    ap.add_argument("--url", required=True, help="SonarQube issues page URL (e.g., https://sq/project/issues?id=proj&resolved=false)")
    ap.add_argument("--token", default=os.environ.get("SONAR_TOKEN"), help="SonarQube user token (or set SONAR_TOKEN env var)")
    ap.add_argument("--out", help="Output CSV file path (default: stdout)")
    ap.add_argument("--json", action="store_true", help="Output JSON instead of CSV")
    ap.add_argument("--insecure", action="store_true", help="Allow insecure TLS (verify=False)")
    args = ap.parse_args()

    if args.insecure:
        SESSION.verify = False
        requests.packages.urllib3.disable_warnings(category=requests.packages.urllib3.exceptions.InsecureRequestWarning)

    base_url, mapped_params = parse_issues_url(args.url)

    # Keep branch/pr handy for SCM context
    branch_param = mapped_params.get("branch")
    pr_param = mapped_params.get("pullRequest")

    # Fetch issues
    issues = fetch_all_issues(base_url, mapped_params, args.token)

    if not issues:
        out = [] if args.json else []
        if args.json:
            print("[]")
        else:
            # still print CSV header
            out_fp = open(args.out, "w", newline="", encoding="utf-8") if args.out else sys.stdout
            write_csv([], out_fp)
            if args.out:
                out_fp.close()
        return

    # Enrich with SCM
    enriched = enrich_with_scm(base_url, args.token, issues, branch_param, pr_param)

    # Output
    if args.json:
        out_data = enriched
        if args.out:
            with open(args.out, "w", encoding="utf-8") as f:
                json.dump(out_data, f, indent=2)
        else:
            json.dump(out_data, sys.stdout, indent=2)
            print()
    else:
        out_fp = open(args.out, "w", newline="", encoding="utf-8") if args.out else sys.stdout
        write_csv(enriched, out_fp)
        if args.out:
            out_fp.close()


if __name__ == "__main__":
    main()
