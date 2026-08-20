from dawn_google_agents.agents import build_google_swarm, google_role_catalog


def test_google_role_catalog_is_bounded_and_launch_focused() -> None:
    roles = google_role_catalog()
    assert {role["id"] for role in roles} == {
        "google_research_analyst",
        "google_web_product_builder",
        "google_commercial_strategist",
        "google_workspace_operator",
        "google_multimodal_reviewer",
        "google_code_reviewer",
    }
    assert all(0 <= int(role["max_permission_tier"]) <= 2 for role in roles)


def test_google_swarm_constructs_without_provider_call() -> None:
    swarm = build_google_swarm()
    assert swarm.name == "GoogleLaunchSwarm"
    assert [agent.name for agent in swarm.sub_agents] == [
        "GoogleResearchAnalyst",
        "GoogleWebProductBuilder",
        "GoogleCommercialStrategist",
        "GoogleWorkspaceOperator",
        "GoogleMultimodalReviewer",
        "GoogleCodeReviewer",
    ]
    assert all(agent.parent_agent is swarm for agent in swarm.sub_agents)
