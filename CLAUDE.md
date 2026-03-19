# CLAUDE.md

This file provides guidance when working with the Harness CIS Benchmark CLI tool.

## Project Overview

Python CLI tool that audits Harness NextGen accounts against CIS-style security benchmarks and operational best practices.

## Recent Major Changes

**2026-03-19 - Production Agent with Interactive Dashboard**
- Transformed into customer-distributable agent
- Added interactive web dashboard with drill-down features
- Docker containerization with production deployment
- Click-to-filter charts and expandable table rows
- Modal detail views with remediation guidance
- Health checks and monitoring endpoints
- Complete distribution package with Docker Compose
- Customer documentation (CUSTOMER_README.md, DEPLOYMENT.md)
- Build script for creating release packages
- Version: 1.0.0

**2026-03-18 (Evening) - Expanded to 23 checks**
- Added 9 new checks across 4 new categories
- Category 7: Cost & Resource Management (7.1, 7.2) - NEW
- Category 8: Deployment Safety (8.1, 8.2) - NEW
- Category 9: Monitoring & Alerts (9.1, 9.2) - NEW
- Category 10: Resource Hygiene (10.1, 10.2, 10.3) - NEW
- New API methods: workspaces, notification rules, freeze windows, services, environments, pipeline executions
- Total checks: 23 (up from 14)

**2026-03-18 (Afternoon) - Expanded from 6 to 14 checks**
- Added 8 new best practices checks across 4 new categories:
- Category 2: Added service account token expiration check (2.2)
- Category 3: Secrets & Connectors (3.1, 3.2) - NEW
- Category 4: Delegates (4.1, 4.2) - NEW
- Category 5: Pipeline Best Practices (5.1, 5.2) - NEW
- Category 6: Governance (6.1) - NEW

**2026-03-18 (Morning) - Fixed all API endpoints**
- Resolved 400 errors by:
- Tokens API: Changed to POST with proper body structure
- Secret Managers API: Added fallback endpoints with multiple response format handling
- Connectors API: Switched from POST to GET with fallback
- Templates API: POST to `/templates/list` with filter body
- Governance Policies API: Updated to correct endpoint with fallback
- Added verbose mode for API debugging

## Commands

### Interactive Dashboard (Recommended)
```bash
# Launch web dashboard
source venv/bin/activate
python3 dashboard.py

# Access at http://localhost:5000
# Click "Run New Scan" to execute checks
# View real-time compliance metrics and charts
```

### CLI Mode
```bash
# Activate virtual environment
source venv/bin/activate

# Run with all options
python main.py \
  --api-key <HARNESS_API_KEY> \
  --account-id <ACCOUNT_ID> \
  --html-report results.html \
  --output-file results.json \
  --verbose  # Optional: debug mode

# Or use environment variables from .env
python main.py --html-report results.html
```

### Setup (first time)
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Code Architecture

**dashboard.py** - Flask web application (NEW)
- Real-time compliance dashboard with interactive charts
- REST API endpoints for scan execution and results
- Caches results for quick retrieval

**api.py** - HarnessAPI class with methods for each endpoint
- All methods have fallback strategies for API variations
- Silent failures for non-critical APIs (return empty lists)
- Handles multiple response structures (data/resource, content/list)

**harness_platform.py** - Check functions organized by category
- Each check returns: id, level, description, result (PASS/FAIL), details
- Levels: 1 (low), 2 (medium), 3 (critical)

**main.py** - CLI entry point
- `run_all_rules()`: executes all checks in category order
- `print_results()`: calculates compliance score
- `export_results()`: JSON and HTML output

**utils.py** - HTML report generation

**templates/** - Dashboard HTML templates

**static/** - CSS and JavaScript for dashboard UI

## Testing After Changes

When modifying checks or API methods:
```bash
# Test with real account
python main.py --api-key $HARNESS_PLATFORM_API_KEY \
  --account-id 9iW-060ARf-7xLCnVrVJbQ \
  --verbose

# Verify results make sense (check compliance score)
# Verify no API errors in output
```

## Known Issues

- Some API endpoints may require different permissions levels
- Token API may fail if account has no tokens configured
- Delegate API response format varies by Harness version

## Future Enhancements (from README)

- Cost estimation checks for IACM
- Trend analysis across multiple runs
- Cloud storage of reports
- Slack/email notifications
- Rule plugin system
- Orphaned resource detection
- Freeze window verification
