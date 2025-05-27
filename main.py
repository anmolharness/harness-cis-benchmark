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
    check_direct_user_role_assignments,
    
)

load_dotenv()

def run_all_rules(api_key, account_id):
    rules = [
        check_sso,
        check_2fa,
        check_lockout_policy,
        check_password_expiration,
        check_password_strength,
        check_direct_user_role_assignments,
        
    ]
    results = [rule(api_key, account_id) for rule in rules]
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
    args = parser.parse_args()

    if not args.api_key or not args.account_id:
        print("❌ Missing --api-key or --account-id (or set them in .env)")
        exit(1)

    results = run_all_rules(args.api_key, args.account_id)
    print_results(results)

    if args.output_file:
        export_results(results, args.output_file)
    
    if args.html_report:
        generate_html(results, args.account_id, args.html_report)
