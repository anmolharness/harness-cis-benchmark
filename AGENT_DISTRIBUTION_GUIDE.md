# Harness CIS Benchmark Agent - Distribution Guide

Instructions for distributing this agent to customers.

## Quick Distribution

### Build Everything

```bash
./build-agent.sh
```

This creates in `dist/`:
- `harness-cis-agent-v1.0.0.tar.gz` - Source code package
- `harness-cis-agent-docker-v1.0.0.tar.gz` - Docker image
- SHA256 checksums for verification

### Customer Delivery Options

## Option 1: Docker Image (Recommended)

**Send customers:**
1. `harness-cis-agent-docker-v1.0.0.tar.gz` (Docker image)
2. `CUSTOMER_README.md` (instructions)
3. `.env.example` (configuration template)

**Customer setup:**
```bash
# Load Docker image
docker load < harness-cis-agent-docker-v1.0.0.tar.gz

# Create configuration
cp .env.example .env
# Edit .env with their credentials

# Run agent
docker run -d \
  -p 5000:5000 \
  --env-file .env \
  --name harness-compliance \
  harness-cis-benchmark:1.0.0
```

## Option 2: Source Package

**Send customers:**
1. `harness-cis-agent-v1.0.0.tar.gz` (source code)
2. `CUSTOMER_README.md` (instructions)

**Customer setup:**
```bash
# Extract package
tar -xzf harness-cis-agent-v1.0.0.tar.gz
cd harness-cis-agent-v1.0.0

# Run with Docker Compose
docker-compose up -d

# Or run with Python
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python3 dashboard.py
```

## Option 3: Private Registry

**Push to your registry:**
```bash
# Tag for your registry
docker tag harness-cis-benchmark:1.0.0 \
  your-registry.com/harness-cis-benchmark:1.0.0

# Push
docker push your-registry.com/harness-cis-benchmark:1.0.0
```

**Customer pulls from registry:**
```bash
docker pull your-registry.com/harness-cis-benchmark:1.0.0
docker run -d -p 5000:5000 \
  -e HARNESS_API_KEY=xxx \
  -e HARNESS_ACCOUNT_ID=xxx \
  your-registry.com/harness-cis-benchmark:1.0.0
```

## Customer Onboarding Checklist

Share this with customers:

### Prerequisites
- [ ] Docker installed (20.10+) OR Python 3.11+
- [ ] Harness account with API access
- [ ] Network access to app.harness.io

### Setup Steps
1. [ ] Create Harness API key (Account Settings → API Keys)
   - Required permissions: Account Viewer or higher
   - Note: Read-only access is sufficient

2. [ ] Get Account ID from Harness URL
   - Format: `https://app.harness.io/ng/account/<ACCOUNT_ID>/`

3. [ ] Choose deployment method (Docker/Python)

4. [ ] Configure credentials in `.env` file

5. [ ] Launch agent

6. [ ] Access dashboard at http://localhost:5000

7. [ ] Run first scan

8. [ ] Review results and remediate issues

### Post-Deployment
- [ ] Schedule regular scans (daily/weekly)
- [ ] Set up monitoring/alerts
- [ ] Document findings and track progress
- [ ] Share results with security team

## Sales Talking Points

### Value Proposition
"Automated compliance monitoring for your Harness platform with zero configuration"

### Key Benefits
- ✅ **41 Best Practice Checks** - Comprehensive coverage
- 🚀 **5-Minute Setup** - Docker one-liner to get started
- 🔒 **Runs in Your Environment** - Data never leaves your infrastructure
- 📊 **Visual Dashboard** - Executive-friendly compliance reports
- 🔍 **Actionable Insights** - Specific remediation steps for each issue
- 💰 **Cost Savings** - Identify unused resources and optimize spending

### Common Objections & Responses

**"We already have compliance tools"**
→ This is Harness-specific. General tools don't understand Harness best practices.

**"We don't have time to set up another tool"**
→ Literally 5 minutes. One Docker command and you're running.

**"What about security/data privacy?"**
→ Runs entirely in your environment. Read-only API access. No data leaves your network.

**"How often do we need to run scans?"**
→ Set it and forget it. Schedule weekly scans, review results quarterly.

