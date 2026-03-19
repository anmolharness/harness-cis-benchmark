"""Unit tests for database.py"""
import pytest
import os
from database import BenchmarkDatabase


@pytest.mark.unit
class TestBenchmarkDatabase:
    """Test suite for BenchmarkDatabase class."""

    def test_initialization(self, temp_db_path):
        """Test database initialization."""
        db = BenchmarkDatabase(temp_db_path)
        assert os.path.exists(temp_db_path)
        db.close()

    def test_schema_creation(self, temp_db_path):
        """Test that database schema is created correctly."""
        db = BenchmarkDatabase(temp_db_path)

        # Check tables exist
        cursor = db.conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        )
        tables = {row[0] for row in cursor.fetchall()}

        assert 'scans' in tables
        assert 'check_results' in tables
        db.close()

    def test_save_scan(self, temp_db_path, sample_check_results, sample_compliance, mock_account_id):
        """Test saving a scan to the database."""
        db = BenchmarkDatabase(temp_db_path)

        scan_id = db.save_scan(mock_account_id, sample_check_results, sample_compliance)

        assert scan_id > 0

        # Verify scan was saved
        cursor = db.conn.execute("SELECT * FROM scans WHERE id = ?", (scan_id,))
        scan = cursor.fetchone()
        assert scan is not None
        assert scan[1] == mock_account_id
        assert scan[2] == sample_compliance['total_checks']
        assert scan[3] == sample_compliance['passed_checks']

        # Verify check results were saved
        cursor = db.conn.execute("SELECT * FROM check_results WHERE scan_id = ?", (scan_id,))
        results = cursor.fetchall()
        assert len(results) == len(sample_check_results)
        db.close()

    def test_get_latest_scan(self, temp_db_path, sample_check_results, sample_compliance, mock_account_id):
        """Test retrieving the latest scan."""
        db = BenchmarkDatabase(temp_db_path)

        # Save two scans
        db.save_scan(mock_account_id, sample_check_results, sample_compliance)
        scan_id_2 = db.save_scan(mock_account_id, sample_check_results, sample_compliance)

        latest = db.get_latest_scan()

        assert latest is not None
        assert latest['scan_id'] == scan_id_2
        assert latest['account_id'] == mock_account_id
        db.close()

    def test_get_previous_scan(self, temp_db_path, sample_check_results, sample_compliance, mock_account_id):
        """Test retrieving the previous scan."""
        db = BenchmarkDatabase(temp_db_path)

        # Save two scans
        scan_id_1 = db.save_scan(mock_account_id, sample_check_results, sample_compliance)
        db.save_scan(mock_account_id, sample_check_results, sample_compliance)

        previous = db.get_previous_scan()

        assert previous is not None
        assert previous['scan_id'] == scan_id_1
        db.close()

    def test_get_remediated_checks(self, temp_db_path, mock_account_id):
        """Test detecting remediated checks (FAIL -> PASS)."""
        db = BenchmarkDatabase(temp_db_path)

        # First scan - some failures
        first_results = [
            {"id": "1.1", "level": 3, "description": "Test 1", "result": "FAIL", "details": "Failed"},
            {"id": "1.2", "level": 3, "description": "Test 2", "result": "PASS", "details": "Passed"},
            {"id": "1.3", "level": 2, "description": "Test 3", "result": "FAIL", "details": "Failed"}
        ]
        compliance = {
            "total_checks": 3,
            "passed_checks": 1,
            "failed_checks": 2,
            "total_points": 8,
            "passed_points": 3,
            "percentage": 37.5
        }
        db.save_scan(mock_account_id, first_results, compliance)

        # Second scan - some remediated
        second_results = [
            {"id": "1.1", "level": 3, "description": "Test 1", "result": "PASS", "details": "Fixed"},
            {"id": "1.2", "level": 3, "description": "Test 2", "result": "PASS", "details": "Passed"},
            {"id": "1.3", "level": 2, "description": "Test 3", "result": "FAIL", "details": "Still failing"}
        ]
        compliance2 = {
            "total_checks": 3,
            "passed_checks": 2,
            "failed_checks": 1,
            "total_points": 8,
            "passed_points": 6,
            "percentage": 75.0
        }
        db.save_scan(mock_account_id, second_results, compliance2)

        remediated = db.get_remediated_checks()

        # Only 1.1 should be remediated (FAIL -> PASS)
        assert len(remediated) == 1
        assert "1.1" in remediated
        assert "1.2" not in remediated  # Was already passing
        assert "1.3" not in remediated  # Still failing
        db.close()

    def test_get_scan_history(self, temp_db_path, sample_check_results, sample_compliance, mock_account_id):
        """Test retrieving scan history."""
        db = BenchmarkDatabase(temp_db_path)

        # Save 5 scans
        for _ in range(5):
            db.save_scan(mock_account_id, sample_check_results, sample_compliance)

        # Get last 3
        history = db.get_scan_history(limit=3)

        assert len(history) == 3
        # Should be in reverse chronological order
        assert history[0]['scan_id'] > history[1]['scan_id']
        db.close()

    def test_get_trends(self, temp_db_path, sample_check_results, mock_account_id):
        """Test getting compliance trends over time."""
        db = BenchmarkDatabase(temp_db_path)

        # Save scans with improving compliance
        for i in range(3):
            compliance = {
                "total_checks": 10,
                "passed_checks": 5 + i,
                "failed_checks": 5 - i,
                "total_points": 20,
                "passed_points": 10 + i * 2,
                "percentage": 50.0 + i * 10
            }
            db.save_scan(mock_account_id, sample_check_results, compliance)

        trends = db.get_trends(days=7)

        assert len(trends['labels']) == 3
        assert len(trends['compliance']) == 3
        # Should show improving trend
        assert trends['compliance'][0] < trends['compliance'][-1]
        db.close()

    def test_get_check_history(self, temp_db_path, mock_account_id):
        """Test getting history for a specific check."""
        db = BenchmarkDatabase(temp_db_path)

        # Save multiple scans with varying results for check 1.1
        for i, result in enumerate(['FAIL', 'FAIL', 'PASS', 'PASS']):
            results = [
                {"id": "1.1", "level": 3, "description": "Test", "result": result, "details": f"Scan {i}"}
            ]
            compliance = {"total_checks": 1, "passed_checks": 1 if result == "PASS" else 0,
                         "failed_checks": 0 if result == "PASS" else 1, "total_points": 3,
                         "passed_points": 3 if result == "PASS" else 0, "percentage": 100 if result == "PASS" else 0}
            db.save_scan(mock_account_id, results, compliance)

        history = db.get_check_history("1.1")

        assert len(history) == 4
        assert history[0]['result'] == 'FAIL'
        assert history[-1]['result'] == 'PASS'
        db.close()

    def test_no_scans_returns_empty(self, temp_db_path):
        """Test that methods return None/empty when no scans exist."""
        db = BenchmarkDatabase(temp_db_path)

        assert db.get_latest_scan() is None
        assert db.get_previous_scan() is None
        assert db.get_remediated_checks() == []
        assert db.get_scan_history() == []
        db.close()
