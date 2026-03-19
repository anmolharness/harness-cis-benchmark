import argparse
import os
import json
from dotenv import load_dotenv
from utils import generate_html
from harness_platform import (
    check_sso,
    check_2fa,
    check_lockout_policy,
    check_password_expiration,
    check_password_strength,
    check_api_key_rotation,
    check_inactive_users,
    check_session_timeout,
    check_direct_user_role_assignments,
    check_service_account_token_expiration,
    check_account_admin_usage,
    check_user_group_coverage,
    check_custom_roles,
    check_least_privilege,
    check_external_secret_manager,
    check_connector_scope,
    check_secret_usage,
    check_secret_scope,
    check_delegate_health,
    check_delegate_selectors,
    check_delegate_redundancy,
    check_remote_pipelines,
    check_template_usage,
    check_pipeline_failure_rate,
    check_pipeline_timeout_config,
    check_governance_policies,
    check_resource_groups,
    check_iacm_cost_estimation,
    check_resource_limits,
    check_budget_alerts,
    check_freeze_windows,
    check_pipeline_approval_gates,
    check_rollback_configuration,
    check_notification_channels,
    check_audit_trail,
    check_continuous_verification,
    check_inactive_projects,
    check_unused_connectors,
    check_environment_separation,
    check_resource_tagging,
    check_naming_conventions,
)

load_dotenv()

def run_all_rules(api_key, account_id):
    """Run all checks using optimized caching (3-6x faster).

    Old approach: Each check makes its own API call = 20-60 seconds
    New approach: Fetch all data once, pass to checks = 5-10 seconds
    """
    from data_collector import HarnessDataCollector
    from harness_platform_optimized import run_all_checks_optimized

    # Fetch all data once (bulk collection)
    collector = HarnessDataCollector(api_key, account_id)
    collector.collect_all()

    # Run all checks with cached data (no more API calls)
    results = run_all_checks_optimized(collector)

    return results

def print_results(results):
    print("\n=== HARNESS CIS PLATFORM BENCHMARK RESULTS ===")
    score = 0
    for rule in results:
        print(f"[{rule['id']}] {rule['description']} - {rule['result']}")
        print(f"Details: {rule['details']}")
        print(f"Level: {rule['level']}")
        print("—" * 50)
        if rule["result"] == "PASS":
            score += rule["level"]  # weighted score

    max_score = sum(rule["level"] for rule in results)
    print(f"Compliance Score: {score}/{max_score} ({(score/max_score)*100:.1f}%)\n")

def export_results(results, output_file):
    with open(output_file, "w") as f:
        json.dump(results, f, indent=2)
    print(f"[✓] Results exported to {output_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--api-key", help="Harness API Key", default=os.getenv("HARNESS_API_KEY"))
    parser.add_argument("--account-id", help="Harness Account ID", default=os.getenv("HARNESS_ACCOUNT_ID"))
    parser.add_argument("--output-file", help="Path to save JSON results (optional)")
    parser.add_argument("--html-report", help="Path to save HTML report (optional)")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose/debug output")
    args = parser.parse_args()

    # Store verbose flag globally for API calls
    import builtins
    builtins.VERBOSE_MODE = args.verbose

    if not args.api_key or not args.account_id:
        print("❌ Missing --api-key or --account-id (or set them in .env)")
        exit(1)

    results = run_all_rules(args.api_key, args.account_id)
    print_results(results)

    if args.output_file:
        export_results(results, args.output_file)
    
    if args.html_report:
        generate_html(results, args.account_id, args.html_report)
