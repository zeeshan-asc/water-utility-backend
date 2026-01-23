"""
Documentation trainer service for Vanna AI.
Handles training with business documentation and column descriptions.

Follows Single Responsibility Principle by focusing solely on documentation training.
"""

import logging
from typing import Optional
from ..core.training_interface import BaseTrainer


class DocumentationTrainer(BaseTrainer):
    """
    Trainer for business documentation and column descriptions.
    
    This class handles training Vanna AI with business context and documentation.
    """
    
    def __init__(self, documentation: Optional[str] = None) -> None:
        """
        Initialize the documentation trainer.
        
        Args:
            documentation: Optional documentation string. If None, generates default documentation.
        """
        super().__init__()
        self.logger = logging.getLogger(__name__)
        self.documentation = documentation
    
    def generate_documentation(self) -> str:
        """
        Generate natural language documentation for water utility database.
        
        Returns:
            str: Natural language documentation for Vanna training
        """
        return """
Water Utility Database Documentation

This database contains financial and operational data for water utility management.

Main Tables:
1. water_data - Core financial and operational metrics by date
   - Financial metrics: actual_revenue, budgeted_revenue, revenue_variance, operating_margin
   - Operational metrics: days_sales_outstanding, non_revenue_water_pct, cost_per_gallon, collection_rate
   - Debt metrics: debt_service_coverage, outstanding_debt, projected_coverage, required_minimum, actual_coverage
   - Monthly metrics: monthly_revenue, monthly_expenses, monthly_margin
   - Accounts receivable: total_ar, current_pct, days_30_pct, days_60_pct
   - Other: water_revenue, cash_reserve

2. departments - Department-level budget vs actual spending
   - Columns: date, department, budget, actual, variance, variance_pct
   - Departments include: Operations, Infrastructure, Commercial, Technology, Utilities

3. alerts - System-generated alerts and forecasts
   - Columns: date, alert_type, description, potential_impact_k, confidence_level
   - Alert types include: Q1 Profitability Forecast, Cost Optimization Opportunity, Revenue Optimization Opportunity

4. scenarios - Financial scenario projections
   - Columns: date, scenario, projected_revenue, projected_expenses, debt_service_coverage, net_income, financial_viability
   - Scenarios include: Base Case, Rate Increase, Water Loss Reduction

Key Metrics:
- Revenue Variance = actual_revenue - budgeted_revenue (negative means under budget)
- Operating Margin = operating_margin (decimal, e.g., 0.17 = 17%)
- Non-Revenue Water % = percentage of water lost/unaccounted for
- Debt Service Coverage = ability to cover debt payments (higher is better, typically > 1.25)
- Collection Rate = percentage of billed amounts collected
- Days Sales Outstanding = average days to collect payment

Date Format:
- Dates are stored as TEXT in 'YYYY-MM-DD' format
- Use date LIKE '2024%' to filter by year
- Use date >= '2024-01-01' AND date <= '2024-12-31' for date ranges

Common Query Patterns:
- Revenue analysis: SUM(actual_revenue) GROUP BY year/quarter
- Budget variance: Compare actual vs budgeted_revenue
- Department spending: Join departments table with water_data on date
- Trend analysis: ORDER BY date to see trends over time
- Filtering: Use WHERE year = X or WHERE quarter = 'Q1'
"""
    
    def validate_documentation(self, documentation: str) -> bool:
        """
        Validate that the documentation content is suitable for training.
        
        Args:
            documentation: The documentation content to validate
            
        Returns:
            bool: True if valid, False otherwise
        """
        if not documentation or not documentation.strip():
            self.logger.error("Documentation content is empty")
            return False
        
        # Check minimum length (should be substantial documentation)
        if len(documentation) < 500:
            self.logger.warning("Documentation seems quite short - may not provide sufficient context")
        
        return True
    
    def train(self, vanna_instance) -> bool:
        """
        Train the Vanna instance with documentation data.
        
        Args:
            vanna_instance: The Vanna AI instance to train
            
        Returns:
            bool: True if training was successful, False otherwise
        """
        try:
            # Validate Vanna instance
            if not self.validate_vanna_instance(vanna_instance):
                self.logger.error("Invalid Vanna instance provided")
                return False
            
            # Generate or use provided documentation
            if self.documentation:
                documentation = self.documentation
            else:
                documentation = self.generate_documentation()
            
            # Validate documentation
            if not self.validate_documentation(documentation):
                return False
            
            # Train Vanna with documentation
            self.logger.info("Training Vanna with documentation data...")
            vanna_instance.add_documentation(documentation)
            
            self.logger.info("Documentation training completed successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Error during documentation training: {e}")
            return False
    
    def get_training_data_type(self) -> str:
        """
        Get the type of training data this trainer handles.
        
        Returns:
            str: The training data type identifier
        """
        return "documentation"
    
    def set_documentation(self, documentation: str) -> None:
        """
        Set custom documentation.
        
        Args:
            documentation: Documentation string
        """
        self.documentation = documentation
        self.logger.info("Documentation updated")




