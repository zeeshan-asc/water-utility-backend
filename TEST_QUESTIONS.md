# Test Questions for Vanna AI (Different from Training Data)

This document contains 20 test questions that are different from the training data to validate Vanna AI's ability to handle various query types and edge cases.

## Questions

1. **What is the minimum collection rate recorded in 2022?**
   - Tests: MIN aggregation, different year (2022)

2. **How many days in 2023 had operating margin below 15%?**
   - Tests: COUNT with filter, percentage threshold

3. **Show me the top 5 days with highest cash reserve in 2024**
   - Tests: TOP N query, ORDER BY DESC with LIMIT

4. **What is the total accounts receivable for Q2 2023?**
   - Tests: SUM aggregation, specific quarter

5. **Which month in 2022 had the lowest water revenue?**
   - Tests: MIN with GROUP BY month

6. **Calculate the percentage of days where debt service coverage exceeded 2.5 in 2024**
   - Tests: Percentage calculation, COUNT with condition

7. **Show me all records where revenue variance was negative in Q3 2023**
   - Tests: Negative value filter, specific quarter

8. **What is the difference between maximum and minimum cost per gallon in 2024?**
   - Tests: MAX - MIN calculation, range

9. **How many records exist for each quarter across all years?**
   - Tests: COUNT with GROUP BY quarter

10. **Show me dates where both collection rate was above 95% and operating margin was above 20%**
    - Tests: Multiple AND conditions

11. **What is the average days sales outstanding for Q4 2022?**
    - Tests: AVG aggregation, Q4 2022

12. **Which year had the highest average non-revenue water percentage?**
    - Tests: AVG with GROUP BY year, ORDER BY DESC

13. **Show me the 10 days with the lowest collection rate in 2023**
    - Tests: Bottom N query, ORDER BY ASC

14. **What was the total monthly expenses for all of 2022?**
    - Tests: SUM for entire year

15. **Calculate the ratio of actual revenue to budgeted revenue for each quarter in 2023**
    - Tests: Division calculation, GROUP BY quarter

16. **Show me records where cash reserve was between 3.5 and 5.0 million**
    - Tests: BETWEEN operator, range filter

17. **What is the median operating margin for 2024?**
    - Tests: Statistical function (may need approximation)

18. **How many days had outstanding debt above 7 million in 2023?**
    - Tests: COUNT with threshold filter

19. **Show me the revenue trend for the first 30 days of 2024**
    - Tests: Date range filter, ORDER BY date

20. **What is the standard deviation of collection rate for 2023?**
    - Tests: Statistical function (may need approximation)

## Usage

These questions can be tested using:

```bash
# Test individual question
python test_vanna_query.py

# Or use the validation script
python validate_training_sql.py
```

## Categories

- **Aggregation**: MIN, MAX, SUM, AVG, COUNT
- **Filtering**: WHERE clauses with various conditions
- **Grouping**: GROUP BY with different columns
- **Sorting**: ORDER BY ASC/DESC with LIMIT
- **Calculations**: Ratios, differences, percentages
- **Date Ranges**: Specific quarters, months, date ranges
- **Multiple Conditions**: AND/OR combinations
- **Statistical Functions**: Median, standard deviation


