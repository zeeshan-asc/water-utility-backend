"""
SQL Query Validation Script for Training Data

This script validates all SQL queries in training_sql_data.json against the water_data.db database.
Follows SOLID principles with clear separation of concerns.

Usage:
    python validate_training_sql.py
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
from abc import ABC, abstractmethod
from datetime import datetime
import pandas as pd

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ============================================================================
# Data Models (Single Responsibility: Data representation)
# ============================================================================

@dataclass
class QueryPair:
    """Represents a question-SQL pair from training data."""
    question: str
    sql: str
    index: int


@dataclass
class ValidationResult:
    """Represents the result of validating a single query."""
    query_pair: QueryPair
    success: bool
    error_message: Optional[str] = None
    execution_time_ms: Optional[float] = None
    row_count: Optional[int] = None
    column_count: Optional[int] = None
    sample_data: Optional[List[Dict]] = None


@dataclass
class ValidationReport:
    """Represents the complete validation report."""
    total_queries: int
    passed_queries: int
    failed_queries: int
    results: List[ValidationResult]
    execution_start_time: datetime
    execution_end_time: Optional[datetime] = None


# ============================================================================
# Interface Definitions (Interface Segregation Principle)
# ============================================================================

class IQueryLoader(ABC):
    """Interface for loading SQL queries from a source."""
    
    @abstractmethod
    def load_queries(self) -> List[QueryPair]:
        """Load queries from the source."""
        pass


class IQueryExecutor(ABC):
    """Interface for executing SQL queries."""
    
    @abstractmethod
    def execute_query(self, sql: str) -> Tuple[bool, Optional[pd.DataFrame], Optional[str], float]:
        """
        Execute a SQL query.
        
        Returns:
            Tuple of (success, dataframe, error_message, execution_time_ms)
        """
        pass


class IQueryValidator(ABC):
    """Interface for validating query results."""
    
    @abstractmethod
    def validate(self, query_pair: QueryPair, result_df: pd.DataFrame) -> Tuple[bool, Optional[str]]:
        """
        Validate query results.
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        pass


class IReportGenerator(ABC):
    """Interface for generating validation reports."""
    
    @abstractmethod
    def generate_report(self, report: ValidationReport) -> str:
        """Generate a formatted report."""
        pass


# ============================================================================
# Concrete Implementations (Single Responsibility Principle)
# ============================================================================

