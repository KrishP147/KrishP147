#!/usr/bin/env node
// Regenerates the <!--START_SECTION:activity--> ... <!--END_SECTION:activity--> block
// in README.md from recent GitHub activity (merged PRs, then recent pushes as filler).
// Run locally: GITHUB_TOKEN=$(gh auth token) node scripts/update-activity.mjs
// Run in CI: invoked by .github/workflows/recent-activity.yml with GITHUB_TOKEN from secrets.

import { readFileSync, writeFileSync } from "node:fs";

const USERNAME = process.env.GH_USERNAME || "KrishP147";
const TOKEN = process.env.GITHUB_TOKEN;
const README_PATH = new URL("../README.md", import.meta.url);
const MAX_ITEMS = 5;
const START = "<!--START_SECTION:activity-->";
const END = "<!--END_SECTION:activity-->";

// Explicit allowlist of active/pinned repos to scan — never falls back to a global
// "everything this token can see" search, so a private repo can never leak into the
// public README even if the workflow token has broader read access.
const ACTIVE_REPOS = [
  "KrishP147/dryft-decode-engine",
  "KrishP147/zephyr",
  "KrishP147/godseye",
  "KrishP147/frameshift",
  "KrishP147/nutrisync",
  "KrishP147/nutrisync-backend",
  "KrishP147/nutrisync-frontend",
  "KrishP147/watspend",
  "KrishP147/examstudyplanner",
  "KrishP147/colourguard",
  "KrishP147/ML-CV-Target-Tracking",
  "KrishP147/autonomous-maze-solving-robot",
  "KrishP147/BaddieLink",
  "KrishP147/ArHackathon2025",
  "KrishP147/youtubetomp3",
  "KrishP147/KrishP147",
  "UWARG/ML-CV-Target-Tracking",
];

if (!TOKEN) {
  console.error("GITHUB_TOKEN not set.");
  process.exit(1);
}

async function gh(path) {
  const res = await fetch(`https://api.github.com${path}`, {
    headers: {
      Authorization: `Bearer ${TOKEN}`,
      Accept: "application/vnd.github+json",
      "X-GitHub-Api-Version": "2022-11-28",
      "User-Agent": `${USERNAME}-profile-activity-bot`,
    },
  });
  if (!res.ok) {
    console.error(`GitHub API ${path} -> ${res.status}`);
    return null;
  }
  return res.json();
}

function fmtDate(iso) {
  return new Date(iso).toISOString().slice(0, 10);
}

function truncate(s, n) {
  s = s.replace(/\s+/g, " ").trim();
  return s.length > n ? s.slice(0, n - 1) + "…" : s;
}

async function mergedPRsForRepo(repo) {
  const data = await gh(`/repos/${repo}/pulls?state=closed&sort=updated&direction=desc&per_page=10`);
  if (!Array.isArray(data)) return [];
  return data
    .filter((pr) => pr.merged_at && pr.user?.login === USERNAME)
    .map((pr) => ({
      date: pr.merged_at,
      line: `**${fmtDate(pr.merged_at)}** — merged PR in [${repo}](${pr.html_url}): ${truncate(pr.title, 80)}`,
    }));
}

async function mergedPRs() {
  const results = await Promise.all(ACTIVE_REPOS.map(mergedPRsForRepo));
  return results.flat();
}

async function recentPushes() {
  const events = await gh(`/users/${USERNAME}/events/public?per_page=50`);
  if (!Array.isArray(events)) return [];
  const allowed = new Set(ACTIVE_REPOS.map((r) => r.toLowerCase()));
  return events
    .filter(
      (e) =>
        e.type === "PushEvent" &&
        e.payload?.commits?.length &&
        allowed.has(e.repo.name.toLowerCase())
    )
    .map((e) => {
      const commit = e.payload.commits[e.payload.commits.length - 1];
      const repo = e.repo.name;
      const url = `https://github.com/${repo}/commit/${commit.sha}`;
      return {
        date: e.created_at,
        line: `**${fmtDate(e.created_at)}** — pushed to [${repo}](${url}): ${truncate(
          commit.message,
          80
        )}`,
      };
    });
}

async function main() {
  const [prs, pushes] = await Promise.all([mergedPRs(), recentPushes()]);

  const seen = new Set();
  const combined = [...prs, ...pushes]
    .sort((a, b) => new Date(b.date) - new Date(a.date))
    .filter((item) => {
      if (seen.has(item.line)) return false;
      seen.add(item.line);
      return true;
    })
    .slice(0, MAX_ITEMS);

  const body = combined.length
    ? combined.map((i) => `- ${i.line}`).join("\n")
    : "- No recent public activity found.";

  const readme = readFileSync(README_PATH, "utf8");
  const startIdx = readme.indexOf(START);
  const endIdx = readme.indexOf(END);
  if (startIdx === -1 || endIdx === -1) {
    console.error(`Markers ${START} / ${END} not found in README.md`);
    process.exit(1);
  }

  const updated =
    readme.slice(0, startIdx + START.length) +
    "\n" +
    body +
    "\n" +
    readme.slice(endIdx);

  if (updated === readme) {
    console.log("No change to activity section.");
    return;
  }

  writeFileSync(README_PATH, updated, "utf8");
  console.log("Updated activity section:\n" + body);
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
