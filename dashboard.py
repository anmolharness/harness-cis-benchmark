"""Interactive web dashboard for Harness CIS Benchmark results."""
import os
import json
from datetime import datetime
from flask import Flask, render_template, jsonify, request
from dotenv import load_dotenv
from harness_api import HarnessAPI
from main import run_all_rules
from database import BenchmarkDatabase
import logging

load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False

# Initialize database
db = BenchmarkDatabase()

# Cache for latest results
latest_results = None
latest_timestamp = None

# Version info
VERSION = "1.0.1"
BUILD_DATE = "2026-03-19"


def get_category_stats(results):
    """Extract statistics by category."""
    categories = {}
    for check in results:
        cat_id = check['id'].split('.')[0]
        cat_name = {
            '1': 'Authentication & Access',
            '2': 'RBAC & Authorization',
            '3': 'Secrets & Connectors',
            '4': 'Delegates',
            '5': 'Pipeline Best Practices',
            '6': 'Governance',
            '7': 'Cost & Resource Management',
            '8': 'Deployment Safety',
            '9': 'Monitoring & Alerts',
            '10': 'Resource Hygiene'
        }.get(cat_id, f'Category {cat_id}')

        if cat_name not in categories:
            categories[cat_name] = {
                'total': 0,
                'passed': 0,
                'failed': 0,
                'points': 0,
                'max_points': 0
            }

        categories[cat_name]['total'] += 1
        categories[cat_name]['max_points'] += check['level']

        if check['result'] == 'PASS':
            categories[cat_name]['passed'] += 1
            categories[cat_name]['points'] += check['level']
        else:
            categories[cat_name]['failed'] += 1

    return categories


def calculate_compliance_score(results):
    """Calculate overall compliance score."""
    total_points = sum(r['level'] for r in results)
    passed_points = sum(r['level'] for r in results if r['result'] == 'PASS')
    percentage = (passed_points / total_points * 100) if total_points > 0 else 0

    return {
        'passed_points': passed_points,
        'total_points': total_points,
        'percentage': round(percentage, 1),
        'passed_checks': sum(1 for r in results if r['result'] == 'PASS'),
        'failed_checks': sum(1 for r in results if r['result'] == 'FAIL'),
        'total_checks': len(results)
    }


@app.route('/')
def index():
    """Render main dashboard."""
    return render_template('dashboard.html')


@app.route('/api/results')
def get_results():
    """Get latest benchmark results."""
    global latest_results, latest_timestamp

    # Return cached results if available
    if latest_results:
        return jsonify({
            'results': latest_results,
            'timestamp': latest_timestamp,
            'cached': True
        })

    return jsonify({'error': 'No results available. Run a scan first.'}), 404


@app.route('/api/scan')
def run_scan():
    """Run a new benchmark scan."""
    global latest_results, latest_timestamp

    api_key = os.getenv('HARNESS_API_KEY')
    account_id = os.getenv('HARNESS_ACCOUNT_ID')

    if not api_key or not account_id:
        return jsonify({'error': 'Missing API credentials'}), 400

    try:
        # Run all checks
        results = run_all_rules(api_key, account_id)

        # Calculate statistics
        compliance = calculate_compliance_score(results)
        categories = get_category_stats(results)

        # Save to database
        scan_id = db.save_scan(account_id, results, compliance)
        logger.info(f"Saved scan {scan_id} to database")

        # Get remediated checks (checks that were FAIL before, PASS now)
        remediated_checks = db.get_remediated_checks()

        # Mark remediated checks
        for check in results:
            if check['id'] in remediated_checks:
                check['remediated'] = True
                check['original_result'] = check['result']
                # Keep the result as PASS but add remediation flag

        latest_results = results
        latest_timestamp = datetime.now().isoformat()

        return jsonify({
            'results': results,
            'timestamp': latest_timestamp,
            'compliance': compliance,
            'categories': categories,
            'remediated_count': len(remediated_checks),
            'scan_id': scan_id
        })
    except Exception as e:
        logger.error(f"Scan failed: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500


@app.route('/api/stats')
def get_stats():
    """Get summary statistics."""
    global latest_results

    if not latest_results:
        return jsonify({'error': 'No results available'}), 404

    compliance = calculate_compliance_score(latest_results)
    categories = get_category_stats(latest_results)

    # Get critical failures
    critical_failures = [
        r for r in latest_results
        if r['result'] == 'FAIL' and r['level'] == 3
    ]

    return jsonify({
        'compliance': compliance,
        'categories': categories,
        'critical_failures': critical_failures,
        'timestamp': latest_timestamp
    })


@app.route('/health')
def health_check():
    """Health check endpoint for monitoring."""
    return jsonify({
        'status': 'healthy',
        'version': VERSION,
        'build_date': BUILD_DATE,
        'has_results': latest_results is not None
    })


@app.route('/api/info')
def get_info():
    """Get dashboard version and info."""
    return jsonify({
        'name': 'Harness CIS Benchmark Dashboard',
        'version': VERSION,
        'build_date': BUILD_DATE,
        'total_checks': 41,
        'categories': 10
    })


@app.route('/api/history')
def get_history():
    """Get scan history."""
    try:
        limit = int(request.args.get('limit', 10))
        history = db.get_scan_history(limit)
        return jsonify({'history': history})
    except Exception as e:
        logger.error(f"Failed to get history: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/check/<check_id>/history')
def get_check_history_api(check_id):
    """Get history for a specific check."""
    try:
        limit = int(request.args.get('limit', 5))
        history = db.get_check_history(check_id, limit)
        return jsonify({'check_id': check_id, 'history': history})
    except Exception as e:
        logger.error(f"Failed to get check history: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/statistics')
def get_statistics_api():
    """Get database statistics."""
    try:
        stats = db.get_statistics()
        return jsonify(stats)
    except Exception as e:
        logger.error(f"Failed to get statistics: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/trends')
def get_trends():
    """Get compliance trends over time."""
    try:
        history = db.get_scan_history(limit=30)

        # Format for charting
        trends = {
            'labels': [h['timestamp'][:10] for h in reversed(history)],  # Date only
            'compliance': [h['compliance_percentage'] for h in reversed(history)],
            'passed': [h['passed_checks'] for h in reversed(history)],
            'failed': [h['failed_checks'] for h in reversed(history)]
        }

        return jsonify(trends)
    except Exception as e:
        logger.error(f"Failed to get trends: {e}")
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    logger.info("🚀 Starting Harness CIS Benchmark Dashboard...")
    logger.info(f"📊 Version: {VERSION}")
    logger.info("📊 Dashboard available at: http://localhost:5000")
    logger.info("🔄 Run a scan at: http://localhost:5000/api/scan")

    # Check for required env vars
    if not os.getenv('HARNESS_API_KEY') or not os.getenv('HARNESS_ACCOUNT_ID'):
        logger.warning("⚠️  HARNESS_API_KEY and HARNESS_ACCOUNT_ID not set in environment")
        logger.warning("⚠️  Set these in .env file or environment variables")

    debug_mode = os.getenv('FLASK_ENV') != 'production'
    app.run(debug=debug_mode, host='0.0.0.0', port=5000)
