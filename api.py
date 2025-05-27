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
        url = f"https://app.harness.io/ng/api/token/aggregate?accountIdentifier={self.account_id}"
        if org_id:
            url += f"&orgIdentifier={org_id}"
        if project_id:
            url += f"&projectIdentifier={project_id}"
        url += "&includeOnlyActiveTokens=true"
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json().get("resource", {}).get("content", [])
        except requests.exceptions.RequestException as e:
            print(f"[ERROR] Failed to fetch tokens: {e}")
            return []