**"What if we fail all the checks?"**
→ That's the point! Identifies gaps so you can improve. Start with critical (Level 3) issues.

## Pricing Models (Examples)

### Free Tier
- Basic agent
- Manual scans
- HTML reports
- Community support

### Professional
- Automated scheduling
- Email notifications
- Trend analysis
- Priority support

### Enterprise
- Multi-account support
- Custom checks
- SSO integration
- Dedicated success manager

## Support & Maintenance

### Customer Support Tiers

**Self-Service (Included)**
- Documentation (CUSTOMER_README.md, DEPLOYMENT.md)
- GitHub issues/discussions
- Community forums

**Email Support (Optional)**
- 48-hour response time
- Installation assistance
- Troubleshooting help

**Premium Support (Optional)**
- 4-hour response time
- Dedicated Slack channel
- Custom deployment assistance
- Quarterly business reviews

### Maintenance Schedule

**Monthly:**
- Security updates
- Bug fixes
- Harness API compatibility

**Quarterly:**
- New checks based on Harness releases
- Feature enhancements
- Dashboard improvements

**Annually:**
- Major version upgrades
- Architecture improvements

## Customization Options

### White-Label Branding

Customers can customize:
```python
# dashboard.py - Update branding
VERSION = "1.0.0 - ACME Corp Edition"

# templates/dashboard.html - Update header
<h1>🛡️ ACME Security Compliance Dashboard</h1>

# static/css/dashboard.css - Update colors
:root {
    --primary-color: #YOUR-BRAND-COLOR;
}
```

### Custom Checks

Add customer-specific checks:
```python
# custom_checks.py
def check_custom_policy(api_key, account_id):
    # Customer-specific compliance check
    return {
        "id": "100.1",
        "level": 3,
        "description": "ACME Corp Policy XYZ",
        "result": "PASS",
        "details": "All resources comply with ACME policy"
    }
```

## Metrics to Track

Monitor these for customer success:

**Adoption Metrics:**
- Time to first scan
- Scan frequency
- Dashboard logins

**Engagement Metrics:**
- Compliance score trend
- Issues remediated
- Critical failures resolved

**Business Impact:**
- Security incidents prevented
- Audit preparation time saved
- Cost savings from resource optimization

## Success Stories Template

**Before Agent:**
- Manual compliance checks took 40 hours/quarter
- Security gaps discovered during audits
- No visibility into Harness configuration drift

**After Agent:**
- 5-minute automated scans on demand
- Proactive issue identification
- 95% compliance score achieved

**ROI:**
- $50K saved annually in manual audit prep
- Zero compliance findings in external audit
- Improved security posture

## Marketing Materials

### Email Template

```
Subject: Automated Compliance for Your Harness Platform

Hi [Customer],

We've developed a new tool to help you maintain security and operational
excellence in Harness: the CIS Benchmark Agent.

What it does:
✅ Scans your Harness account against 41 best practices
📊 Provides visual dashboard with compliance score
🔧 Gives specific remediation steps

Setup takes 5 minutes. Runs entirely in your environment.

Interested in a demo? Let's schedule 15 minutes.

[Schedule Demo]
```

### One-Pager Content

**Headline:** Automated Harness Compliance in 5 Minutes

**Subhead:** Security best practices monitoring for your CI/CD platform

**Features:**
- 41 comprehensive checks
- Interactive dashboard
- Docker deployment
- Zero configuration

**Benefits:**
- Pass audits with confidence
- Identify security gaps early
- Optimize costs
- Save time on manual reviews

**Proof:** [Customer testimonial or case study]

**Call to Action:** Download free trial

## Technical FAQs

**Q: Does it work with Harness FirstGen?**
A: No, NextGen only. FirstGen uses different APIs.

**Q: Can we run multiple instances for different accounts?**
A: Yes! Use different ports or different servers.

**Q: Does it require delegate access?**
A: No, just Harness API access.

**Q: What Harness APIs does it call?**
A: All read-only APIs (users, pipelines, secrets metadata, etc.)

**Q: Can we customize the checks?**
A: Yes! Add your own in custom_checks.py

**Q: Does it modify anything in Harness?**
A: No, 100% read-only.

---

**Ready to distribute?** Run `./build-agent.sh` and send customers the package!
