from __future__ import annotations

import base64
import re
from typing import Any

import httpx


GITHUB_API = "https://api.github.com"
_FULL_NAME = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")

CATEGORY_KEYWORDS: dict[str, tuple[str, ...]] = {
    "orchestration": ("agent", "orchestrat", "workflow", "mcp", "automation"),
    "memory": ("memory", "graph", "qdrant", "obsidian", "vector", "database", "db"),
    "creative": ("image", "video", "audio", "voice", "design", "comfy", "flux", "poster", "studio"),
    "marketing": ("marketing", "social", "post", "content", "instagram", "youtube"),
    "engineering": ("code", "build", "developer", "web", "api", "cloud", "deploy"),
    "business-ops": ("crm", "commerce", "finance", "cfo", "sales", "ops", "staff", "odoo"),
    "models": ("llm", "model", "mlx", "llama", "kimi", "inference"),
    "research": ("research", "intel", "crawl", "search", "monitor"),
}


def validate_full_name(full_name: str) -> str:
    value = full_name.strip()
    if not _FULL_NAME.fullmatch(value):
        raise ValueError("GitHub repository must be owner/name using safe GitHub characters")
    return value


def classify_repository(repo: dict[str, Any]) -> list[str]:
    haystack = " ".join(
        str(repo.get(key) or "")
        for key in ("name", "description", "language")
    ).lower()
    topics = repo.get("topics") or []
    if isinstance(topics, list):
        haystack += " " + " ".join(str(topic) for topic in topics).lower()
    categories = [
        category
        for category, keywords in CATEGORY_KEYWORDS.items()
        if any(keyword in haystack for keyword in keywords)
    ]
    return categories or ["uncategorised"]


def repo_record(repo: dict[str, Any], relation: str) -> dict[str, Any]:
    return {
        "relation": relation,
        "full_name": repo.get("full_name"),
        "name": repo.get("name"),
        "private": bool(repo.get("private", False)),
        "fork": bool(repo.get("fork", False)),
        "archived": bool(repo.get("archived", False)),
        "description": repo.get("description"),
        "language": repo.get("language"),
        "topics": repo.get("topics") or [],
        "stargazers_count": int(repo.get("stargazers_count") or 0),
        "forks_count": int(repo.get("forks_count") or 0),
        "size": int(repo.get("size") or 0),
        "updated_at": repo.get("updated_at"),
        "html_url": repo.get("html_url"),
        "categories": classify_repository(repo),
    }


def _headers(token: str | None, *, raw: bool = False) -> dict[str, str]:
    headers = {
        "Accept": "application/vnd.github.raw+json" if raw else "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "founderos-dawn-portfolio-auditor",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


def _get_json(url: str, token: str | None, timeout: float, params: dict[str, Any] | None = None) -> Any:
    with httpx.Client(timeout=timeout, follow_redirects=False) as client:
        response = client.get(url, headers=_headers(token), params=params)
    response.raise_for_status()
    return response.json()


def _paginate(url: str, token: str | None, timeout: float, max_pages: int) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    for page in range(1, max(1, min(max_pages, 20)) + 1):
        batch = _get_json(url, token, timeout, {"per_page": 100, "page": page})
        if not isinstance(batch, list):
            break
        items.extend(item for item in batch if isinstance(item, dict))
        if len(batch) < 100:
            break
    return items


def portfolio_snapshot(owner: str, token: str | None, timeout: float, max_pages: int = 10) -> dict[str, Any]:
    owner = owner.strip()
    if not owner or not re.fullmatch(r"[A-Za-z0-9-]+", owner):
        raise ValueError("invalid GitHub owner")

    owned_url = f"{GITHUB_API}/user/repos" if token else f"{GITHUB_API}/users/{owner}/repos"
    owned = _paginate(owned_url, token, timeout, max_pages)
    if token:
        owned = [repo for repo in owned if (repo.get("owner") or {}).get("login", "").lower() == owner.lower()]
    starred = _paginate(f"{GITHUB_API}/users/{owner}/starred", token, timeout, max_pages)

    owned_records = [repo_record(repo, "owned") for repo in owned]
    starred_records = [repo_record(repo, "starred") for repo in starred]
    return {
        "owner": owner,
        "owned_scope": "private+public" if token else "public-only",
        "owned_count": len(owned_records),
        "starred_count": len(starred_records),
        "owned": owned_records,
        "starred": starred_records,
        "interpretation_rule": (
            "This is inventory evidence, not an adoption decision. Inspect README/source/license and compare against DAWN "
            "capabilities before recommending ADOPT, INTEGRATE, REPLACE, REFERENCE or IGNORE."
        ),
    }


def inspect_repository(full_name: str, token: str | None, timeout: float) -> dict[str, Any]:
    safe_name = validate_full_name(full_name)
    repo = _get_json(f"{GITHUB_API}/repos/{safe_name}", token, timeout)
    readme_text: str | None = None
    readme_error: str | None = None
    try:
        readme = _get_json(f"{GITHUB_API}/repos/{safe_name}/readme", token, timeout)
        if isinstance(readme, dict) and readme.get("content"):
            readme_text = base64.b64decode(readme["content"]).decode("utf-8", errors="replace")[:50_000]
    except Exception as exc:
        readme_error = str(exc)

    return {
        "repository": repo_record(repo, "inspection"),
        "license": (repo.get("license") or {}).get("spdx_id") if isinstance(repo, dict) else None,
        "default_branch": repo.get("default_branch") if isinstance(repo, dict) else None,
        "homepage": repo.get("homepage") if isinstance(repo, dict) else None,
        "readme": readme_text,
        "readme_error": readme_error,
    }
