# Harness CIS Benchmark Agent

Enterprise-grade security compliance dashboard for your Harness account.

## What is This?

The Harness CIS Benchmark Agent is a compliance tool that:

✅ **Scans** your Harness account against 41 security and operational best practices
📊 **Visualizes** compliance with interactive charts and dashboards
🔍 **Identifies** critical security gaps with remediation guidance
🚀 **Runs** entirely in your environment - your data stays with you

## Quick Start (5 Minutes)

### Step 1: Get Your Credentials

You need two things:
1. **Harness API Key** - Create in Harness UI → Account Settings → API Keys
2. **Account ID** - Found in Harness URL: `https://app.harness.io/ng/account/<ACCOUNT_ID>/`

### Step 2: Run the Agent

**Using Docker (Easiest):**

```bash
# Set your credentials
export HARNESS_API_KEY="your_key_here"
export HARNESS_ACCOUNT_ID="your_account_id"

# Run the agent
docker run -d \
  -p 5000:5000 \
  -e HARNESS_API_KEY=$HARNESS_API_KEY \
  -e HARNESS_ACCOUNT_ID=$HARNESS_ACCOUNT_ID \
  --name harness-compliance \
  harness-cis-benchmark:latest
```

**Using Docker Compose:**

```bash
# 1. Create .env file with your credentials:
cat > .env << EOF
HARNESS_API_KEY=your_key_here
HARNESS_ACCOUNT_ID=your_account_id
EOF

# 2. Start the agent:
docker-compose up -d
```

### Step 3: Open Dashboard

Visit: **http://localhost:5000**

Click **"🔄 Run New Scan"** and wait 10-30 seconds for results.

## What Gets Checked?

The agent evaluates 41 checks across 10 categories:

| Category | Checks | Focus |
|----------|--------|-------|
| 🔐 Authentication & Access | 8 | SSO, 2FA, password policies |
| 👥 RBAC & Authorization | 6 | Role assignments, least privilege |
| 🔑 Secrets & Connectors | 4 | External secret managers, scoping |
| 🤖 Delegates | 3 | Health, redundancy, selectors |
| 🚀 Pipeline Best Practices | 4 | Remote storage, templates, timeouts |
| 📋 Governance | 2 | OPA policies, resource groups |
| 💰 Cost Management | 3 | Budget alerts, resource limits |
| 🛡️ Deployment Safety | 3 | Freeze windows, approvals, rollbacks |
| 📊 Monitoring & Alerts | 3 | Notifications, audit trail, verification |
| 🧹 Resource Hygiene | 5 | Tagging, naming, cleanup |

## Understanding Your Score

**Compliance Score = Passed Points / Total Points**

Each check has a severity level:
- **Level 3** (Critical) - 3 points
- **Level 2** (Medium) - 2 points
- **Level 1** (Low) - 1 point

**Example:**
- Total: 41 checks = 61 points possible
- Passed: 31 points
- **Score: 50.8%**

## Features

### Interactive Dashboard

**📊 Summary Cards**
- Overall compliance percentage
- Passed/failed check counts
- Critical failure alerts
- Last scan timestamp

**📈 Visual Charts**
- Category compliance bar chart (click to filter)
- Pass/fail donut chart (click to filter)
- Color-coded severity indicators

**🔍 Drill-Down Details**
- Click any check row to expand
- View specific findings
- Get remediation instructions
- Access Harness documentation links

**🚨 Critical Failures**
- Dedicated section for Level 3 issues
- Immediate visibility of high-priority risks

### API Access

Integrate with your tools:

```bash
# Get latest results (JSON)
curl http://localhost:5000/api/results

# Trigger new scan
curl http://localhost:5000/api/scan

# Get summary stats
curl http://localhost:5000/api/stats

# Health check
curl http://localhost:5000/health
```

## Security & Privacy

✅ **Runs in Your Environment** - Agent runs on your infrastructure
✅ **No Data Leaves** - All processing happens locally
✅ **Read-Only Access** - Agent only queries Harness APIs
✅ **No Credentials Stored** - API keys in environment variables only
✅ **Open Source** - Review all code before deployment

## Remediation Examples

Each failed check includes specific guidance:

**Example: SSO Not Enabled (Check 1.1)**
```
🔧 Remediation:
Enable SSO in Account Settings → Authentication → Configure SAML/OAuth provider

📚 Documentation:
https://docs.harness.io/category/authentication-and-authorization
```

**Example: Too Many Account Admins (Check 2.3)**
```
🔧 Remediation:
Limit Account Admin role to 2-3 trusted administrators.
Create custom roles for other users.

📚 Documentation:
https://docs.harness.io/article/vz5cq0nfg2-rbac-in-harness
```

## Scheduling Regular Scans

**Daily Scans with Cron:**
```bash
# Add to crontab
0 9 * * * docker exec harness-compliance curl -s http://localhost:5000/api/scan > /var/log/harness-scan.log
```

**Weekly Email Reports:**
```bash
#!/bin/bash
# scan-and-email.sh
curl -s http://localhost:5000/api/scan > results.json
python3 -c "
import json, smtplib
with open('results.json') as f:
    data = json.load(f)
# Send email with results...
"
```

## Troubleshooting

**Dashboard won't load?**
```bash
# Check if agent is running
docker ps | grep harness-compliance

# View logs
docker logs harness-compliance

# Restart agent
docker-compose restart
```

**No scan results?**
- Verify API key has correct permissions (Account Viewer or higher)
- Check account ID is correct
- Ensure network access to app.harness.io

**Slow scans?**
- Normal scan time: 10-30 seconds
- If longer, check Harness API response times
- Review delegate health in your account

## Upgrading

```bash
# Pull latest version
docker pull harness-cis-benchmark:latest

# Restart with new version
docker-compose down
docker-compose up -d
```

## Support

**Documentation:** See `DEPLOYMENT.md` for detailed deployment options

**API Permissions Required:**
- View Users, User Groups, Roles
- View Connectors, Secrets, Delegates
- View Pipelines, Templates, Policies

**System Requirements:**
- Docker 20.10+ or Python 3.11+
- 512MB RAM minimum
- Network access to app.harness.io

## What's Next?

1. **Run your first scan** - Click "Run New Scan" in the dashboard
2. **Review critical failures** - Focus on Level 3 issues first
3. **Implement fixes** - Follow remediation guidance
4. **Re-scan** - Verify improvements
5. **Schedule regular scans** - Track compliance over time

---

**Questions?** Contact your Harness representative for support.

**Version:** 1.0.0 | **Last Updated:** 2026-03-19
