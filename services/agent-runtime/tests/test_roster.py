from founderos_agents.agents import ROLE_SPECS, role_catalog


def test_initial_nucleus_has_exactly_five_roles() -> None:
    assert [role.id for role in ROLE_SPECS] == [
        "governor",
        "systems_architect",
        "dawn_operator",
        "capability_builder",
        "verifier",
    ]


def test_builder_can_write_but_verifier_cannot() -> None:
    roles = {role["id"]: role for role in role_catalog()}
    assert roles["capability_builder"]["can_write_workspace"] is True
    assert roles["capability_builder"]["can_run_checks"] is True
    assert roles["verifier"]["can_write_workspace"] is False
    assert roles["verifier"]["can_run_checks"] is True
