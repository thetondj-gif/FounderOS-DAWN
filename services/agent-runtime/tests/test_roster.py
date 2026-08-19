from founderos_agents.agents import ROLE_SPECS, role_catalog


def test_bootstrap_nucleus_has_portfolio_architect_and_governance_roles() -> None:
    assert [role.id for role in ROLE_SPECS] == [
        "governor",
        "portfolio_architect",
        "systems_architect",
        "dawn_operator",
        "capability_builder",
        "verifier",
    ]


def test_builder_can_write_but_verifier_and_portfolio_architect_cannot() -> None:
    roles = {role["id"]: role for role in role_catalog()}
    assert roles["capability_builder"]["can_write_workspace"] is True
    assert roles["capability_builder"]["can_run_checks"] is True
    assert roles["portfolio_architect"]["can_write_workspace"] is False
    assert roles["verifier"]["can_write_workspace"] is False
    assert roles["verifier"]["can_run_checks"] is True
