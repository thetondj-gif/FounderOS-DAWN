from founderos_agents.brief import MASTER_BUILD_BRIEF, bootstrap_task, mission_prompt, portfolio_audit_task
from founderos_agents.capabilities import capability_catalog, get_capability


def test_master_brief_contains_architecture_permissions_and_completion_gates() -> None:
    assert "FounderOS" in MASTER_BUILD_BRIEF
    assert "Microsoft Agent Framework" in MASTER_BUILD_BRIEF
    assert "DAWN OS" in MASTER_BUILD_BRIEF
    assert "GitHub estate assimilation" in MASTER_BUILD_BRIEF
    assert "ADOPT_AS_SERVICE" in MASTER_BUILD_BRIEF
    assert "Tier 0" in MASTER_BUILD_BRIEF
    assert "Tier 5" in MASTER_BUILD_BRIEF
    assert "Completion criteria" in MASTER_BUILD_BRIEF
    assert "DISCOVER -> DESIGN -> BUILD IN ISOLATION -> TEST -> INDEPENDENT VERIFY" in MASTER_BUILD_BRIEF


def test_mission_prompt_always_injects_master_brief() -> None:
    prompt = mission_prompt("Inspect the stack")
    assert prompt.startswith("# DAWN / FounderOS Master Build Brief")
    assert "## Current mission\nInspect the stack" in prompt
    assert bootstrap_task()
    assert "owned repository" in portfolio_audit_task()
    assert "starred repository" in portfolio_audit_task()


def test_capability_catalog_contains_core_stack_and_permission_metadata() -> None:
    ids = {item["id"] for item in capability_catalog()}
    required = {
        "founderos-api",
        "microsoft-agent-framework",
        "github",
        "github-portfolio",
        "ollama",
        "hermes",
        "n8n",
        "composio",
        "gmail",
        "google-calendar",
        "google-drive",
        "postiz",
        "firecrawl",
        "playwright",
        "qdrant",
        "graphiti",
        "obsidian",
        "langfuse",
        "comfyui",
        "mcp",
        "capability-foundry",
        "proof-ledger",
    }
    assert required <= ids
    assert all(0 <= int(item["permission_tier"]) <= 5 for item in capability_catalog())


def test_catalog_does_not_equate_known_with_live() -> None:
    github = get_capability("github")
    github_portfolio = get_capability("github-portfolio")
    ollama = get_capability("ollama")
    assert github is not None and github["availability"] == "requires-adapter"
    assert github_portfolio is not None and github_portfolio["availability"] == "available"
    assert int(github_portfolio["permission_tier"]) == 1
    assert ollama is not None and ollama["availability"] == "available"
    assert get_capability("does-not-exist") is None


def test_capability_search_is_bounded_and_relevant() -> None:
    results = capability_catalog("memory", max_results=2)
    assert 1 <= len(results) <= 2
    assert all("memory" in " ".join(map(str, item.values())).lower() for item in results)
