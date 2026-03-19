"""Unit tests for harness_platform_optimized.py"""
import pytest
from unittest.mock import Mock
from harness_platform_optimized import (
    check_sso_cached,
    check_2fa_cached,
    check_direct_user_role_assignments_cached,
    check_external_secret_manager_cached,
    check_delegate_health_cached,
    run_all_checks_optimized
)


@pytest.mark.unit
class TestOptimizedChecks:
    """Test suite for optimized check functions."""

    def test_check_sso_cached_pass(self):
        """Test SSO check passes with SAML."""
        auth_config = {"authenticationMechanism": "SAML"}
        result = check_sso_cached(auth_config)

        assert result['id'] == '1.1'
        assert result['result'] == 'PASS'
        assert result['level'] == 3
        assert 'SAML' in result['details']

    def test_check_sso_cached_fail(self):
        """Test SSO check fails with USER_PASSWORD."""
        auth_config = {"authenticationMechanism": "USER_PASSWORD"}
        result = check_sso_cached(auth_config)

        assert result['id'] == '1.1'
        assert result['result'] == 'FAIL'
        assert 'USER_PASSWORD' in result['details']

    def test_check_sso_cached_error_handling(self):
        """Test SSO check handles missing data."""
        auth_config = {}
        result = check_sso_cached(auth_config)

        assert result['id'] == '1.1'
        assert result['result'] in ['FAIL', 'ERROR']

    def test_check_2fa_cached_pass(self):
        """Test 2FA check passes when all users have 2FA."""
        users = [
            {"email": "user1@example.com", "twoFactorAuthenticationEnabled": True, "disabled": False},
            {"email": "user2@example.com", "twoFactorAuthenticationEnabled": True, "disabled": False}
        ]
        result = check_2fa_cached(users)

        assert result['id'] == '1.2'
        assert result['result'] == 'PASS'
        assert 'All 2 users' in result['details']

    def test_check_2fa_cached_fail(self):
        """Test 2FA check fails when users lack 2FA."""
        users = [
            {"email": "user1@example.com", "twoFactorAuthenticationEnabled": True, "disabled": False},
            {"email": "user2@example.com", "twoFactorAuthenticationEnabled": False, "disabled": False},
            {"email": "user3@example.com", "twoFactorAuthenticationEnabled": False, "disabled": False}
        ]
        result = check_2fa_cached(users)

        assert result['id'] == '1.2'
        assert result['result'] == 'FAIL'
        assert '2 users without 2FA' in result['details']

    def test_check_2fa_cached_ignores_disabled_users(self):
        """Test 2FA check ignores disabled users."""
        users = [
            {"email": "user1@example.com", "twoFactorAuthenticationEnabled": True, "disabled": False},
            {"email": "disabled@example.com", "twoFactorAuthenticationEnabled": False, "disabled": True}
        ]
        result = check_2fa_cached(users)

        assert result['result'] == 'PASS'

    def test_check_direct_user_role_assignments_cached_pass(self):
        """Test direct role assignment check passes when all via groups."""
        role_assignments = [
            {"principal": {"type": "USER_GROUP", "identifier": "group1"}},
            {"principal": {"type": "SERVICE_ACCOUNT", "identifier": "sa1"}}
        ]
        result = check_direct_user_role_assignments_cached(role_assignments)

        assert result['id'] == '2.1'
        assert result['result'] == 'PASS'

    def test_check_direct_user_role_assignments_cached_fail(self):
        """Test direct role assignment check fails when users assigned directly."""
        role_assignments = [
            {"principal": {"type": "USER", "identifier": "user1"}},
            {"principal": {"type": "USER", "identifier": "user2"}},
            {"principal": {"type": "USER_GROUP", "identifier": "group1"}}
        ]
        result = check_direct_user_role_assignments_cached(role_assignments)

        assert result['id'] == '2.1'
        assert result['result'] == 'FAIL'
        assert '2 direct user role assignments' in result['details']

    def test_check_external_secret_manager_cached_pass(self):
        """Test external secret manager check passes."""
        secret_managers = [
            {"identifier": "vault1", "type": "HashiCorpVault"},
            {"identifier": "aws1", "type": "AwsSecretsManager"}
        ]
        result = check_external_secret_manager_cached(secret_managers)

        assert result['id'] == '3.1'
        assert result['result'] == 'PASS'
        assert '2 external secret managers' in result['details']

    def test_check_external_secret_manager_cached_fail(self):
        """Test external secret manager check fails when none configured."""
        secret_managers = []
        result = check_external_secret_manager_cached(secret_managers)

        assert result['id'] == '3.1'
        assert result['result'] == 'FAIL'

    def test_check_delegate_health_cached_pass(self):
        """Test delegate health check passes."""
        import time
        current_time_ms = int(time.time() * 1000)
        five_min_ago = current_time_ms - (5 * 60 * 1000)

        delegates = [
            {
                "identifier": "del1",
                "hostName": "delegate-1",
                "delegateType": "KUBERNETES",
                "status": "ENABLED",
                "lastHeartBeat": five_min_ago
            }
        ]
        result = check_delegate_health_cached(delegates)

        assert result['id'] == '4.1'
        assert result['result'] == 'PASS'

    def test_check_delegate_health_cached_fail_disconnected(self):
        """Test delegate health check fails for disconnected delegates."""
        import time
        current_time_ms = int(time.time() * 1000)
        one_hour_ago = current_time_ms - (60 * 60 * 1000)

        delegates = [
            {
                "identifier": "del1",
                "hostName": "delegate-1",
                "delegateType": "KUBERNETES",
                "status": "ENABLED",
                "lastHeartBeat": one_hour_ago
            }
        ]
        result = check_delegate_health_cached(delegates)

        assert result['id'] == '4.1'
        assert result['result'] == 'FAIL'
        assert 'disconnected' in result['details'].lower()

    def test_run_all_checks_optimized(self, mock_harness_api):
        """Test running all checks with mock data collector."""
        # Create a mock data collector
        mock_collector = Mock()
        mock_collector.get.side_effect = lambda key, default=None: {
            'auth_config': {"authenticationMechanism": "SAML"},
            'users': [{"email": "user@example.com", "twoFactorAuthenticationEnabled": True, "disabled": False}],
            'user_groups': [],
            'api_keys': [],
            'roles': [],
            'resource_groups': [],
            'delegates': [],
            'secret_managers': [{"type": "HashiCorpVault"}],
            'templates': [],
            'governance_policies': [],
            'notification_rules': [],
            'freeze_windows': [],
            'connectors': [],
            'secrets': [],
            'tokens': [],
            'workspaces': [],
            'organizations': [],
            'projects': [],
            'pipelines': [],
            'environments': [],
            'services': [],
            'role_assignments': []
        }.get(key, default)

        results = run_all_checks_optimized(mock_collector)

        # Should return list of check results
        assert isinstance(results, list)
        assert len(results) > 0

        # Each result should have required fields
        for result in results:
            assert 'id' in result
            assert 'level' in result
            assert 'description' in result
            assert 'result' in result
            assert 'details' in result
            assert result['result'] in ['PASS', 'FAIL', 'ERROR', 'MANUAL']

    def test_check_results_structure(self, mock_harness_api):
        """Test that all check results have consistent structure."""
        mock_collector = Mock()
        mock_collector.get.return_value = []

        results = run_all_checks_optimized(mock_collector)

        for result in results:
            # Verify required fields
            assert isinstance(result['id'], str)
            assert isinstance(result['level'], int)
            assert result['level'] in [1, 2, 3]
            assert isinstance(result['description'], str)
            assert result['result'] in ['PASS', 'FAIL', 'ERROR', 'MANUAL']
            assert isinstance(result['details'], str)

    def test_checks_use_cached_data_not_api(self):
        """Test that checks use cached data, not making API calls."""
        # Create a mock collector that tracks get() calls
        mock_collector = Mock()
        get_calls = []

        def track_get(key, default=None):
            get_calls.append(key)
            return default if default is not None else []

        mock_collector.get.side_effect = track_get

        results = run_all_checks_optimized(mock_collector)

        # Should have called get() for various data keys
        assert len(get_calls) > 0
        assert 'users' in get_calls
        assert 'auth_config' in get_calls

        # Should NOT have any API attributes (would raise AttributeError)
        # This confirms checks are not calling api.get_*() methods
        assert not hasattr(mock_collector, 'get_users')
