"""Shared pytest fixtures for all tests."""
import pytest
import os
import tempfile
from unittest.mock import Mock, MagicMock


@pytest.fixture
def mock_api_key():
    """Return a mock API key."""
    return "test_api_key_12345"


@pytest.fixture
def mock_account_id():
    """Return a mock account ID."""
    return "test_account_abc123"


@pytest.fixture
def temp_db_path():
    """Create a temporary database file path."""
    fd, path = tempfile.mkstemp(suffix='.db')
    os.close(fd)
    yield path
    # Cleanup
    if os.path.exists(path):
        os.unlink(path)


@pytest.fixture
def mock_harness_api():
    """Create a mock HarnessAPI instance."""
    api = Mock()

    # Mock auth config
    api.get_auth_config.return_value = {
        "authenticationMechanism": "SAML",
        "twoFactorEnabled": True,
        "passwordStrengthPolicy": "STRONG"
    }

    # Mock users
    api.get_users.return_value = [
        {"email": "user1@example.com", "twoFactorAuthenticationEnabled": True, "disabled": False},
        {"email": "user2@example.com", "twoFactorAuthenticationEnabled": False, "disabled": False}
    ]

    # Mock user groups
    api.get_user_groups.return_value = [
        {"identifier": "group1", "name": "Developers"}
    ]

    # Mock API keys
    api.get_api_keys.return_value = []

    # Mock roles
    api.get_roles.return_value = [
        {"identifier": "role1", "name": "Admin"}
    ]

    # Mock resource groups
    api.get_resource_groups.return_value = [
        {"identifier": "rg1", "name": "All Resources"}
    ]

    # Mock delegates
    api.get_delegates.return_value = [
        {
            "identifier": "delegate1",
            "hostName": "delegate-host-1",
            "delegateType": "KUBERNETES",
            "status": "ENABLED",
            "lastHeartBeat": 1234567890000
        }
    ]

    # Mock secret managers
    api.get_secret_managers.return_value = [
        {"identifier": "sm1", "type": "HashiCorpVault"}
    ]

    # Mock templates
    api.get_templates.return_value = []

    # Mock governance policies
    api.get_governance_policies.return_value = []

    # Mock notification rules
    api.get_notification_rules.return_value = []

    # Mock freeze windows
    api.get_freeze_windows.return_value = []

    # Mock connectors
    api.get_connectors.return_value = [
        {"identifier": "conn1", "type": "K8sCluster", "orgIdentifier": "org1"}
    ]

    # Mock secrets
    api.get_secrets.return_value = [
        {"identifier": "secret1", "type": "SecretText"}
    ]

    # Mock tokens
    api.get_tokens.return_value = []

    # Mock workspaces
    api.get_workspaces.return_value = []

    # Mock organizations
    api.get_organizations.return_value = [
        {"identifier": "org1", "name": "Test Org"}
    ]

    # Mock projects
    api.get_projects.return_value = [
        {"identifier": "proj1", "name": "Test Project", "orgIdentifier": "org1"}
    ]

    # Mock pipelines
    api.get_pipelines.return_value = [
        {"identifier": "pipe1", "name": "Test Pipeline"}
    ]

    # Mock environments
    api.get_environments.return_value = [
        {"identifier": "env1", "name": "production", "type": "Production"}
    ]

    # Mock services
    api.get_services.return_value = [
        {"identifier": "svc1", "name": "Test Service"}
    ]

    # Mock role assignments
    api.get_role_assignments_for_scope.return_value = [
        {
            "roleIdentifier": "role1",
            "principal": {"type": "USER", "identifier": "user1"}
        }
    ]

    return api


@pytest.fixture
def sample_check_results():
    """Return sample check results."""
    return [
        {
            "id": "1.1",
            "level": 3,
            "description": "SSO should be enabled",
            "result": "PASS",
            "details": "SSO is configured with SAML"
        },
        {
            "id": "1.2",
            "level": 3,
            "description": "2FA should be enforced",
            "result": "FAIL",
            "details": "1 users without 2FA"
        },
        {
            "id": "2.1",
            "level": 2,
            "description": "No direct user role assignments",
            "result": "PASS",
            "details": "All users assigned via groups"
        }
    ]


@pytest.fixture
def sample_compliance():
    """Return sample compliance metrics."""
    return {
        "total_checks": 3,
        "passed_checks": 2,
        "failed_checks": 1,
        "total_points": 8,
        "passed_points": 5,
        "percentage": 62.5
    }
