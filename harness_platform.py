from api import HarnessAPI

def check_sso(api_key, account_id):
    api = HarnessAPI(api_key, account_id)
    config = api.get_auth_config()
    mechanism = config.get("authenticationMechanism", "UNKNOWN")
    passed = mechanism != "USER_PASSWORD"

    return {
        "id": "1.1",
        "level": 3,
        "description": "Ensure SSO is enabled",
        "result": "PASS" if passed else "FAIL",
        "details": f"Authentication mechanism: {mechanism}"
    }

def check_2fa(api_key, account_id):
    api = HarnessAPI(api_key, account_id)
    config = api.get_auth_config()
    enabled = config.get("twoFactorEnabled", False)
    passed = enabled

    return {
        "id": "1.2",
        "level": 2,
        "description": "Ensure Two-Factor Authentication is enabled for USER_PASSWORD",
        "result": "PASS" if passed else "FAIL",
        "details": f"2FA enabled: {enabled}"
    }

def check_lockout_policy(api_key, account_id):
    api = HarnessAPI(api_key, account_id)
    config = api.get_auth_config()
    policy = config.get("ngAuthSettings", [{}])[0].get("loginSettings", {}).get("userLockoutPolicy", {})
    enabled = policy.get("enableLockoutPolicy", False)

    return {
        "id": "1.3",
        "level": 2,
        "description": "Ensure User Lockout Policy is enabled",
        "result": "PASS" if enabled else "FAIL",
        "details": f"Lockout policy enabled: {enabled}"
    }

def check_password_expiration(api_key, account_id):
    api = HarnessAPI(api_key, account_id)
    config = api.get_auth_config()
    policy = config.get("ngAuthSettings", [{}])[0].get("loginSettings", {}).get("passwordExpirationPolicy", {})
    enabled = policy.get("enabled", False)

    return {
        "id": "1.4",
        "level": 1,
        "description": "Ensure Password Expiration Policy is enabled",
        "result": "PASS" if enabled else "FAIL",
        "details": f"Password expiration policy enabled: {enabled}"
    }

def check_password_strength(api_key, account_id):
    api = HarnessAPI(api_key, account_id)
    config = api.get_auth_config()
    policy = config.get("ngAuthSettings", [{}])[0].get("loginSettings", {}).get("passwordStrengthPolicy", {})
    enabled = policy.get("enabled", False)

    return {
        "id": "1.5",
        "level": 1,
        "description": "Ensure Password Strength Policy is enabled",
        "result": "PASS" if enabled else "FAIL",
        "details": f"Password strength policy enabled: {enabled}"
    }



def check_direct_user_role_assignments(api_key, account_id):
    api = HarnessAPI(api_key, account_id)
    direct_assignments = []

    # Account scope
    account_roles = api.get_role_assignments_for_scope("")
    for entry in account_roles:
        principal = entry.get("roleAssignment", {}).get("principal", {})
        if principal.get("type") == "USER":
            direct_assignments.append({
                "scope": "account",
                "user": principal.get("identifier"),
                "role": entry.get("roleAssignment", {}).get("roleIdentifier")
            })

    # Org & project scopes
    orgs = api.get_organizations()
    for org in orgs:
        org_id = org["identifier"]

        # Org scope
        org_roles = api.get_role_assignments_for_scope(f"orgIdentifier={org_id}")
        for entry in org_roles:
            principal = entry.get("roleAssignment", {}).get("principal", {})
            if principal.get("type") == "USER":
                direct_assignments.append({
                    "scope": f"org:{org_id}",
                    "user": principal.get("identifier"),
                    "role": entry.get("roleAssignment", {}).get("roleIdentifier")
                })

        # Project scope
        projects = api.get_projects(org_id)
        for project in projects:
            project_id = project["identifier"]
            query = f"orgIdentifier={org_id}&projectIdentifier={project_id}"
            project_roles = api.get_role_assignments_for_scope(query)
            for entry in project_roles:
                principal = entry.get("roleAssignment", {}).get("principal", {})
                if principal.get("type") == "USER":
                    direct_assignments.append({
                        "scope": f"project:{org_id}/{project_id}",
                        "user": principal.get("identifier"),
                        "role": entry.get("roleAssignment", {}).get("roleIdentifier")
                    })

    passed = len(direct_assignments) == 0
    return {
        "id": "2.1",
        "level": 2,
        "description": "Ensure roles are assigned via user groups, not directly to users",
        "result": "PASS" if passed else "FAIL",
        "details": f"Users with direct role assignments: {direct_assignments if not passed else 'None'}"
    }





