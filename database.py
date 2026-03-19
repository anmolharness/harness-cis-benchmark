"""SQLite database for storing scan results and tracking remediation."""
import os
import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

# Use /app/data in Docker, ./data locally
if os.path.exists('/app/data'):
    DATABASE_PATH = "/app/data/benchmark.db"
else:
    DATABASE_PATH = os.path.join(os.path.dirname(__file__), "data", "benchmark.db")


class BenchmarkDatabase:
    """Database manager for CIS benchmark results."""

    def __init__(self, db_path: str = DATABASE_PATH):
        self.db_path = db_path
        self._init_db()

    def _get_connection(self):
        """Get database connection."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        """Initialize database schema."""
        conn = self._get_connection()
        cursor = conn.cursor()

        # Scans table - stores each scan execution
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS scans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                account_id TEXT NOT NULL,
                total_checks INTEGER NOT NULL,
                passed_checks INTEGER NOT NULL,
                failed_checks INTEGER NOT NULL,
                total_points INTEGER NOT NULL,
                passed_points INTEGER NOT NULL,
                compliance_percentage REAL NOT NULL
            )
        """)

        # Check results table - stores individual check results
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS check_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                scan_id INTEGER NOT NULL,
                check_id TEXT NOT NULL,
                check_level INTEGER NOT NULL,
                description TEXT NOT NULL,
                result TEXT NOT NULL,
                details TEXT NOT NULL,
                FOREIGN KEY (scan_id) REFERENCES scans (id)
            )
        """)

        # Create indexes for faster queries
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_scan_timestamp
            ON scans(timestamp DESC)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_check_results_scan
            ON check_results(scan_id)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_check_results_check_id
            ON check_results(check_id)
        """)

        conn.commit()
        conn.close()
        logger.info("Database initialized")

    def save_scan(self, account_id: str, results: List[Dict[str, Any]],
                  compliance: Dict[str, Any]) -> int:
        """Save scan results to database."""
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            # Insert scan record
            cursor.execute("""
                INSERT INTO scans (
                    timestamp, account_id, total_checks, passed_checks,
                    failed_checks, total_points, passed_points, compliance_percentage
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                datetime.now().isoformat(),
                account_id,
                compliance['total_checks'],
                compliance['passed_checks'],
                compliance['failed_checks'],
                compliance['total_points'],
                compliance['passed_points'],
                compliance['percentage']
            ))

            scan_id = cursor.lastrowid

            # Insert check results
            for check in results:
                cursor.execute("""
                    INSERT INTO check_results (
                        scan_id, check_id, check_level, description, result, details
                    ) VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    scan_id,
                    check['id'],
                    check['level'],
                    check['description'],
                    check['result'],
                    check['details']
                ))

            conn.commit()
            logger.info(f"Saved scan {scan_id} with {len(results)} check results")
            return scan_id

        except Exception as e:
            conn.rollback()
            logger.error(f"Failed to save scan: {e}")
            raise
        finally:
            conn.close()

    def get_latest_scan(self) -> Optional[Dict[str, Any]]:
        """Get the most recent scan."""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT * FROM scans
            ORDER BY timestamp DESC
            LIMIT 1
        """)

        scan = cursor.fetchone()
        if not scan:
            conn.close()
            return None

        scan_id = scan['id']

        # Get check results
        cursor.execute("""
            SELECT * FROM check_results
            WHERE scan_id = ?
        """, (scan_id,))

        results = [dict(row) for row in cursor.fetchall()]
        conn.close()

        return {
            'scan': dict(scan),
            'results': results
        }

    def get_previous_scan(self) -> Optional[Dict[str, Any]]:
        """Get the second most recent scan (for comparison)."""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT * FROM scans
            ORDER BY timestamp DESC
            LIMIT 1 OFFSET 1
        """)

        scan = cursor.fetchone()
        if not scan:
            conn.close()
            return None

        scan_id = scan['id']

        cursor.execute("""
            SELECT * FROM check_results
            WHERE scan_id = ?
        """, (scan_id,))

        results = [dict(row) for row in cursor.fetchall()]
        conn.close()

        return {
            'scan': dict(scan),
            'results': results
        }

    def get_remediated_checks(self) -> List[str]:
        """Get list of check IDs that were remediated in the latest scan."""
        latest = self.get_latest_scan()
        previous = self.get_previous_scan()

        if not latest or not previous:
            return []

        remediated = []

        # Create lookup dicts
        latest_results = {r['check_id']: r['result'] for r in latest['results']}
        previous_results = {r['check_id']: r['result'] for r in previous['results']}

        # Find checks that changed from FAIL to PASS
        for check_id, current_result in latest_results.items():
            previous_result = previous_results.get(check_id)
            if previous_result == 'FAIL' and current_result == 'PASS':
                remediated.append(check_id)

        logger.info(f"Found {len(remediated)} remediated checks")
        return remediated

    def get_scan_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get historical scan summary."""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                id,
                timestamp,
                total_checks,
                passed_checks,
                failed_checks,
                compliance_percentage
            FROM scans
            ORDER BY timestamp DESC
            LIMIT ?
        """, (limit,))

        history = [dict(row) for row in cursor.fetchall()]
        conn.close()

        return history

    def get_check_history(self, check_id: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Get history for a specific check."""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                s.timestamp,
                cr.result,
                cr.details
            FROM check_results cr
            JOIN scans s ON cr.scan_id = s.id
            WHERE cr.check_id = ?
            ORDER BY s.timestamp DESC
            LIMIT ?
        """, (check_id, limit))

        history = [dict(row) for row in cursor.fetchall()]
        conn.close()

        return history

    def get_statistics(self) -> Dict[str, Any]:
        """Get database statistics."""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) as total_scans FROM scans")
        total_scans = cursor.fetchone()['total_scans']

        cursor.execute("""
            SELECT
                AVG(compliance_percentage) as avg_compliance,
                MIN(compliance_percentage) as min_compliance,
                MAX(compliance_percentage) as max_compliance
            FROM scans
        """)
        stats = dict(cursor.fetchone())
        stats['total_scans'] = total_scans

        conn.close()
        return stats
