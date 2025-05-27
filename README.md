# Harness CIS Benchmark CLI 🔒

This is a Python-based CLI tool to audit your Harness NextGen account against custom CIS-style security benchmarks.

It checks for security and access control best practices across:

- ✅ SSO enforcement
- ✅ 2FA enforcement
- ✅ Password policies
- ✅ RBAC hygiene (no direct user roles)
- ✅ Service account token expiration
- ✅ Org & project scope violations
- ✅ JSON + HTML reporting

---

## 📦 Installation

### 🔧 Clone the repo

```bash
git clone https://github.com/your-org/harness-cis-benchmark.git
cd harness-cis-benchmark

python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

pip install -r requirements.txt

Create a .env file or copy the example .env and populate the data this step is optional
since the cli will also accept both key and account as ARGS
HARNESS_API_KEY=your-api-key
HARNESS_ACCOUNT_ID=your-account-id

Usage
python main.py \
  --api-key YOUR_API_KEY \
  --account-id YOUR_ACCOUNT_ID \
  --html-report results.html \
  --output-file results.json

Output
Terminal Report with Pass/Fail per rule
JSON output with detailed results
HTML report suitable for audit export 

CIS Ruled Covered

| Rule ID | Description                                     | Level |
| ------- | ----------------------------------------------- | ----- |
| 1.1     | Ensure SSO is enabled                           | 3     |
| 1.2     | Ensure 2FA is enabled for USER\_PASSWORD auth   | 2     |
| 1.3     | Ensure lockout policy is enabled                | 2     |
| 1.4     | Ensure password expiration is enabled           | 1     |
| 1.5     | Ensure password strength policy is enabled      | 1     |
| 2.1     | Ensure roles are not directly assigned to users | 2     |
| 2.2     | Ensure service account tokens have expiration   | 2     |


🛡️ Coming Soon
    🔄 Harness pipeline support
    ☁️ Cloud storage of reports
    📬 Slack / email notifications
    🧩 Rule plugin system

system

🤝 Contributing
Pull requests and issues are welcome!

