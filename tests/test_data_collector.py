"""Unit tests for data_collector.py"""
import pytest
from unittest.mock import Mock, patch
from data_collector import HarnessDataCollector


@pytest.mark.unit
class TestHarnessDataCollector:
    """Test suite for HarnessDataCollector class."""

    def test_initialization(self, mock_api_key, mock_account_id):
        """Test collector initialization."""
        collector = HarnessDataCollector(mock_api_key, mock_account_id)
        assert collector.account_id == mock_account_id
        assert collector.data == {}
        assert collector.fetch_time == 0

    @patch('data_collector.HarnessAPI')
    def test_collect_all_account_data(self, mock_api_class, mock_api_key, mock_account_id, mock_harness_api):
        """Test that collect_all fetches all account-level data."""
        mock_api_class.return_value = mock_harness_api

        collector = HarnessDataCollector(mock_api_key, mock_account_id)
        data = collector.collect_all()

        # Verify all account-level endpoints were called
        mock_harness_api.get_auth_config.assert_called_once()
        mock_harness_api.get_users.assert_called_once()
        mock_harness_api.get_user_groups.assert_called_once()
        mock_harness_api.get_api_keys.assert_called_once()
        mock_harness_api.get_roles.assert_called_once()
        mock_harness_api.get_delegates.assert_called_once()
        mock_harness_api.get_connectors.assert_called_once()
        mock_harness_api.get_secrets.assert_called_once()

        # Verify data is cached
        assert 'auth_config' in data
        assert 'users' in data
        assert 'connectors' in data
        assert data['users'] == mock_harness_api.get_users.return_value

    @patch('data_collector.HarnessAPI')
    def test_collect_handles_api_errors(self, mock_api_class, mock_api_key, mock_account_id):
        """Test that collector handles API errors gracefully."""
        mock_api = Mock()
        mock_api.get_auth_config.side_effect = Exception("API Error")
        mock_api.get_users.return_value = [{"email": "test@example.com"}]
        mock_api.get_organizations.return_value = []  # Return empty list for orgs
        mock_api.get_user_groups.return_value = []
        mock_api.get_api_keys.return_value = []
        mock_api.get_roles.return_value = []
        mock_api.get_resource_groups.return_value = []
        mock_api.get_delegates.return_value = []
        mock_api.get_secret_managers.return_value = []
        mock_api.get_templates.return_value = []
        mock_api.get_governance_policies.return_value = []
        mock_api.get_notification_rules.return_value = []
        mock_api.get_freeze_windows.return_value = []
        mock_api.get_connectors.return_value = []
        mock_api.get_secrets.return_value = []
        mock_api.get_tokens.return_value = []
        mock_api.get_workspaces.return_value = []
        mock_api.get_role_assignments_for_scope.return_value = []
        mock_api_class.return_value = mock_api

        collector = HarnessDataCollector(mock_api_key, mock_account_id)
        data = collector.collect_all()

        # Should return empty dict/list for failed calls
        assert data['auth_config'] == {}
        # Should still fetch successful calls
        assert len(data['users']) == 1

    @patch('data_collector.HarnessAPI')
    def test_get_cached_data(self, mock_api_class, mock_api_key, mock_account_id, mock_harness_api):
        """Test getting cached data."""
        mock_api_class.return_value = mock_harness_api

        collector = HarnessDataCollector(mock_api_key, mock_account_id)
        collector.collect_all()

        # Get cached data
        users = collector.get('users')
        assert users == mock_harness_api.get_users.return_value

        # Get non-existent key with default
        missing = collector.get('nonexistent', [])
        assert missing == []

    @patch('data_collector.HarnessAPI')
    def test_fetch_time_recorded(self, mock_api_class, mock_api_key, mock_account_id, mock_harness_api):
        """Test that fetch time is recorded."""
        mock_api_class.return_value = mock_harness_api

        collector = HarnessDataCollector(mock_api_key, mock_account_id)
        collector.collect_all()

        assert collector.fetch_time > 0

    @patch('data_collector.HarnessAPI')
    def test_get_stats(self, mock_api_class, mock_api_key, mock_account_id, mock_harness_api):
        """Test statistics collection."""
        mock_api_class.return_value = mock_harness_api

        collector = HarnessDataCollector(mock_api_key, mock_account_id)
        collector.collect_all()

        stats = collector.get_stats()

        assert 'fetch_time' in stats
        assert 'total_items' in stats
        assert 'endpoints_called' in stats
        assert 'users' in stats
        assert 'connectors' in stats
        assert stats['users'] == len(mock_harness_api.get_users.return_value)

    @patch('data_collector.HarnessAPI')
    def test_org_and_project_sampling(self, mock_api_class, mock_api_key, mock_account_id, mock_harness_api):
        """Test that org and project data is sampled (not all fetched)."""
        # Setup multiple orgs
        mock_harness_api.get_organizations.return_value = [
            {"identifier": f"org{i}", "name": f"Org {i}"} for i in range(10)
        ]
        mock_harness_api.get_projects.return_value = [
            {"identifier": f"proj{i}", "name": f"Project {i}"} for i in range(5)
        ]
        mock_api_class.return_value = mock_harness_api

        collector = HarnessDataCollector(mock_api_key, mock_account_id)
        collector.collect_all()

        # Should only sample top 3 orgs (as per implementation)
        assert mock_harness_api.get_projects.call_count <= 3
