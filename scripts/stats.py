#!/usr/bin/env python3
"""Generate contribution stats SVG cards (dark + light) from the GitHub GraphQL API.

Stdlib only. Requires GITHUB_TOKEN in the environment.
"""

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from xml.sax.saxutils import escape

GRAPHQL_URL = "https://api.github.com/graphql"

QUERY = """
query($login: String!) {
  user(login: $login) {
    contributionsCollection {
      contributionCalendar {
        totalContributions
        weeks {
          contributionDays {
            date
            contributionCount
          }
        }
      }
      totalCommitContributions
      totalPullRequestContributions
      totalIssueContributions
      totalPullRequestReviewContributions
    }
  }
}
"""


def fetch_contributions(login, token):
    body = json.dumps({"query": QUERY, "variables": {"login": login}}).encode("utf-8")
    req = urllib.request.Request(
        GRAPHQL_URL,
        data=body,
        method="POST",
        headers={
            "Authorization": f"bearer {token}",
            "Content-Type": "application/json",
            "Accept": "application/vnd.github+json",
            "User-Agent": "stats-script",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        detail = e.read().decode("utf-8", errors="replace")
        print(f"GitHub API HTTP error {e.code}: {detail}", file=sys.stderr)
        sys.exit(1)
    except urllib.error.URLError as e:
        print(f"GitHub API request failed: {e}", file=sys.stderr)
        sys.exit(1)

    if "errors" in payload and payload["errors"]:
        print(f"GraphQL errors: {payload['errors']}", file=sys.stderr)
        sys.exit(1)

    user = payload.get("data", {}).get("user")
    if not user:
        print(f"GraphQL response missing user data: {payload}", file=sys.stderr)
        sys.exit(1)

    return user["contributionsCollection"]


def flatten_days(calendar):
    days = []
    for week in calendar["weeks"]:
        for day in week["contributionDays"]:
            days.append(
                {
                    "date": datetime.strptime(day["date"], "%Y-%m-%d").date(),
                    "count": day["contributionCount"],
                }
            )
    days.sort(key=lambda d: d["date"])
    return days


def fmt_date(d):
    return f"{d.strftime('%b')} {d.day}"


def fmt_range(start, end):
    if start is None or end is None:
        return "—"  # em dash
    if start == end:
        return fmt_date(start)
    return f"{fmt_date(start)} – {fmt_date(end)}"  # en dash


def current_streak(days):
    """Consecutive count>0 days ending on the last day in the data (treated as
    "today"), or ending the day before if today has zero contributions."""
    if not days:
        return 0, None, None

    idx = len(days) - 1
    if days[idx]["count"] == 0:
        idx -= 1

    if idx < 0 or days[idx]["count"] == 0:
        return 0, None, None

    end = idx
    start = idx
    while start - 1 >= 0 and days[start - 1]["count"] > 0:
        start -= 1

    return (end - start + 1), days[start]["date"], days[end]["date"]


def longest_streak(days):
    best_len, best_start, best_end = 0, None, None
    cur_len, cur_start = 0, None

    for i, d in enumerate(days):
        if d["count"] > 0:
            if cur_len == 0:
                cur_start = i
            cur_len += 1
            if cur_len > best_len:
                best_len = cur_len
                best_start = cur_start
                best_end = i
        else:
            cur_len = 0

    if best_len == 0:
        return 0, None, None

    return best_len, days[best_start]["date"], days[best_end]["date"]


PALETTES = {
    "dark": {
        "bg": "#050505",
        "border": "#ffce1a",
        "border_opacity": "0.25",
        "number": "#ffce1a",
        "label": "#d8c9a8",
        "muted": "#a1a1aa",
    },
    "light": {
        "bg": "#ffffff",
        "border": "#e6e6e6",
        "border_opacity": "1",
        "number": "#b8900a",
        "label": "#333333",
        "muted": "#6b6b6b",
    },
}

FONT_FAMILY = "Inter, -apple-system, Segoe UI, Helvetica, Arial, sans-serif"


def render_svg(login, total, cur_len, cur_range, long_len, long_range, updated, theme):
    p = PALETTES[theme]
    width, height = 600, 160
    col_centers = (100, 300, 500)

    title = escape(f"GitHub contribution stats for {login}", {"\"": "&quot;"})
    updated_text = escape(f"updated {updated.strftime('%Y-%m-%d %H:%M')} UTC")

    def column(cx, number, label, subrange=None):
        parts = [
            f'<text x="{cx}" y="72" text-anchor="middle" font-family="{FONT_FAMILY}" '
            f'font-size="36" font-weight="700" fill="{p["number"]}">{escape(str(number))}</text>',
            f'<text x="{cx}" y="98" text-anchor="middle" font-family="{FONT_FAMILY}" '
            f'font-size="13" fill="{p["label"]}">{escape(label)}</text>',
        ]
        if subrange is not None:
            parts.append(
                f'<text x="{cx}" y="116" text-anchor="middle" font-family="{FONT_FAMILY}" '
                f'font-size="11" fill="{p["muted"]}">{escape(subrange)}</text>'
            )
        return "\n  ".join(parts)

    columns = "\n  ".join(
        [
            column(col_centers[0], total, "Total contributions (past year)"),
            column(col_centers[1], cur_len, "Current streak", cur_range),
            column(col_centers[2], long_len, "Longest streak", long_range),
        ]
    )

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-label="{title}">
  <title>{title}</title>
  <rect x="0.5" y="0.5" width="{width - 1}" height="{height - 1}" rx="6" fill="{p["bg"]}" stroke="{p["border"]}" stroke-opacity="{p["border_opacity"]}" />
  {columns}
  <text x="{width - 10}" y="{height - 12}" text-anchor="end" font-family="{FONT_FAMILY}" font-size="10" fill="{p["muted"]}">{updated_text}</text>
</svg>
"""
    return svg


def main():
    parser = argparse.ArgumentParser(description="Generate GitHub contribution stats SVGs")
    parser.add_argument("--out", default="dist", help="output directory")
    parser.add_argument("--user", default="KrishP147", help="GitHub login")
    args = parser.parse_args()

    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        print("GITHUB_TOKEN environment variable is required", file=sys.stderr)
        sys.exit(1)

    collection = fetch_contributions(args.user, token)
    calendar = collection["contributionCalendar"]
    days = flatten_days(calendar)

    total = calendar["totalContributions"]
    cur_len, cur_start, cur_end = current_streak(days)
    long_len, long_start, long_end = longest_streak(days)

    cur_range = fmt_range(cur_start, cur_end)
    long_range = fmt_range(long_start, long_end)

    updated = datetime.now(timezone.utc)

    os.makedirs(args.out, exist_ok=True)

    for theme, filename in (("dark", "stats-dark.svg"), ("light", "stats.svg")):
        svg = render_svg(
            args.user, total, cur_len, cur_range, long_len, long_range, updated, theme
        )
        path = os.path.join(args.out, filename)
        with open(path, "w", encoding="utf-8", newline="\n") as f:
            f.write(svg)

    print(f"Total contributions (past year): {total}")
    print(f"Current streak: {cur_len} days ({cur_range})")
    print(f"Longest streak: {long_len} days ({long_range})")


if __name__ == "__main__":
    main()
