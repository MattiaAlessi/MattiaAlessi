#!/usr/bin/env python3
"""Render the live GitHub star counts of the featured repositories into README.md.

The rows of the "$ find ~/projects -type f -name \"featured*\"" block live in
.github/featured-repos.md and may contain placeholders such as:

    {{ index .github.repositories "phantom-keylogger" "stars" }}

Every placeholder is replaced by the current number of stars of that repository
(GitHub API) and the rendered rows are written into README.md, between the
featured:start / featured:end markers, wrapped in the same <pre><code> block.

Environment variables:
    FEATURED_SOURCE  rows to render          (default .github/featured-repos.md)
    README_FILE      README to rewrite       (default README.md)
    REPO_OWNER       owner of the repos      (default $GITHUB_REPOSITORY_OWNER)
    GITHUB_TOKEN     optional API token      (falls back to the public API)
"""

from __future__ import annotations

import json
import os
import re
import sys
import urllib.error
import urllib.request

SOURCE = os.environ.get("FEATURED_SOURCE", ".github/featured-repos.md")
README = os.environ.get("README_FILE", "README.md")
OWNER = os.environ.get("REPO_OWNER") or os.environ.get("GITHUB_REPOSITORY_OWNER") or ""
TOKEN = (os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN") or "").strip()

PLACEHOLDER = re.compile(
    r"\{\{\s*index\s+\.github\.repositories\s+\"([^\"]+)\"\s+\"stars\"\s*\}\}"
)
COMMENT = re.compile(r"<!--.*?-->", re.DOTALL)
START_MARKER = "<!-- featured:start -->"
END_MARKER = "<!-- featured:end -->"
API_URL = "https://api.github.com/repos/{owner}/{repo}"


def read_text(path: str) -> tuple[str, str]:
    """Return the file content (LF normalised) and the newline style it uses."""
    with open(path, "rb") as handle:
        raw = handle.read()
    text = raw.decode("utf-8")
    newline = "\r\n" if "\r\n" in text else "\n"
    return text.replace("\r\n", "\n"), newline


def write_text(path: str, text: str, newline: str) -> None:
    with open(path, "wb") as handle:
        handle.write(text.replace("\n", newline).encode("utf-8"))


def fetch_stars(repo: str) -> str | None:
    """Return the current star count of a repository, or None if it is unreachable."""
    url = API_URL.format(owner=OWNER, repo=repo)
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "readme-stars-updater",
    }
    attempts = []
    if TOKEN:
        attempts.append({**headers, "Authorization": f"Bearer {TOKEN}"})
    # The workflow token is scoped to this repository: the public API is used as
    # a fallback for the other (public) repositories of the owner.
    attempts.append(headers)

    last_error: Exception | None = None
    for attempt in attempts:
        try:
            request = urllib.request.Request(url, headers=attempt)
            with urllib.request.urlopen(request, timeout=30) as response:
                payload = json.load(response)
            return str(payload["stargazers_count"])
        except urllib.error.HTTPError as error:
            last_error = error
        except Exception as error:  # timeout, DNS failure, malformed payload...
            last_error = error
    print(
        f"warning: cannot read the star count of {OWNER}/{repo}: {last_error}",
        file=sys.stderr,
    )
    return None


def render_rows(source_text: str) -> tuple[str, dict[str, str]]:
    """Replace every star placeholder of the source rows with the live count."""
    rows = [line.rstrip() for line in COMMENT.sub("", source_text).split("\n")]
    rows = [line for line in rows if line.strip()]

    values: dict[str, str] = {}
    for repo in dict.fromkeys(PLACEHOLDER.findall("\n".join(rows))):
        stars = fetch_stars(repo)
        values[repo] = stars if stars is not None else "n/a"

    # Same width for every counter, so the columns stay aligned.
    width = max((len(value) for value in values.values()), default=1)
    rendered = PLACEHOLDER.sub(lambda match: values[match.group(1)].rjust(width), "\n".join(rows))
    return rendered, values


def main() -> int:
    if not OWNER:
        print("error: REPO_OWNER is not set", file=sys.stderr)
        return 1

    source_text, _ = read_text(SOURCE)
    rendered, values = render_rows(source_text)

    readme_text, newline = read_text(README)
    if START_MARKER not in readme_text or END_MARKER not in readme_text:
        print(
            f"error: {START_MARKER} / {END_MARKER} not found in {README}",
            file=sys.stderr,
        )
        return 1

    head, rest = readme_text.split(START_MARKER, 1)
    _, tail = rest.split(END_MARKER, 1)
    block = f"{START_MARKER}\n<pre><code>\n{rendered}\n</code></pre>\n{END_MARKER}"
    updated = head + block + tail

    if updated == readme_text:
        print(f"{README} is already up to date")
        return 0

    write_text(README, updated, newline)
    summary = ", ".join(f"{repo}={value}" for repo, value in values.items())
    print(f"updated {README} ({summary})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
