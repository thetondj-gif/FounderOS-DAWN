import pytest

from founderos_agents.portfolio import classify_repository, repo_record, validate_full_name


def test_validate_full_name_rejects_url_and_path_escape() -> None:
    assert validate_full_name("microsoft/agent-framework") == "microsoft/agent-framework"
    with pytest.raises(ValueError):
        validate_full_name("https://github.com/microsoft/agent-framework")
    with pytest.raises(ValueError):
        validate_full_name("../secret/repo")


def test_repository_classification_supports_dawn_domains() -> None:
    repo = {
        "name": "agent-memory-studio",
        "description": "Agent workflow with vector memory and image generation",
        "language": "Python",
        "topics": ["mcp"],
    }
    categories = classify_repository(repo)
    assert "orchestration" in categories
    assert "memory" in categories
    assert "creative" in categories


def test_repo_record_preserves_adoption_evidence_fields() -> None:
    record = repo_record(
        {
            "full_name": "owner/example",
            "name": "example",
            "private": False,
            "fork": True,
            "archived": False,
            "description": "workflow automation",
            "language": "Python",
            "topics": ["agents"],
            "stargazers_count": 123,
            "forks_count": 7,
            "size": 42,
            "updated_at": "2026-08-19T00:00:00Z",
            "html_url": "https://github.com/owner/example",
        },
        "starred",
    )
    assert record["relation"] == "starred"
    assert record["fork"] is True
    assert record["stargazers_count"] == 123
    assert "orchestration" in record["categories"]
