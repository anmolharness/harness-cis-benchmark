"""Data models for CIS benchmark checks."""
from dataclasses import dataclass
from typing import Literal, Optional


@dataclass
class CheckResult:
    """Result of a single CIS benchmark check."""
    id: str
    level: Literal[1, 2, 3]
    description: str
    result: Literal["PASS", "FAIL", "ERROR", "MANUAL", "REMEDIATED"]
    details: str
    remediated: bool = False

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "id": self.id,
            "level": self.level,
            "description": self.description,
            "result": self.result,
            "details": self.details
        }


@dataclass
class ComplianceScore:
    """Overall compliance score."""
    passed_points: int
    total_points: int
    percentage: float
    passed_checks: int
    failed_checks: int
    total_checks: int

    def __str__(self) -> str:
        return f"{self.passed_points}/{self.total_points} ({self.percentage:.1f}%)"
