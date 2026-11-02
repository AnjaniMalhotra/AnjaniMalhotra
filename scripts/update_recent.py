"""Refresh the "Recently shipped" list in README.md from public GitHub data."""
import datetime
import json
import os
import pathlib
import re
import urllib.request

USER = "AnjaniMalhotra"
LIMIT = 5

# Only these repos can appear in the list. Add a repo here when it's ready to show.
SHOWCASE = {
    "legal-docs-review",
    "Hospital-insurance-FDE",
    "FDE-northstar-legacy-system",
    "JEV-Business-Leads-Inbox",
    "news-digest-bot",
}

README = pathlib.Path(__file__).resolve().parent.parent / "README.md"
BLOCK = re.compile(r"(<!-- RECENT:START -->\n).*?(<!-- RECENT:END -->)", re.DOTALL)


def fetch_repos():
    url = f"https://api.github.com/users/{USER}/repos?per_page=100&sort=pushed"
    headers = {"Accept": "application/vnd.github+json"}
    if token := os.environ.get("GITHUB_TOKEN"):
        headers["Authorization"] = f"Bearer {token}"
    with urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=30) as response:
        return json.load(response)


def format_line(repo):
    pushed = datetime.datetime.strptime(repo["pushed_at"], "%Y-%m-%dT%H:%M:%SZ")
    return f"- **{pushed.day} {pushed:%b %Y}** · [{repo['name']}]({repo['html_url']})"


def main():
    repos = [repo for repo in fetch_repos() if repo["name"] in SHOWCASE]
    if not repos:
        raise SystemExit("No showcase repos found, so README.md was left unchanged.")
    repos.sort(key=lambda repo: repo["pushed_at"], reverse=True)
    lines = "\n".join(format_line(repo) for repo in repos[:LIMIT])

    text = README.read_text(encoding="utf-8")
    if not BLOCK.search(text):
        raise SystemExit("RECENT markers are missing from README.md.")
    README.write_text(BLOCK.sub(lambda m: f"{m[1]}{lines}\n{m[2]}", text), encoding="utf-8")


if __name__ == "__main__":
    main()
