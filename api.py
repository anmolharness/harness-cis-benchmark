import requests

BASE_URL = "https://app.harness.io/ng/api"

class HarnessAPI:
    def __init__(self, api_key: str, account_id: str):
        self.api_key = api_key
        self.account_id = account_id
        self.headers = {
            "x-api-key": self.api_key,
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

    def _log(self, message: str):
        """Log debug messages if verbose mode is enabled"""
        import builtins
        if hasattr(builtins, 'VERBOSE_MODE') and builtins.VERBOSE_MODE:
            print(f"[DEBUG] {message}")

    def get_auth_config(self):
        """
        Get full authentication settings including 2FA, SSO, lockout, etc.
        """
        url = f"{BASE_URL}/authentication-settings?accountIdentifier={self.account_id}"
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            return response.json().get("resource", {})
        except requests.exceptions.RequestException as e:
            print(f"[ERROR] Failed to fetch auth config: {e}")
            return {}

    def get_account_role_assignments(self):
        url = f"https://app.harness.io/authz/api/roleassignments?accountIdentifier={self.account_id}"
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json().get("resource", {}).get("content", [])
        except requests.exceptions.RequestException as e:
            print(f"[ERROR] Failed to fetch account role assignments: {e}")
            return []

    def get_organization_role_assignments(self, org_id):
        url = f"https://app.harness.io/ng/authz/roleassignments?accountIdentifier={self.account_id}&orgIdentifier={org_id}"
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json().get("resource", {}).get("content", [])
        except requests.exceptions.RequestException as e:
            print(f"[ERROR] Failed to fetch organization role assignments: {e}")
            return []

    def get_project_role_assignments(self, org_id, project_id):
        url = f"https://app.harness.io/authz/api/roleassignments?accountIdentifier={self.account_id}&orgIdentifier={org_id}&projectIdentifier={project_id}"
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json().get("resource", {}).get("content", [])
        except requests.exceptions.RequestException as e:
            print(f"[ERROR] Failed to fetch project role assignments: {e}")
            return []

    def get_organizations(self):
        url = f"https://app.harness.io/ng/api/organizations?accountIdentifier={self.account_id}"
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json().get("resource", {}).get("content", [])
        except requests.exceptions.RequestException as e:
            print(f"[ERROR] Failed to fetch organizations: {e}")
            return []

    def get_projects(self, org_id):
        url = f"https://app.harness.io/ng/api/projects?accountIdentifier={self.account_id}&orgIdentifier={org_id}"
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json().get("resource", {}).get("content", [])
        except requests.exceptions.RequestException as e:
            print(f"[ERROR] Failed to fetch projects: {e}")
            return []
    
    def get_role_assignments_for_scope(self, scope_query: str):
        url = f"https://app.harness.io/authz/api/roleassignments?accountIdentifier={self.account_id}&{scope_query}&pageSize=1000"
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json().get("data", {}).get("content", [])
        except requests.exceptions.RequestException as e:
            print(f"[ERROR] Failed to fetch role assignments for scope [{scope_query}]: {e}")
            return []
    
    def get_tokens(self, org_id=None, project_id=None):
        url = f"{BASE_URL}/token/aggregate?accountIdentifier={self.account_id}"
        if org_id:
            url += f"&orgIdentifier={org_id}"
        if project_id:
            url += f"&projectIdentifier={project_id}"

        # Use POST with filter body
        body = {
            "includeOnlyActiveTokens": True
        }
        try:
            response = requests.post(url, headers=self.headers, json=body, timeout=10)
            response.raise_for_status()
            data = response.json().get("data", {})
            if isinstance(data, dict):
                return data.get("content", [])
            return []
        except requests.exceptions.RequestException as e:
            # Silently fail - tokens might not be accessible
            return []

    def get_secret_managers(self):
        """Get all secret managers configured at account level"""
        # Try primary endpoint
        url = f"{BASE_URL}/secret-managers/meta-data?accountIdentifier={self.account_id}"
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            data = response.json()

            # Handle different response structures
            if "data" in data:
                return data.get("data", [])
            elif "resource" in data:
                return data.get("resource", [])
            return []
        except requests.exceptions.RequestException:
            # Try alternative endpoint
            try:
                url = f"{BASE_URL}/connectors?accountIdentifier={self.account_id}&type=SecretManager&pageSize=100"
                response = requests.get(url, headers=self.headers, timeout=10)
                response.raise_for_status()
                data = response.json()
                if "data" in data and "content" in data["data"]:
                    return data["data"]["content"]
                return []
            except requests.exceptions.RequestException:
                # Silently fail
                return []

    def get_connectors(self, org_id=None, project_id=None):
        """Get connectors with optional org/project scope"""
        url = f"{BASE_URL}/connectors?accountIdentifier={self.account_id}&pageSize=100"
        if org_id:
            url += f"&orgIdentifier={org_id}"
        if project_id:
            url += f"&projectIdentifier={project_id}"

        self._log(f"Fetching connectors from {url}")
        # Try GET first (simpler)
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            data = response.json()
            self._log(f"Connectors API response: {len(str(data))} bytes")

            # Handle different response structures
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
        except requests.exceptions.RequestException:
            # Try POST as fallback
            try:
                url = f"{BASE_URL}/connectors/listV2?accountIdentifier={self.account_id}&pageSize=100"
                if org_id:
                    url += f"&orgIdentifier={org_id}"
                if project_id:
                    url += f"&projectIdentifier={project_id}"

                body = {"filterType": "Connector"}
                response = requests.post(url, headers=self.headers, json=body, timeout=10)
                response.raise_for_status()
                data = response.json()
                if "data" in data and "content" in data["data"]:
                    return data["data"]["content"]
                return []
            except requests.exceptions.RequestException:
                # Silently fail
                return []

    def get_delegates(self):
        """Get all delegates in the account"""
        url = f"{BASE_URL}/delegate-token-ng/delegate-groups?accountId={self.account_id}"
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            return response.json().get("resource", [])
        except requests.exceptions.RequestException as e:
            print(f"[ERROR] Failed to fetch delegates: {e}")
            return []

    def get_pipelines(self, org_id=None, project_id=None):
        """Get pipelines with optional org/project scope"""
        url = f"{BASE_URL}/pipelines/list?accountIdentifier={self.account_id}&pageSize=100"
        if org_id:
            url += f"&orgIdentifier={org_id}"
        if project_id:
            url += f"&projectIdentifier={project_id}"
        try:
            response = requests.post(url, headers=self.headers, json={}, timeout=10)
            response.raise_for_status()
            return response.json().get("data", {}).get("content", [])
        except requests.exceptions.RequestException as e:
            print(f"[ERROR] Failed to fetch pipelines: {e}")
            return []

    def get_templates(self):
        """Get all templates in the account"""
        # Templates list usually requires POST
        url = f"{BASE_URL}/templates/list?accountIdentifier={self.account_id}&pageSize=100"
        body = {
            "filterType": "Template"
        }
        try:
            response = requests.post(url, headers=self.headers, json=body, timeout=10)
            response.raise_for_status()
            data = response.json()

            # Handle different response structures
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
        except requests.exceptions.RequestException:
            # Try GET as fallback
            try:
                url = f"{BASE_URL}/templates?accountIdentifier={self.account_id}&pageSize=100"
                response = requests.get(url, headers=self.headers, timeout=10)
                response.raise_for_status()
                data = response.json()
                if "data" in data and "content" in data["data"]:
                    return data["data"]["content"]
                return []
            except requests.exceptions.RequestException:
                # Silently fail
                return []

    def get_governance_policies(self):
        """Get governance policies"""
        url = f"https://app.harness.io/pm/api/v1/policies/list?accountIdentifier={self.account_id}&pageSize=100"
        body = {
            "filterType": "PolicySet"
        }
        try:
            response = requests.post(url, headers=self.headers, json=body, timeout=10)
            response.raise_for_status()
            data = response.json()

            # Handle different response structures
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
        except requests.exceptions.RequestException:
            # Try NG API as fallback
            try:
                url = f"{BASE_URL}/governance/policy-set?accountIdentifier={self.account_id}&pageSize=100"
                response = requests.get(url, headers=self.headers, timeout=10)
                response.raise_for_status()
                data = response.json()
                if "data" in data and "content" in data["data"]:
                    return data["data"]["content"]
                return []
            except requests.exceptions.RequestException:
                # Silently fail
                return []

    def get_workspaces(self, org_id=None, project_id=None):
        """Get IACM workspaces"""
        url = f"{BASE_URL}/iacm/workspaces?accountIdentifier={self.account_id}&pageSize=100"
        if org_id:
            url += f"&orgIdentifier={org_id}"
        if project_id:
            url += f"&projectIdentifier={project_id}"

        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            data = response.json()
            if "data" in data and "content" in data["data"]:
                return data["data"]["content"]
            return []
        except requests.exceptions.RequestException:
            return []

    def get_notification_rules(self):
        """Get notification rules configured"""
        url = f"{BASE_URL}/notifications/rules?accountIdentifier={self.account_id}&pageSize=100"
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            data = response.json()
            if "data" in data and "content" in data["data"]:
                return data["data"]["content"]
            elif "resource" in data:
                return data["resource"] if isinstance(data["resource"], list) else []
            return []
        except requests.exceptions.RequestException:
            return []

    def get_freeze_windows(self):
        """Get deployment freeze windows"""
        url = f"{BASE_URL}/freeze?accountIdentifier={self.account_id}&pageSize=100"
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            data = response.json()
            if "data" in data and "content" in data["data"]:
                return data["data"]["content"]
            elif "resource" in data:
                return data["resource"] if isinstance(data["resource"], list) else []
            return []
        except requests.exceptions.RequestException:
            return []

    def get_services(self, org_id, project_id):
        """Get services in a project"""
        url = f"{BASE_URL}/servicesV2?accountIdentifier={self.account_id}&orgIdentifier={org_id}&projectIdentifier={project_id}&pageSize=100"
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            data = response.json()
            if "data" in data and "content" in data["data"]:
                return data["data"]["content"]
            return []
        except requests.exceptions.RequestException:
            return []

    def get_environments(self, org_id, project_id):
        """Get environments in a project"""
        url = f"{BASE_URL}/environmentsV2?accountIdentifier={self.account_id}&orgIdentifier={org_id}&projectIdentifier={project_id}&pageSize=100"
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            data = response.json()
            if "data" in data and "content" in data["data"]:
                return data["data"]["content"]
            return []
        except requests.exceptions.RequestException:
            return []

    def get_pipeline_executions(self, org_id, project_id, pipeline_id, limit=10):
        """Get recent pipeline executions"""
        url = f"{BASE_URL}/pipelines/execution/summary?accountIdentifier={self.account_id}&orgIdentifier={org_id}&projectIdentifier={project_id}&pipelineIdentifier={pipeline_id}&page=0&size={limit}"
        try:
            response = requests.post(url, headers=self.headers, json={}, timeout=10)
            response.raise_for_status()
            data = response.json()
            if "data" in data and "content" in data["data"]:
                return data["data"]["content"]
            return []
        except requests.exceptions.RequestException:
            return []

    def get_users(self):
        """Get all users in the account"""
        url = f"{BASE_URL}/users?accountIdentifier={self.account_id}&pageSize=100"
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            data = response.json()
            if "data" in data and "content" in data["data"]:
                return data["data"]["content"]
            elif "resource" in data:
                return data["resource"] if isinstance(data["resource"], list) else []
            return []
        except requests.exceptions.RequestException:
            return []

    def get_user_groups(self):
        """Get all user groups"""
        url = f"{BASE_URL}/user-groups?accountIdentifier={self.account_id}&pageSize=100"
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            data = response.json()
            if "data" in data and "content" in data["data"]:
                return data["data"]["content"]
            elif "resource" in data:
                return data["resource"] if isinstance(data["resource"], list) else []
            return []
        except requests.exceptions.RequestException:
            return []

    def get_secrets(self, org_id=None, project_id=None):
        """Get secrets"""
        url = f"{BASE_URL}/v2/secrets?accountIdentifier={self.account_id}&pageSize=100"
        if org_id:
            url += f"&orgIdentifier={org_id}"
        if project_id:
            url += f"&projectIdentifier={project_id}"
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            data = response.json()
            if "data" in data and "content" in data["data"]:
                return data["data"]["content"]
            return []
        except requests.exceptions.RequestException:
            return []

    def get_resource_groups(self):
        """Get resource groups"""
        url = f"{BASE_URL}/resourcegroup?accountIdentifier={self.account_id}&pageSize=100"
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            data = response.json()
            if "data" in data and "content" in data["data"]:
                return data["data"]["content"]
            return []
        except requests.exceptions.RequestException:
            return []

    def get_roles(self):
        """Get custom roles"""
        url = f"{BASE_URL}/roles?accountIdentifier={self.account_id}&pageSize=100"
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            data = response.json()
            if "data" in data and "content" in data["data"]:
                return data["data"]["content"]
            return []
        except requests.exceptions.RequestException:
            return []

    def get_api_keys(self):
        """Get API keys"""
        url = f"{BASE_URL}/api-key?accountIdentifier={self.account_id}&pageSize=100"
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            data = response.json()
            if "data" in data and "content" in data["data"]:
                return data["data"]["content"]
            return []
        except requests.exceptions.RequestException:
            return []