class JSONQueryLoader(IQueryLoader):
    """Loads SQL queries from a JSON file."""
    
    def __init__(self, json_file_path: Path):
        """
        Initialize the JSON query loader.
        
        Args:
            json_file_path: Path to the JSON file containing query pairs
        """
        self.json_file_path = json_file_path
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    def load_queries(self) -> List[QueryPair]:
        """Load queries from JSON file."""
        try:
            self.logger.info(f"Loading queries from {self.json_file_path}")
            
            if not self.json_file_path.exists():
                raise FileNotFoundError(f"Training SQL file not found: {self.json_file_path}")
            
            with open(self.json_file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if not isinstance(data, list):
                raise ValueError("JSON file must contain a list of query pairs")
            
            queries = []
            for index, item in enumerate(data):
                if not isinstance(item, dict) or 'question' not in item or 'sql' not in item:
                    self.logger.warning(f"Skipping invalid item at index {index}")
                    continue
                
                queries.append(QueryPair(
                    question=item['question'],
                    sql=item['sql'],
                    index=index
                ))
            
            self.logger.info(f"Successfully loaded {len(queries)} queries")
            return queries
            
        except Exception as e:
            self.logger.error(f"Error loading queries: {e}")
            raise


class SQLiteQueryExecutor(IQueryExecutor):
    """Executes SQL queries against a SQLite database."""
    
    def __init__(self, db_path: Path):
        """
        Initialize the SQLite query executor.
        
        Args:
            db_path: Path to the SQLite database file
        """
        self.db_path = db_path
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        if not self.db_path.exists():
            raise FileNotFoundError(f"Database not found: {self.db_path}")
    
    def execute_query(self, sql: str) -> Tuple[bool, Optional[pd.DataFrame], Optional[str], float]:
        """
        Execute a SQL query against the database.
        
        Args:
            sql: SQL query to execute
            
        Returns:
            Tuple of (success, dataframe, error_message, execution_time_ms)
        """
        import time
        start_time = time.time()
        
        try:
            self.logger.debug(f"Executing query: {sql[:100]}...")
            
            with sqlite3.connect(str(self.db_path)) as conn:
                conn.row_factory = sqlite3.Row
                result_df = pd.read_sql_query(sql, conn)
            
            execution_time = (time.time() - start_time) * 1000  # Convert to milliseconds
            
            self.logger.debug(f"Query executed successfully in {execution_time:.2f}ms, returned {len(result_df)} rows")
            return True, result_df, None, execution_time
            
        except Exception as e:
            execution_time = (time.time() - start_time) * 1000
            error_msg = str(e)
            self.logger.error(f"Query execution failed: {error_msg}")
            return False, None, error_msg, execution_time


class BasicQueryValidator(IQueryValidator):
    """Validates query results with basic checks."""
    
    def __init__(self):
        """Initialize the basic query validator."""
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    def validate(self, query_pair: QueryPair, result_df: pd.DataFrame) -> Tuple[bool, Optional[str]]:
        """
        Validate query results with basic checks.
        
        Args:
            query_pair: The query pair being validated
            result_df: The result dataframe
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check if result is empty (this might be valid for some queries)
        if result_df.empty:
            self.logger.warning(f"Query {query_pair.index} returned empty result")
            # Empty results are valid - just a warning
        
        # Check for NaN values in critical columns (warning, not error)
        nan_columns = result_df.columns[result_df.isnull().any()].tolist()
        if nan_columns:
            self.logger.debug(f"Query {query_pair.index} has NaN values in columns: {nan_columns}")
        
        # Basic validation passed
        return True, None


class ComprehensiveQueryValidator(IQueryValidator):
    """Validates query results with comprehensive checks."""
    
    def __init__(self, require_non_empty: bool = False):
        """
        Initialize the comprehensive query validator.
        
        Args:
            require_non_empty: If True, empty results are considered invalid
        """
        self.require_non_empty = require_non_empty
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    def validate(self, query_pair: QueryPair, result_df: pd.DataFrame) -> Tuple[bool, Optional[str]]:
        """
        Validate query results with comprehensive checks.
        
        Args:
            query_pair: The query pair being validated
            result_df: The result dataframe
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check if result is empty
        if result_df.empty:
            if self.require_non_empty:
                return False, "Query returned empty result but non-empty result was expected"
            else:
                self.logger.warning(f"Query {query_pair.index} returned empty result")
        
        # Check for reasonable column count
        if len(result_df.columns) == 0:
            return False, "Query returned no columns"
        
        # Check for reasonable row count (warn if too many)
        if len(result_df) > 10000:
            self.logger.warning(f"Query {query_pair.index} returned {len(result_df)} rows - may be inefficient")
        
        # Validation passed
        return True, None


# ============================================================================
# Report Generator (Single Responsibility: Report formatting)
# ============================================================================

class TextReportGenerator(IReportGenerator):
    """Generates text-formatted validation reports."""
    
    def __init__(self, verbose: bool = True):
        """
        Initialize the text report generator.
        
        Args:
            verbose: If True, include detailed information for each query
        """
        self.verbose = verbose
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    def generate_report(self, report: ValidationReport) -> str:
        """
        Generate a formatted text report.
        
        Args:
            report: The validation report to format
            
        Returns:
            Formatted report string
        """
        lines = []
        lines.append("=" * 80)
        lines.append("SQL QUERY VALIDATION REPORT")
        lines.append("=" * 80)
        lines.append("")
        
        # Summary
        lines.append("SUMMARY")
        lines.append("-" * 80)
        lines.append(f"Total Queries: {report.total_queries}")
        lines.append(f"Passed: {report.passed_queries} ({report.passed_queries/report.total_queries*100:.1f}%)")
        lines.append(f"Failed: {report.failed_queries} ({report.failed_queries/report.total_queries*100:.1f}%)")
        
        if report.execution_end_time:
            duration = (report.execution_end_time - report.execution_start_time).total_seconds()
            lines.append(f"Execution Time: {duration:.2f} seconds")
        lines.append("")
        
        # Detailed results
        if self.verbose:
            lines.append("DETAILED RESULTS")
            lines.append("-" * 80)
            
            for result in report.results:
                status = "[PASS]" if result.success else "[FAIL]"
                lines.append(f"\n{status} Query #{result.query_pair.index + 1}")
                lines.append(f"  Question: {result.query_pair.question}")
                lines.append(f"  SQL: {result.query_pair.sql[:100]}...")
                
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
        
        # Failed queries summary
        failed_results = [r for r in report.results if not r.success]
        if failed_results:
            lines.append("")
            lines.append("FAILED QUERIES SUMMARY")
            lines.append("-" * 80)
            for result in failed_results:
                lines.append(f"\nQuery #{result.query_pair.index + 1}: {result.query_pair.question}")
                lines.append(f"  Error: {result.error_message}")
                lines.append(f"  SQL: {result.query_pair.sql}")
        
        lines.append("")
        lines.append("=" * 80)
        
        return "\n".join(lines)


# ============================================================================
# Validation Runner (Single Responsibility: Orchestration)
# ============================================================================

class SQLValidationRunner:
    """
    Orchestrates the SQL validation process.
    
    Follows Dependency Inversion Principle by depending on abstractions (interfaces)
    rather than concrete implementations.
    """
    
    def __init__(
        self,
        query_loader: IQueryLoader,
        query_executor: IQueryExecutor,
        query_validator: IQueryValidator,
        report_generator: IReportGenerator
    ):
        """
        Initialize the validation runner.
        
        Args:
            query_loader: Loader for SQL queries
            query_executor: Executor for SQL queries
            query_validator: Validator for query results
            report_generator: Generator for validation reports
        """
        self.query_loader = query_loader
        self.query_executor = query_executor
        self.query_validator = query_validator
        self.report_generator = report_generator
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    def run_validation(self) -> ValidationReport:
        """
        Run the complete validation process.
        
        Returns:
            ValidationReport with all results
        """
        self.logger.info("Starting SQL validation process...")
        start_time = datetime.now()
        
        # Load queries
        queries = self.query_loader.load_queries()
        
        # Validate each query
        results = []
        for query_pair in queries:
            self.logger.info(f"Validating query {query_pair.index + 1}/{len(queries)}: {query_pair.question[:60]}...")
            
            # Execute query
            success, result_df, error_message, execution_time = self.query_executor.execute_query(query_pair.sql)
            
            # Validate result if execution succeeded
            validation_success = success
            validation_error = error_message
            
            if success:
                validation_success, validation_error = self.query_validator.validate(query_pair, result_df)
            
            # Prepare sample data
            sample_data = None
            row_count = None
            column_count = None
            
            if success and result_df is not None:
                row_count = len(result_df)
                column_count = len(result_df.columns)
                if row_count > 0:
                    sample_data = result_df.head(1).to_dict('records')
            
            # Create validation result
            result = ValidationResult(
                query_pair=query_pair,
                success=validation_success and success,
                error_message=validation_error if not (validation_success and success) else None,
                execution_time_ms=execution_time,
                row_count=row_count,
                column_count=column_count,
                sample_data=sample_data
            )
            
            results.append(result)
            
            status = "PASS" if result.success else "FAIL"
            self.logger.info(f"  Query {query_pair.index + 1} {status} ({execution_time:.2f}ms)")
        
        end_time = datetime.now()
        
        # Create report
        report = ValidationReport(
            total_queries=len(queries),
            passed_queries=sum(1 for r in results if r.success),
            failed_queries=sum(1 for r in results if not r.success),
            results=results,
            execution_start_time=start_time,
            execution_end_time=end_time
        )
        
        self.logger.info(f"Validation completed: {report.passed_queries}/{report.total_queries} queries passed")
        
        return report


# ============================================================================
# Main Entry Point
# ============================================================================

def main() -> int:
    """Main entry point for the validation script."""
    try:
        # Configuration
        project_root = Path(__file__).resolve().parent
        json_file = project_root / "training_sql_data.json"
        db_file = project_root / "database" / "water_data.db"
        
        # Validate files exist
        if not json_file.exists():
            logger.error(f"Training SQL file not found: {json_file}")
            return 1
        
        if not db_file.exists():
            logger.error(f"Database file not found: {db_file}")
            return 1
        
        # Create components (Dependency Injection)
        query_loader = JSONQueryLoader(json_file)
        query_executor = SQLiteQueryExecutor(db_file)
        query_validator = ComprehensiveQueryValidator(require_non_empty=False)
        report_generator = TextReportGenerator(verbose=True)
        
        # Create runner
        runner = SQLValidationRunner(
            query_loader=query_loader,
            query_executor=query_executor,
            query_validator=query_validator,
            report_generator=report_generator
        )
        
        # Run validation
        report = runner.run_validation()
        
        # Generate and print report
        report_text = report_generator.generate_report(report)
        print(report_text)
        
        # Save report to file
        report_file = project_root / "sql_validation_report.txt"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report_text)
        logger.info(f"Report saved to: {report_file}")
        
        # Return exit code based on results
        return 0 if report.failed_queries == 0 else 1
        
    except Exception as e:
        logger.error(f"Validation failed with error: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)








