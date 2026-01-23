"""
Validate Test Questions SQL Queries

This script validates all SQL queries in test_questions.json against the water_data.db database.
Similar to validate_training_sql.py but for test questions.
"""

import sys
import io

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

import json
import sqlite3
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import pandas as pd

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class TestResult:
    """Represents the result of validating a single test question."""
    question: str
    sql: str
    index: int
    success: bool
    error_message: Optional[str] = None
    execution_time_ms: Optional[float] = None
    row_count: Optional[int] = None
    column_count: Optional[int] = None
    sample_data: Optional[List[Dict]] = None


def validate_test_questions(json_file: Path, db_file: Path) -> List[TestResult]:
    """
    Validate all test questions against the database.
    
    Args:
        json_file: Path to test_questions.json
        db_file: Path to water_data.db
        
    Returns:
        List of TestResult objects
    """
    # Load test questions
    logger.info(f"Loading test questions from {json_file}")
    with open(json_file, 'r', encoding='utf-8') as f:
        questions = json.load(f)
    
    results = []
    
    # Validate each question
    for index, item in enumerate(questions):
        question = item.get('question', '')
        sql = item.get('sql', '')
        category = item.get('category', 'unknown')
        
        logger.info(f"Validating question {index + 1}/{len(questions)}: {question[:60]}...")
        
        # Execute SQL
        import time
        start_time = time.time()
        
        try:
            with sqlite3.connect(str(db_file)) as conn:
                conn.row_factory = sqlite3.Row
                result_df = pd.read_sql_query(sql, conn)
            
            execution_time = (time.time() - start_time) * 1000
            
            # Prepare sample data
            sample_data = None
            if len(result_df) > 0:
                sample_data = result_df.head(1).to_dict('records')
            
            result = TestResult(
                question=question,
                sql=sql,
                index=index,
                success=True,
                execution_time_ms=execution_time,
                row_count=len(result_df),
                column_count=len(result_df.columns),
                sample_data=sample_data
            )
            
            logger.info(f"  ✓ PASS ({execution_time:.2f}ms, {len(result_df)} rows)")
            
        except Exception as e:
            execution_time = (time.time() - start_time) * 1000
            error_msg = str(e)
            
            result = TestResult(
                question=question,
                sql=sql,
                index=index,
                success=False,
                error_message=error_msg,
                execution_time_ms=execution_time
            )
            
            logger.error(f"  ✗ FAIL ({execution_time:.2f}ms): {error_msg}")
        
        results.append(result)
    
    return results


def generate_report(results: List[TestResult]) -> str:
    """Generate a formatted validation report."""
    total = len(results)
    passed = sum(1 for r in results if r.success)
    failed = total - passed
    
    lines = []
    lines.append("=" * 80)
    lines.append("TEST QUESTIONS VALIDATION REPORT")
    lines.append("=" * 80)
    lines.append("")
    
    # Summary
    lines.append("SUMMARY")
    lines.append("-" * 80)
    lines.append(f"Total Questions: {total}")
    lines.append(f"Passed: {passed} ({passed/total*100:.1f}%)")
    lines.append(f"Failed: {failed} ({failed/total*100:.1f}%)")
    lines.append("")
    
    # Detailed results
    lines.append("DETAILED RESULTS")
    lines.append("-" * 80)
    
    for result in results:
        status = "[PASS]" if result.success else "[FAIL]"
        lines.append(f"\n{status} Question #{result.index + 1}")
        lines.append(f"  Question: {result.question}")
        lines.append(f"  SQL: {result.sql}")
        
        if result.success:
            lines.append(f"  Execution Time: {result.execution_time_ms:.2f}ms")
            lines.append(f"  Rows Returned: {result.row_count}")
            lines.append(f"  Columns Returned: {result.column_count}")
            
            if result.sample_data and len(result.sample_data) > 0:
                lines.append(f"  Sample Data (first row):")
                for key, value in result.sample_data[0].items():
                    lines.append(f"    {key}: {value}")
        else:
            lines.append(f"  Error: {result.error_message}")
            lines.append(f"  Execution Time: {result.execution_time_ms:.2f}ms")
    
    # Failed questions summary
    failed_results = [r for r in results if not r.success]
    if failed_results:
        lines.append("")
        lines.append("FAILED QUESTIONS SUMMARY")
        lines.append("-" * 80)
        for result in failed_results:
            lines.append(f"\nQuestion #{result.index + 1}: {result.question}")
            lines.append(f"  Error: {result.error_message}")
            lines.append(f"  SQL: {result.sql}")
    
    lines.append("")
    lines.append("=" * 80)
    
    return "\n".join(lines)


def main() -> int:
    """Main entry point."""
    try:
        project_root = Path(__file__).resolve().parent
        json_file = project_root / "test_questions.json"
        db_file = project_root / "database" / "water_data.db"
        
        # Validate files exist
        if not json_file.exists():
            logger.error(f"Test questions file not found: {json_file}")
            return 1
        
        if not db_file.exists():
            logger.error(f"Database file not found: {db_file}")
            return 1
        
        # Validate questions
        results = validate_test_questions(json_file, db_file)
        
        # Generate report
        report_text = generate_report(results)
        print(report_text)
        
        # Save report
        report_file = project_root / "test_questions_validation_report.txt"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report_text)
        logger.info(f"Report saved to: {report_file}")
        
        # Return exit code
        return 0 if all(r.success for r in results) else 1
        
    except Exception as e:
        logger.error(f"Validation failed: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)


