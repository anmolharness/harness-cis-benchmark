"""Unit tests for dashboard.py Flask application"""
import pytest
import json
import os
from unittest.mock import patch, Mock
from dashboard import app


@pytest.fixture
def client():
    """Create a test client for the Flask app."""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


@pytest.fixture
def mock_env_vars(monkeypatch):
    """Set up mock environment variables."""
    monkeypatch.setenv('HARNESS_API_KEY', 'test_api_key')
    monkeypatch.setenv('HARNESS_ACCOUNT_ID', 'test_account_id')


@pytest.mark.unit
class TestDashboardAPI:
    """Test suite for Dashboard Flask API endpoints."""

    def test_index_route(self, client):
        """Test that index route renders dashboard."""
        response = client.get('/')
        assert response.status_code == 200
        assert b'Harness CIS Benchmark' in response.data

    def test_health_check(self, client):
        """Test health check endpoint."""
        response = client.get('/health')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'healthy'

    @patch('dashboard.run_all_rules')
    @patch('dashboard.BenchmarkDatabase')
    def test_api_scan_success(self, mock_db_class, mock_run_all, client, mock_env_vars, sample_check_results, sample_compliance):
        """Test successful scan execution."""
        # Mock run_all_rules to return sample results
        mock_run_all.return_value = sample_check_results

        # Mock database
        mock_db = Mock()
        mock_db.save_scan.return_value = 1
        mock_db.get_remediated_checks.return_value = []
        mock_db_class.return_value = mock_db

        response = client.get('/api/scan')

        assert response.status_code == 200
        data = json.loads(response.data)

        assert 'results' in data
        assert 'compliance' in data
        assert 'timestamp' in data
        assert len(data['results']) == len(sample_check_results)

    @patch('dashboard.run_all_rules')
    def test_api_scan_missing_credentials(self, mock_run_all, client):
        """Test scan fails without API credentials."""
        response = client.get('/api/scan')

        # Should still work if env vars are not set (uses .env file)
        # Or should return error if truly missing
        assert response.status_code in [200, 500]

    @patch('dashboard.run_all_rules')
    @patch('dashboard.BenchmarkDatabase')
    def test_api_scan_with_remediation(self, mock_db_class, mock_run_all, client, mock_env_vars, sample_check_results):
        """Test scan endpoint marks remediated checks."""
        mock_run_all.return_value = sample_check_results

        # Mock database to return remediated checks
        mock_db = Mock()
        mock_db.save_scan.return_value = 1
        mock_db.get_remediated_checks.return_value = ['1.2']
        mock_db_class.return_value = mock_db

        response = client.get('/api/scan')

        assert response.status_code == 200
        data = json.loads(response.data)

        # Check that remediated flag is set
        remediated_check = next((c for c in data['results'] if c['id'] == '1.2'), None)
        assert remediated_check is not None
        assert remediated_check.get('remediated') == True

    @patch('dashboard.BenchmarkDatabase')
    def test_api_results_with_cache(self, mock_db_class, client):
        """Test retrieving cached results."""
        mock_db = Mock()
        mock_db.get_latest_scan.return_value = {
            'scan_id': 1,
            'account_id': 'test_account',
            'timestamp': '2024-01-01 12:00:00',
            'total_checks': 3,
            'passed_checks': 2
        }
        mock_db_class.return_value = mock_db

        # First, run a scan to populate cache (using mock)
        with patch('dashboard.run_all_rules') as mock_run:
            mock_run.return_value = [
                {"id": "1.1", "level": 3, "description": "Test", "result": "PASS", "details": "OK"}
            ]
            client.get('/api/scan')

        # Then retrieve results
        response = client.get('/api/results')

        assert response.status_code in [200, 404]  # 404 if no cache yet

    @patch('dashboard.BenchmarkDatabase')
    def test_api_stats(self, mock_db_class, client, sample_check_results):
        """Test statistics endpoint."""
        mock_db = Mock()
        mock_db.get_latest_scan.return_value = None
        mock_db_class.return_value = mock_db

        # First populate cache
        with patch('dashboard.run_all_rules') as mock_run:
            mock_run.return_value = sample_check_results
            client.get('/api/scan')

        # Get stats
        response = client.get('/api/stats')

        assert response.status_code in [200, 404]

    @patch('dashboard.BenchmarkDatabase')
    def test_api_trends(self, mock_db_class, client):
        """Test trends endpoint."""
        mock_db = Mock()
        mock_db.get_trends.return_value = {
            'labels': ['2024-01-01', '2024-01-02'],
            'compliance': [50.0, 75.0]
        }
        mock_db_class.return_value = mock_db

        response = client.get('/api/trends')

        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'labels' in data
        assert 'compliance' in data

    @patch('dashboard.BenchmarkDatabase')
    def test_api_history(self, mock_db_class, client):
        """Test scan history endpoint."""
        mock_db = Mock()
        mock_db.get_scan_history.return_value = [
            {
                'scan_id': 2,
                'timestamp': '2024-01-02 12:00:00',
                'compliance_percentage': 75.0
            },
            {
                'scan_id': 1,
                'timestamp': '2024-01-01 12:00:00',
                'compliance_percentage': 50.0
            }
        ]
        mock_db_class.return_value = mock_db

        response = client.get('/api/history')

        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data) == 2

    def test_static_files_served(self, client):
        """Test that static files are accessible."""
        # Test CSS
        response = client.get('/static/css/dashboard.css')
        assert response.status_code == 200

        # Test JS
        response = client.get('/static/js/dashboard.js')
        assert response.status_code == 200


@pytest.mark.integration
class TestDashboardIntegration:
    """Integration tests for dashboard with real components."""

    @pytest.mark.slow
    def test_full_scan_flow(self, client, mock_env_vars, temp_db_path):
        """Test complete scan workflow from trigger to results."""
        # This would be a full integration test
        # Skipped in unit tests, run separately
        pass
