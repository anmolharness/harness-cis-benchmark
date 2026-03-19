# Harness CIS Benchmark Dashboard

Interactive web dashboard for visualizing Harness security compliance.

## Features

- **Real-time Compliance Metrics**: Overall score, passed/failed checks, critical failures
- **Category Breakdown**: Visual charts showing compliance by category
- **Interactive Filtering**: Filter checks by category, status, and severity level
- **Critical Failures Highlight**: Immediate visibility into high-priority issues
- **One-Click Scanning**: Run new scans directly from the dashboard

## Quick Start

### 1. Install Dependencies

```bash
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Set Environment Variables

Create a `.env` file:

```bash
HARNESS_API_KEY=your_api_key_here
HARNESS_ACCOUNT_ID=your_account_id_here
```

### 3. Launch Dashboard

```bash
python3 dashboard.py
```

The dashboard will be available at: **http://localhost:5000**

## Usage

### Running a Scan

1. Open http://localhost:5000 in your browser
2. Click **"🔄 Run New Scan"** button
3. Wait for the scan to complete (usually 10-30 seconds)
4. View results in real-time

### Dashboard Sections

**Summary Cards**
- Compliance Score: Overall percentage and points
- Passed Checks: Number of successful checks
- Failed Checks: Number of failures with critical count
- Last Scan: Timestamp of most recent scan

**Charts**
- Compliance by Category: Bar chart showing per-category scores
- Overall Status: Donut chart showing pass/fail ratio

**Critical Failures**
- Highlighted section showing Level 3 failures
- Immediate visibility for high-priority issues

**All Checks Table**
- Complete list of all benchmark checks
- Filter by category, status, or level
- Detailed results and remediation guidance

## API Endpoints

The dashboard exposes REST APIs for integration:

### GET /api/results
Get cached scan results

### GET /api/scan
Trigger a new benchmark scan

### GET /api/stats
Get summary statistics and compliance metrics

## Development

### File Structure

```
dashboard.py              # Flask application
templates/
  dashboard.html          # Main dashboard UI
static/
  css/dashboard.css       # Styling
  js/dashboard.js         # Interactive features
```

### Extending the Dashboard

To add new metrics or visualizations:

1. Update `dashboard.py` to expose new API endpoints
2. Modify `dashboard.js` to fetch and display new data
3. Add UI components in `dashboard.html`
4. Style with `dashboard.css`

## Production Deployment

For production use:

```bash
# Use a production WSGI server
pip install gunicorn

# Run with gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 dashboard:app
```

## Troubleshooting

**Port 5000 already in use?**
```bash
# Kill existing process
lsof -ti:5000 | xargs kill -9

# Or use a different port
export FLASK_RUN_PORT=8080
python3 dashboard.py
```

**No results showing?**
- Click "Run New Scan" to generate initial data
- Check .env file has correct credentials
- Verify API key has necessary permissions

**Charts not rendering?**
- Ensure Chart.js is loading (check browser console)
- Clear browser cache and reload

## Screenshots

The dashboard provides:
- Clean, modern UI with responsive design
- Color-coded status indicators (green=pass, red=fail)
- Severity badges (Level 1/2/3)
- Real-time updates without page refresh
