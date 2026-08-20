from pathlib import Path

from founderos_agents.agents import build_agents
from founderos_agents.config import Settings
from founderos_agents.workflow import build_founder_workflow


def _settings(tmp_path: Path) -> Settings:
    return Settings(
        repo_root=tmp_path,
        workspace_root=tmp_path / ".agent-workspace",
        ollama_host="http://127.0.0.1:11434",
        ollama_model="test-model",
        founder_os_base_url="http://127.0.0.1:4100",
        request_timeout_seconds=0.1,
        max_file_bytes=10_000,
    )


def test_real_agent_framework_objects_construct_without_network(tmp_path: Path) -> None:
    bundle = build_agents(_settings(tmp_path))
    assert bundle.governor.name == "FounderGovernor"
    assert [agent.name for agent in bundle.participants] == [
        "PortfolioArchitect",
        "SystemsArchitect",
        "DawnOperator",
        "CapabilityBuilder",
        "IndependentVerifier",
    ]


def test_magentic_workflow_constructs_without_network(tmp_path: Path) -> None:
    workflow = build_founder_workflow(_settings(tmp_path))
    assert workflow is not None
    assert workflow.name
