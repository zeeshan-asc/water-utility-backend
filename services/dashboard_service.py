"""
Dashboard Service Layer

This service handles all business logic for dashboard data operations.
Follows SOLID principles with single responsibility for each method.
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import pandas as pd
from pathlib import Path

logger = logging.getLogger('aquasentinel.api')


class DashboardService:
    """
    Service class for dashboard data operations.
    
    Principles:
    - Single Responsibility: Each method handles one specific data operation
    - Dependency Inversion: Depends on data file abstraction
    """
    
    def __init__(self):
        """Initialize the dashboard service."""
        self.logger = logger
        self.data_dir = Path(__file__).parent.parent / "data"
        # Initialize cache
        self._cache = {}
        self._cache_timestamps = {}
        # Cache duration: 5 minutes for most endpoints
        self._cache_duration = timedelta(minutes=5)
        self._load_data()
    
    def _load_data(self):
        """Load single CSV data file into memory."""
        try:
            # Load single unified CSV file (like utmb-backend)
            self.main_data = pd.read_csv(self.data_dir / 'data.csv')
            self.main_data['date'] = pd.to_datetime(self.main_data['date'])
            
            
            # Parse JSON columns for nested data (more efficient approach)
            import json
            
            # Parse departments JSON column
            if 'departments' in self.main_data.columns:
                departments_list = []
                for _, row in self.main_data.iterrows():
                    depts = json.loads(row['departments']) if pd.notna(row['departments']) else []
                    for dept in depts:
                        dept['date'] = row['date']
                        departments_list.append(dept)
                self.departments_data = pd.DataFrame(departments_list)
                if not self.departments_data.empty:
                    self.departments_data['date'] = pd.to_datetime(self.departments_data['date'])
                else:
                    # Initialize empty DataFrame with required columns
                    self.departments_data = pd.DataFrame(columns=['date', 'department', 'budget', 'actual', 'variance', 'variance_pct'])
            else:
                # Initialize empty DataFrame if column doesn't exist
                self.departments_data = pd.DataFrame(columns=['date', 'department', 'budget', 'actual', 'variance', 'variance_pct'])
            
            # Parse alerts JSON column
            if 'alerts' in self.main_data.columns:
                alerts_list = []
                for _, row in self.main_data.iterrows():
                    alerts = json.loads(row['alerts']) if pd.notna(row['alerts']) else []
                    for alert in alerts:
                        alert['date'] = row['date']
                        alerts_list.append(alert)
                self.alerts_data = pd.DataFrame(alerts_list)
                if not self.alerts_data.empty:
                    self.alerts_data['date'] = pd.to_datetime(self.alerts_data['date'])
                else:
                    # Initialize empty DataFrame with required columns
                    self.alerts_data = pd.DataFrame(columns=['date', 'alert_type', 'description', 'potential_impact_k', 'confidence_level'])
            else:
                # Initialize empty DataFrame if column doesn't exist
                self.alerts_data = pd.DataFrame(columns=['date', 'alert_type', 'description', 'potential_impact_k', 'confidence_level'])
            
            # Parse scenarios JSON column
            if 'scenarios' in self.main_data.columns:
                scenarios_list = []
                for _, row in self.main_data.iterrows():
                    scenarios = json.loads(row['scenarios']) if pd.notna(row['scenarios']) else []
                    for scenario in scenarios:
                        scenario['date'] = row['date']
                        scenarios_list.append(scenario)
                self.scenarios_data = pd.DataFrame(scenarios_list)
                if not self.scenarios_data.empty:
                    self.scenarios_data['date'] = pd.to_datetime(self.scenarios_data['date'])
                else:
                    # Initialize empty DataFrame with required columns
                    self.scenarios_data = pd.DataFrame(columns=['date', 'scenario', 'projected_revenue', 'projected_expenses', 'debt_service_coverage', 'net_income', 'financial_viability'])
            else:
                # Initialize empty DataFrame if column doesn't exist
                self.scenarios_data = pd.DataFrame(columns=['date', 'scenario', 'projected_revenue', 'projected_expenses', 'debt_service_coverage', 'net_income', 'financial_viability'])
            
            self.logger.info("Dashboard data loaded successfully from single CSV file")
        except Exception as e:
            self.logger.error(f"Error loading dashboard data: {str(e)}")
            raise
    
    def _get_from_cache(self, cache_key: str) -> Optional[Any]:
        """Get data from cache if it exists and is fresh."""
        if cache_key in self._cache:
            if datetime.now() - self._cache_timestamps[cache_key] < self._cache_duration:
                self.logger.debug(f"Cache HIT for key: {cache_key}")
                return self._cache[cache_key]
            else:
                self.logger.debug(f"Cache EXPIRED for key: {cache_key}")
                del self._cache[cache_key]
                del self._cache_timestamps[cache_key]
        return None
    
    def _set_cache(self, cache_key: str, data: Any) -> None:
        """Store data in cache with timestamp."""
        self._cache[cache_key] = data
        self._cache_timestamps[cache_key] = datetime.now()
        self.logger.debug(f"Cache SET for key: {cache_key}")
    
    def get_financial_kpis(self) -> Dict[str, Any]:
        """
        Get current financial KPIs for the dashboard header.
        Uses caching to improve performance.
        
        Returns:
            Dictionary containing all financial KPIs with changes
        """
        cache_key = "financial_kpis"
        
        # Check cache first
        cached_data = self._get_from_cache(cache_key)
        if cached_data is not None:
            return cached_data
        
        self.logger.info("Generating financial KPIs (cache miss)")
        
        try:
            # Get latest data
            latest = self.main_data.iloc[-1]
            previous = self.main_data.iloc[-2]
            
            # Calculate year-to-date revenue
            current_year = latest['year']
            ytd_data = self.main_data[self.main_data['year'] == current_year]
            annual_revenue = ytd_data['actual_revenue'].sum()
            
            # Calculate changes
            margin_change = ((latest['operating_margin'] - previous['operating_margin']) / previous['operating_margin']) * 100
            dso_change = ((latest['days_sales_outstanding'] - previous['days_sales_outstanding']) / previous['days_sales_outstanding']) * 100
            nrw_change = ((latest['non_revenue_water_pct'] - previous['non_revenue_water_pct']) / previous['non_revenue_water_pct']) * 100
            cost_change = ((latest['cost_per_gallon'] - previous['cost_per_gallon']) / previous['cost_per_gallon']) * 100
            collection_change = ((latest['collection_rate'] - previous['collection_rate']) / previous['collection_rate']) * 100
            
            result = {
                # Return as decimals (0.199) since frontend multiplies by 100 to get percentages
                # Frontend expects decimals and will multiply by 100, so we return raw decimal values
                "operating_margin": round(latest['operating_margin'], 4),  # 0.1994 -> frontend will show 19.94%
                "days_sales_outstanding": int(latest['days_sales_outstanding']),
                "non_revenue_water_pct": round(latest['non_revenue_water_pct'], 4),  # 0.2010 -> frontend will show 20.10%
                "cost_per_gallon": round(latest['cost_per_gallon'], 2),
                "collection_rate": round(latest['collection_rate'], 4),  # 0.9516 -> frontend will show 95.16%
                "annual_revenue": round(annual_revenue, 1),
                "water_revenue": round(latest['water_revenue'], 1),
                "cash_reserve": round(latest['cash_reserve'], 1),
                "debt_service_coverage": round(latest['debt_service_coverage'], 1),
                "operating_margin_change": f"{'+' if margin_change > 0 else ''}{round(margin_change, 1)}%",
                "dso_change": f"{'+' if dso_change > 0 else ''}{round(dso_change, 1)}%",
                "nrw_change": f"{'+' if nrw_change > 0 else ''}{round(nrw_change, 1)}%",
                "cost_per_gallon_change": f"{'+' if cost_change > 0 else ''}{round(cost_change, 1)}%",
                "collection_rate_change": f"{'+' if collection_change > 0 else ''}{round(collection_change, 1)}%"
            }
            
            # Cache the result
            self._set_cache(cache_key, result)
            return result
        except Exception as e:
            self.logger.error(f"Error generating financial KPIs: {str(e)}")
            raise
    
    def get_revenue_summary(self) -> Dict[str, Any]:
        """
        Get revenue performance summary with variance analysis.
        Uses caching to improve performance.
        
        Returns:
            Dictionary containing revenue summary
        """
        cache_key = "revenue_summary"
        
        # Check cache first
        cached_data = self._get_from_cache(cache_key)
        if cached_data is not None:
            return cached_data
        
        self.logger.info("Generating revenue summary (cache miss)")
        
        try:
            # Get latest quarter data
            latest_quarter = self.main_data[self.main_data['quarter'] == self.main_data.iloc[-1]['quarter']]
            
            actual = latest_quarter['actual_revenue'].sum()
            budgeted = latest_quarter['budgeted_revenue'].sum()
            variance = actual - budgeted
            variance_pct = (variance / budgeted) * 100
            
            result = {
                "actual_revenue": round(actual, 1),
                "budgeted_revenue": round(budgeted, 1),
                "variance": round(variance, 1),
                "variance_pct": round(variance_pct, 1),
                "status": "positive" if variance > 0 else "negative"
            }
            
            # Cache the result
            self._set_cache(cache_key, result)
            return result
        except Exception as e:
            self.logger.error(f"Error generating revenue summary: {str(e)}")
            raise
    
    def get_revenue_trends(self, start_date: Optional[str] = None, 
                          end_date: Optional[str] = None,
                          period: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get revenue trends over time for charting.
        
        Args:
            start_date: Optional start date filter
            end_date: Optional end date filter
            period: Optional period aggregation (monthly/quarterly/yearly)
            
        Returns:
            List of dictionaries with revenue trend data
        """
        self.logger.info(f"Generating revenue trends - period: {period}")
        
        try:
            df = self.main_data.copy()
            
            # Filter by date range if provided
            if start_date:
                df = df[df['date'] >= pd.to_datetime(start_date)]
            if end_date:
                df = df[df['date'] <= pd.to_datetime(end_date)]
            
            # Aggregate by period
            if period == 'quarterly':
                df = df.groupby(['year', 'quarter']).agg({
                    'actual_revenue': 'sum',
                    'budgeted_revenue': 'sum',
                    'revenue_variance': 'sum'
                }).reset_index()
                df['period'] = df['year'].astype(str) + '-' + df['quarter']
            elif period == 'yearly':
                df = df.groupby('year').agg({
                    'actual_revenue': 'sum',
                    'budgeted_revenue': 'sum',
                    'revenue_variance': 'sum'
                }).reset_index()
                df['period'] = df['year'].astype(str)
            else:
                # Monthly aggregation - group by year-month and sum
                df['period'] = df['date'].dt.strftime('%Y-%m')
                df = df.groupby('period').agg({
                    'actual_revenue': 'sum',
                    'budgeted_revenue': 'sum',
                    'revenue_variance': 'sum'
                }).reset_index()
            
            return df[['period', 'actual_revenue', 'budgeted_revenue', 'revenue_variance']].to_dict('records')
        except Exception as e:
            self.logger.error(f"Error generating revenue trends: {str(e)}")
            raise
    
    def get_budget_variance(self, department: Optional[str] = None, 
                           year: Optional[int] = None) -> Dict[str, Any]:
        """
        Get budget variance by department.
        
        Args:
            department: Optional department filter
            year: Optional year filter
            
        Returns:
            Dictionary containing budget variance data
        """
        self.logger.info(f"Generating budget variance - department: {department}, year: {year}")
        
        try:
            df = self.departments_data.copy()
            
            # Handle empty DataFrame
            if df.empty:
                return {
                    "summary": [],
                    "departments": []
                }
            
            if department:
                df = df[df['department'] == department]
            if year:
                df['year'] = pd.to_datetime(df['date']).dt.year
                df = df[df['year'] == year]
            
            # Get latest month for each department
            if df.empty:
                return {
                    "summary": [],
                    "departments": self.departments_data['department'].unique().tolist() if not self.departments_data.empty else []
                }
            
            latest_date = pd.to_datetime(df['date']).max()
            latest_data = df[pd.to_datetime(df['date']) == latest_date]
            
            return {
                "summary": latest_data.to_dict('records'),
                "departments": self.departments_data['department'].unique().tolist() if not self.departments_data.empty else []
            }
        except Exception as e:
            self.logger.error(f"Error generating budget variance: {str(e)}")
            raise
    
    def get_ar_aging(self) -> Dict[str, Any]:
        """
        Get current accounts receivable aging distribution.
        Uses caching to improve performance.
        
        Returns:
            Dictionary containing AR aging data
        """
        cache_key = "ar_aging"
        
        # Check cache first
        cached_data = self._get_from_cache(cache_key)
        if cached_data is not None:
            return cached_data
        
        self.logger.info("Generating AR aging data (cache miss)")
        
        try:
            latest = self.main_data.iloc[-1]
            
            result = {
                "current": {
                    "percentage": round(latest['current_pct'] * 100, 2),
                    "amount": round(latest['total_ar'] * latest['current_pct'], 2)
                },
                "days_30": {
                    "percentage": round(latest['days_30_pct'] * 100, 2),
                    "amount": round(latest['total_ar'] * latest['days_30_pct'], 2)
                },
                "days_60": {
                    "percentage": round(latest['days_60_pct'] * 100, 2),
                    "amount": round(latest['total_ar'] * latest['days_60_pct'], 2)
                },
                "total_ar": round(latest['total_ar'], 2)
            }
            
            # Cache the result
            self._set_cache(cache_key, result)
            return result
        except Exception as e:
            self.logger.error(f"Error generating AR aging: {str(e)}")
            raise
    
    def get_debt_metrics(self) -> Dict[str, Any]:
        """
        Get current debt sustainability metrics.
        Uses caching to improve performance.
        
        Returns:
            Dictionary containing debt metrics
        """
        cache_key = "debt_metrics"
        
        # Check cache first
        cached_data = self._get_from_cache(cache_key)
        if cached_data is not None:
            return cached_data
        
        self.logger.info("Generating debt metrics (cache miss)")
        
        try:
            latest = self.main_data.iloc[-1]
            
            result = {
                "debt_service_coverage": round(latest['debt_service_coverage'], 2),
                "projected_coverage": round(latest['projected_coverage'], 2),
                "actual_coverage": round(latest['actual_coverage'], 2),
                "required_minimum": round(latest['required_minimum'], 2),
                "outstanding_debt": round(latest['outstanding_debt'], 2),
                "status": "healthy" if latest['actual_coverage'] >= latest['required_minimum'] else "at_risk"
            }
            
            # Cache the result
            self._set_cache(cache_key, result)
            return result
        except Exception as e:
            self.logger.error(f"Error generating debt metrics: {str(e)}")
            raise
    
    def get_efficiency_alerts(self, alert_type: Optional[str] = None, 
                              limit: int = 10) -> Dict[str, Any]:
        """
        Get efficiency alerts and optimization opportunities.
        
        Args:
            alert_type: Optional alert type filter
            limit: Maximum number of alerts to return
            
        Returns:
            Dictionary containing alerts data
        """
        self.logger.info(f"Generating efficiency alerts - type: {alert_type}, limit: {limit}")
        
        try:
            df = self.alerts_data.copy()
            
            # Handle empty DataFrame
            if df.empty:
                return {
                    "alerts": [],
                    "alert_types": []
                }
            
            if alert_type:
                df = df[df['alert_type'] == alert_type]
            
            # Sort by date descending and confidence level
            df = df.sort_values(['date', 'confidence_level'], ascending=[False, False])
            df = df.head(limit)
            df['date_str'] = pd.to_datetime(df['date']).dt.strftime('%Y-%m-%d')
            
            return {
                "alerts": df[['date_str', 'alert_type', 'description', 
                             'potential_impact_k', 'confidence_level']].to_dict('records'),
                "alert_types": self.alerts_data['alert_type'].unique().tolist() if not self.alerts_data.empty else []
            }
        except Exception as e:
            self.logger.error(f"Error generating efficiency alerts: {str(e)}")
            raise
    
    def get_scenarios(self, year: Optional[int] = None) -> Dict[str, Any]:
        """
        Get scenario planning projections.
        
        Args:
            year: Optional year filter
            
        Returns:
            Dictionary containing scenario data
        """
        self.logger.info(f"Generating scenarios - year: {year}")
        
        try:
            df = self.scenarios_data.copy()
            
            # Handle empty DataFrame
            if df.empty:
                return {
                    "scenarios": [],
                    "scenario_types": []
                }
            
            if year:
                df['year'] = pd.to_datetime(df['date']).dt.year
                df = df[df['year'] == year]
            
            # Get latest projections for each scenario
            if df.empty:
                return {
                    "scenarios": [],
                    "scenario_types": self.scenarios_data['scenario'].unique().tolist() if not self.scenarios_data.empty else []
                }
            
            latest_date = pd.to_datetime(df['date']).max()
            latest_scenarios = df[pd.to_datetime(df['date']) == latest_date]
            
            return {
                "scenarios": latest_scenarios[['scenario', 'projected_revenue', 'projected_expenses',
                                             'debt_service_coverage', 'net_income', 'financial_viability']].to_dict('records'),
                "scenario_types": self.scenarios_data['scenario'].unique().tolist() if not self.scenarios_data.empty else []
            }
        except Exception as e:
            self.logger.error(f"Error generating scenarios: {str(e)}")
            raise

