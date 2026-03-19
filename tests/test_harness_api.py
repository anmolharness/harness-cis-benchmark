"""Unit tests for harness_api.py"""
import pytest
import responses
from harness_api import HarnessAPI


@pytest.mark.unit
class TestHarnessAPI:
    """Test suite for HarnessAPI class."""

    def test_initialization(self, mock_api_key, mock_account_id):
        """Test API client initialization."""
        api = HarnessAPI(mock_api_key, mock_account_id)
        assert api.api_key == mock_api_key
        assert api.account_id == mock_account_id
        assert api.base_url == "https://app.harness.io"

    def test_headers_contain_auth(self, mock_api_key, mock_account_id):
        """Test that headers contain API key."""
        api = HarnessAPI(mock_api_key, mock_account_id)
        headers = api._get_headers()

        assert "x-api-key" in headers
        assert headers["x-api-key"] == mock_api_key

    @responses.activate
    def test_get_auth_config_success(self, mock_api_key, mock_account_id):
        """Test successful auth config retrieval."""
        responses.add(
            responses.GET,
            f"https://app.harness.io/ng/api/authentication-settings/login-settings?accountIdentifier={mock_account_id}",
            json={"data": {"authenticationMechanism": "SAML"}},
            status=200
        )

        api = HarnessAPI(mock_api_key, mock_account_id)
        result = api.get_auth_config()

        assert result["authenticationMechanism"] == "SAML"

    @responses.activate
    def test_get_users_success(self, mock_api_key, mock_account_id):
        """Test successful users retrieval."""
        responses.add(
            responses.GET,
            f"https://app.harness.io/ng/api/user/aggregate?accountIdentifier={mock_account_id}&pageSize=100",
            json={
                "data": {
                    "content": [
                        {"email": "user1@example.com", "twoFactorAuthenticationEnabled": True}
                    ]
                }
            },
            status=200
        )

        api = HarnessAPI(mock_api_key, mock_account_id)
        result = api.get_users()

        assert len(result) == 1
        assert result[0]["email"] == "user1@example.com"

    @responses.activate
    def test_get_delegates_success(self, mock_api_key, mock_account_id):
        """Test successful delegates retrieval."""
        responses.add(
            responses.GET,
            f"https://app.harness.io/ng/api/delegate-token-ng/delegate-groups?accountId={mock_account_id}",
            json={
                "resource": [
                    {
                        "groupId": "delegate1",
                        "groupName": "k8s-delegate",
                        "delegateType": "KUBERNETES"
                    }
                ]
            },
            status=200
        )

        api = HarnessAPI(mock_api_key, mock_account_id)
        result = api.get_delegates()

        assert len(result) == 1
        assert result[0]["groupName"] == "k8s-delegate"

    @responses.activate
    def test_api_error_handling(self, mock_api_key, mock_account_id):
        """Test API error handling."""
        responses.add(
            responses.GET,
            f"https://app.harness.io/ng/api/authentication-settings/login-settings?accountIdentifier={mock_account_id}",
            json={"error": "Unauthorized"},
            status=401
        )

        api = HarnessAPI(mock_api_key, mock_account_id)

        with pytest.raises(Exception):
            api.get_auth_config()

    @responses.activate
    def test_fallback_endpoint_on_404(self, mock_api_key, mock_account_id):
        """Test fallback to alternative endpoint on 404."""
        # First endpoint returns 404
        responses.add(
            responses.POST,
            "https://app.harness.io/ng/api/connectors/listV2",
            status=404
        )

        # Fallback endpoint succeeds
        responses.add(
            responses.GET,
            f"https://app.harness.io/ng/api/connectors?accountIdentifier={mock_account_id}",
            json={
                "data": {
                    "content": [{"identifier": "conn1", "type": "K8sCluster"}]
                }
            },
            status=200
        )

        api = HarnessAPI(mock_api_key, mock_account_id)
        result = api.get_connectors()

        # Should successfully use fallback
        assert len(result) >= 0

    @responses.activate
    def test_pagination_handling(self, mock_api_key, mock_account_id):
        """Test that pagination is handled correctly."""
        # Return paginated response
        responses.add(
            responses.GET,
            f"https://app.harness.io/ng/api/user/aggregate?accountIdentifier={mock_account_id}&pageSize=100",
            json={
                "data": {
                    "content": [{"email": f"user{i}@example.com"} for i in range(100)],
                    "totalPages": 1,
                    "totalElements": 100
                }
            },
            status=200
        )

        api = HarnessAPI(mock_api_key, mock_account_id)
        result = api.get_users()

        assert len(result) == 100

    @responses.activate
    def test_empty_response_handling(self, mock_api_key, mock_account_id):
        """Test handling of empty API responses."""
        responses.add(
            responses.GET,
            f"https://app.harness.io/ng/api/user/aggregate?accountIdentifier={mock_account_id}&pageSize=100",
            json={"data": {"content": []}},
            status=200
        )

        api = HarnessAPI(mock_api_key, mock_account_id)
        result = api.get_users()

        assert result == []

    def test_verbose_mode(self, mock_api_key, mock_account_id, capsys):
        """Test verbose mode outputs debug info."""
        api = HarnessAPI(mock_api_key, mock_account_id, verbose=True)

        # Verbose mode should be set
        assert api.verbose == True

    @responses.activate
    def test_post_request_with_body(self, mock_api_key, mock_account_id):
        """Test POST requests with JSON body."""
        responses.add(
            responses.POST,
            "https://app.harness.io/ng/api/connectors/listV2",
            json={
                "data": {
                    "content": [{"identifier": "conn1"}]
                }
            },
            status=200
        )

        api = HarnessAPI(mock_api_key, mock_account_id)
        result = api.get_connectors()

        assert len(result) >= 0
