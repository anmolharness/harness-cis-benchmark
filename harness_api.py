"""Harness API client with improved error handling and type hints."""
import logging
from typing import List, Dict, Any, Optional
import requests

from constants import BASE_URL, DEFAULT_TIMEOUT, DEFAULT_PAGE_SIZE

logger = logging.getLogger(__name__)


class HarnessAPIError(Exception):
    """Base exception for Harness API errors."""
    pass


class HarnessAPI:
    """Client for interacting with Harness NextGen API."""

    def __init__(self, api_key: str, account_id: str, verbose: bool = False):
        """Initialize Harness API client.

        Args:
            api_key: Harness API key
            account_id: Harness account identifier
            verbose: Enable verbose logging
        """
        self.api_key = api_key
        self.account_id = account_id
        self.verbose = verbose
        self.headers = {
            "x-api-key": self.api_key,
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

    def _log(self, message: str) -> None:
        """Log debug messages if verbose mode is enabled."""
        if self.verbose:
            logger.debug(message)

    def _get(self, url: str, timeout: int = DEFAULT_TIMEOUT) -> Dict[str, Any]:
        """Make GET request with error handling."""
        self._log(f"GET {url}")
        try:
            response = requests.get(url, headers=self.headers, timeout=timeout)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"GET request failed: {e}")
            return {}

    def _post(self, url: str, json_data: Dict[str, Any], timeout: int = DEFAULT_TIMEOUT) -> Dict[str, Any]:
        """Make POST request with error handling."""
        self._log(f"POST {url}")
        try:
            response = requests.post(url, headers=self.headers, json=json_data, timeout=timeout)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"POST request failed: {e}")
            return {}

    def _extract_content(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract content from various API response formats."""
        if "data" in data:
            if isinstance(data["data"], dict) and "content" in data["data"]:
                return data["data"]["content"]
            elif isinstance(data["data"], list):
                return data["data"]
        elif "resource" in data:
            if isinstance(data["resource"], dict) and "content" in data["resource"]:
                return data["resource"]["content"]
            elif isinstance(data["resource"], list):
                return data["resource"]
        return []

    # Authentication & Users
    def get_auth_config(self) -> Dict[str, Any]:
        """Get authentication settings."""
        url = f"{BASE_URL}/authentication-settings?accountIdentifier={self.account_id}"
        data = self._get(url)
        return data.get("resource", {})

    def get_users(self) -> List[Dict[str, Any]]:
        """Get all users in the account."""
        url = f"{BASE_URL}/users?accountIdentifier={self.account_id}&pageSize={DEFAULT_PAGE_SIZE}"
        data = self._get(url)
        return self._extract_content(data)

    def get_user_groups(self) -> List[Dict[str, Any]]:
        """Get all user groups."""
        url = f"{BASE_URL}/user-groups?accountIdentifier={self.account_id}&pageSize={DEFAULT_PAGE_SIZE}"
        data = self._get(url)
        return self._extract_content(data)

    def get_api_keys(self) -> List[Dict[str, Any]]:
        """Get API keys."""
        url = f"{BASE_URL}/api-key?accountIdentifier={self.account_id}&pageSize={DEFAULT_PAGE_SIZE}"
        data = self._get(url)
        return self._extract_content(data)

    # RBAC
    def get_role_assignments_for_scope(self, scope_query: str = "") -> List[Dict[str, Any]]:
        """Get role assignments for a specific scope."""
        url = f"https://app.harness.io/authz/api/roleassignments?accountIdentifier={self.account_id}"
        if scope_query:
            url += f"&{scope_query}"
        url += f"&pageSize={DEFAULT_PAGE_SIZE * 10}"
        data = self._get(url)
        return data.get("data", {}).get("content", [])

    def get_roles(self) -> List[Dict[str, Any]]:
        """Get custom roles."""
        url = f"{BASE_URL}/roles?accountIdentifier={self.account_id}&pageSize={DEFAULT_PAGE_SIZE}"
        data = self._get(url)
        return self._extract_content(data)

    def get_resource_groups(self) -> List[Dict[str, Any]]:
        """Get resource groups."""
        url = f"{BASE_URL}/resourcegroup?accountIdentifier={self.account_id}&pageSize={DEFAULT_PAGE_SIZE}"
        data = self._get(url)
        return self._extract_content(data)

    # Tokens & Secrets
    def get_tokens(self, org_id: Optional[str] = None, project_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get service account tokens."""
        url = f"{BASE_URL}/token/aggregate?accountIdentifier={self.account_id}"
        if org_id:
            url += f"&orgIdentifier={org_id}"
        if project_id:
            url += f"&projectIdentifier={project_id}"

        body = {"includeOnlyActiveTokens": True}
        data = self._post(url, body)
        return self._extract_content(data)

    def get_secrets(self, org_id: Optional[str] = None, project_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get secrets."""
        url = f"{BASE_URL}/v2/secrets?accountIdentifier={self.account_id}&pageSize={DEFAULT_PAGE_SIZE}"
        if org_id:
            url += f"&orgIdentifier={org_id}"
        if project_id:
            url += f"&projectIdentifier={project_id}"
        data = self._get(url)
        return self._extract_content(data)

    def get_secret_managers(self) -> List[Dict[str, Any]]:
        """Get secret managers."""
        url = f"{BASE_URL}/secret-managers/meta-data?accountIdentifier={self.account_id}"
        data = self._get(url)
        if data:
            return data.get("data", data.get("resource", []))
        # Fallback
        url = f"{BASE_URL}/connectors?accountIdentifier={self.account_id}&type=SecretManager&pageSize={DEFAULT_PAGE_SIZE}"
        data = self._get(url)
        return self._extract_content(data)

    # Connectors & Delegates
    def get_connectors(self, org_id: Optional[str] = None, project_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get connectors."""
        url = f"{BASE_URL}/connectors?accountIdentifier={self.account_id}&pageSize={DEFAULT_PAGE_SIZE}"
        if org_id:
            url += f"&orgIdentifier={org_id}"
        if project_id:
            url += f"&projectIdentifier={project_id}"

        data = self._get(url)
        return self._extract_content(data)

    def get_delegates(self) -> List[Dict[str, Any]]:
        """Get all delegates."""
        url = f"{BASE_URL}/delegate-token-ng/delegate-groups?accountId={self.account_id}"
        data = self._get(url)
        return data.get("resource", [])

    # Organizations & Projects
    def get_organizations(self) -> List[Dict[str, Any]]:
        """Get all organizations."""
        url = f"{BASE_URL}/organizations?accountIdentifier={self.account_id}&pageSize={DEFAULT_PAGE_SIZE}"
        data = self._get(url)
        return self._extract_content(data)

    def get_projects(self, org_id: str) -> List[Dict[str, Any]]:
        """Get projects in an organization."""
        url = f"{BASE_URL}/projects?accountIdentifier={self.account_id}&orgIdentifier={org_id}&pageSize={DEFAULT_PAGE_SIZE}"
        data = self._get(url)
        return self._extract_content(data)

    # Pipelines & Templates
    def get_pipelines(self, org_id: str, project_id: str) -> List[Dict[str, Any]]:
        """Get pipelines in a project."""
        url = f"{BASE_URL}/pipelines/list?accountIdentifier={self.account_id}&orgIdentifier={org_id}&projectIdentifier={project_id}&pageSize={DEFAULT_PAGE_SIZE}"
        data = self._post(url, {})
        return self._extract_content(data)

    def get_templates(self) -> List[Dict[str, Any]]:
        """Get templates."""
        url = f"{BASE_URL}/templates/list?accountIdentifier={self.account_id}&pageSize={DEFAULT_PAGE_SIZE}"
        data = self._post(url, {"filterType": "Template"})
        return self._extract_content(data)

    def get_pipeline_executions(self, org_id: str, project_id: str, pipeline_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent pipeline executions."""
        url = f"{BASE_URL}/pipelines/execution/summary?accountIdentifier={self.account_id}&orgIdentifier={org_id}&projectIdentifier={project_id}&pipelineIdentifier={pipeline_id}&page=0&size={limit}"
        data = self._post(url, {})
        return self._extract_content(data)

    # Governance & Policies
    def get_governance_policies(self) -> List[Dict[str, Any]]:
        """Get governance policies."""
        url = f"https://app.harness.io/pm/api/v1/policies/list?accountIdentifier={self.account_id}&pageSize={DEFAULT_PAGE_SIZE}"
        data = self._post(url, {"filterType": "PolicySet"})
        return self._extract_content(data)

    # Environments & Services
    def get_environments(self, org_id: str, project_id: str) -> List[Dict[str, Any]]:
        """Get environments in a project."""
        url = f"{BASE_URL}/environmentsV2?accountIdentifier={self.account_id}&orgIdentifier={org_id}&projectIdentifier={project_id}&pageSize={DEFAULT_PAGE_SIZE}"
        data = self._get(url)
        return self._extract_content(data)

    def get_services(self, org_id: str, project_id: str) -> List[Dict[str, Any]]:
        """Get services in a project."""
        url = f"{BASE_URL}/servicesV2?accountIdentifier={self.account_id}&orgIdentifier={org_id}&projectIdentifier={project_id}&pageSize={DEFAULT_PAGE_SIZE}"
        data = self._get(url)
        return self._extract_content(data)

    # IACM
    def get_workspaces(self, org_id: Optional[str] = None, project_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get IACM workspaces."""
        url = f"{BASE_URL}/iacm/workspaces?accountIdentifier={self.account_id}&pageSize={DEFAULT_PAGE_SIZE}"
        if org_id:
            url += f"&orgIdentifier={org_id}"
        if project_id:
            url += f"&projectIdentifier={project_id}"
        data = self._get(url)
        return self._extract_content(data)

    # Notifications & Monitoring
    def get_notification_rules(self) -> List[Dict[str, Any]]:
        """Get notification rules."""
        url = f"{BASE_URL}/notifications/rules?accountIdentifier={self.account_id}&pageSize={DEFAULT_PAGE_SIZE}"
        data = self._get(url)
        return self._extract_content(data)

    def get_freeze_windows(self) -> List[Dict[str, Any]]:
        """Get deployment freeze windows."""
        url = f"{BASE_URL}/freeze?accountIdentifier={self.account_id}&pageSize={DEFAULT_PAGE_SIZE}"
        data = self._get(url)
        return self._extract_content(data)
