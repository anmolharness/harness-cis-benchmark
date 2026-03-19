# Harness CIS Benchmark CLI 🔒

This is a Python-based CLI tool to audit your Harness NextGen account against custom CIS-style security benchmarks.

It checks for security, access control, and operational best practices across:

**Security & Access:**
- ✅ SSO enforcement
- ✅ 2FA enforcement
- ✅ Password policies (lockout, expiration, strength)
- ✅ RBAC hygiene (no direct user roles)
- ✅ Service account token expiration
- ✅ External secret manager usage

**Infrastructure & Operations:**
- ✅ Delegate health and configuration
- ✅ Connector scope best practices
- ✅ Environment separation (dev/staging/prod)

**Pipelines & Deployments:**
- ✅ Pipeline GitOps (remote storage)
- ✅ Template reusability
- ✅ Deployment freeze windows
- ✅ Approval gates for production

**Cost & Governance:**
- ✅ IACM cost estimation
- ✅ Resource limits and quotas
- ✅ Governance policy configuration

**Monitoring & Hygiene:**
- ✅ Notification channels configured
- ✅ Audit trail enabled
- ✅ Inactive project detection
- ✅ Unused connector identification

**Reporting:**
- ✅ JSON + HTML reporting with compliance scoring

---

## 🧪 Testing

Comprehensive unit test suite with 50+ tests covering:
- Data collection and caching (3-6x performance optimization)
- Database persistence and remediation tracking
- Check function logic for all 23 checks
- Dashboard API endpoints
- Harness API wrapper

```bash
# Install test dependencies
pip install -r requirements-dev.txt

# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# View coverage report
open htmlcov/index.html
```

See [tests/README.md](tests/README.md) for detailed testing documentation.

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
  --output-file results.json \
  --verbose  # Optional: Enable debug output for API calls

Output
Terminal Report with Pass/Fail per rule
JSON output with detailed results
HTML report suitable for audit export 

Rules Covered

**Category 1: Authentication & Access**
| Rule ID | Description                                     | Level |
| ------- | ----------------------------------------------- | ----- |
| 1.1     | Ensure SSO is enabled                           | 3     |
| 1.2     | Ensure 2FA is enabled for USER\_PASSWORD auth   | 2     |
| 1.3     | Ensure lockout policy is enabled                | 2     |
| 1.4     | Ensure password expiration is enabled           | 1     |
| 1.5     | Ensure password strength policy is enabled      | 1     |

**Category 2: RBAC & Authorization**
| Rule ID | Description                                     | Level |
| ------- | ----------------------------------------------- | ----- |
| 2.1     | Ensure roles are not directly assigned to users | 2     |
| 2.2     | Ensure service account tokens have expiration   | 2     |

**Category 3: Secrets & Connectors**
| Rule ID | Description                                     | Level |
| ------- | ----------------------------------------------- | ----- |
| 3.1     | Ensure external secret manager is configured    | 2     |
| 3.2     | Ensure connectors are scoped appropriately      | 1     |

**Category 4: Delegates**
| Rule ID | Description                                     | Level |
| ------- | ----------------------------------------------- | ----- |
| 4.1     | Ensure delegates are deployed and healthy       | 3     |
| 4.2     | Ensure delegate selectors are configured        | 1     |

**Category 5: Pipeline Best Practices**
| Rule ID | Description                                     | Level |
| ------- | ----------------------------------------------- | ----- |
| 5.1     | Ensure pipelines are stored remotely in Git     | 2     |
| 5.2     | Ensure pipeline templates are used              | 1     |

**Category 6: Governance**
| Rule ID | Description                                     | Level |
| ------- | ----------------------------------------------- | ----- |
| 6.1     | Ensure governance policies are configured       | 2     |

**Category 7: Cost & Resource Management**
| Rule ID | Description                                     | Level |
| ------- | ----------------------------------------------- | ----- |
| 7.1     | Ensure IACM cost estimation is enabled          | 1     |
| 7.2     | Ensure resource quotas/limits are configured    | 1     |

**Category 8: Deployment Safety**
| Rule ID | Description                                     | Level |
| ------- | ----------------------------------------------- | ----- |
| 8.1     | Ensure deployment freeze windows configured     | 2     |
| 8.2     | Ensure production pipelines have approval gates | 2     |

**Category 9: Monitoring & Alerts**
| Rule ID | Description                                     | Level |
| ------- | ----------------------------------------------- | ----- |
| 9.1     | Ensure notification channels are configured     | 1     |
| 9.2     | Ensure audit trail is enabled and retained      | 2     |

**Category 10: Resource Hygiene**
| Rule ID | Description                                     | Level |
| ------- | ----------------------------------------------- | ----- |
| 10.1    | Identify and clean up inactive projects         | 1     |
| 10.2    | Identify and remove unused connectors           | 1     |
| 10.3    | Ensure proper environment separation            | 2     |


🛡️ Coming Soon
    🔄 Cost estimation checks for IACM
    📊 Trend analysis across multiple runs
    ☁️ Cloud storage of reports
    📬 Slack / email notifications
    🧩 Rule plugin system
    🔍 Orphaned resource detection
    ⏰ Freeze window verification

system

🤝 Contributing
Pull requests and issues are welcome!

