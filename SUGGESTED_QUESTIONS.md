# Suggested Questions for Testing AI/ML Endpoints

## Financial Performance Questions

### Revenue Analysis
1. **What was the total actual revenue in 2024?**
2. **Show me the revenue variance for each month in 2023**
3. **Which year had the highest total actual revenue?**
4. **What is the average monthly revenue for 2024?**
5. **Compare actual revenue vs budgeted revenue for Q1 2024**
6. **What was the revenue growth rate from 2022 to 2024?**
7. **Show me the monthly revenue trend for the last 6 months**

### Budget Variance
8. **Which months had the highest revenue variance?**
9. **What is the total budget variance for 2024?**
10. **Show me months where actual revenue exceeded budget by more than 15%**

## Operational Metrics

### Operating Margin
11. **What is the average operating margin for 2024?**
12. **Show me the operating margin trend over the last 12 months**
13. **Which quarter had the best operating margin?**

### Days Sales Outstanding (DSO)
14. **What is the average days sales outstanding for each year?**
15. **Show me months with DSO above 40 days**
16. **What is the DSO trend from 2022 to 2024?**

### Non-Revenue Water (NRW)
17. **What is the average non-revenue water percentage for 2024?**
18. **Show me months with non-revenue water above 24%**
19. **What is the NRW trend over the last 3 years?**

### Collection Rate
20. **Calculate the collection rate trend over the last 12 months**
21. **What is the average collection rate for 2024?**
22. **Show me months where collection rate was below 94%**

### Cost Metrics
23. **What is the average cost per gallon for each quarter?**
24. **Show me the cost per gallon trend for 2024**
25. **Which month had the highest cost per gallon?**

## Water Revenue

26. **What was the total water revenue in 2024?**
27. **Which months had the highest water revenue?**
28. **Show me the water revenue trend for Q2 2024**
29. **Compare water revenue vs actual revenue for 2024**

## Cash & Reserves

30. **What is the cash reserve trend over the last 12 months?**
31. **What was the cash reserve at the end of 2024?**
32. **Show me the cash reserve growth rate**

## Debt & Financial Health

### Debt Service Coverage Ratio (DSCR)
33. **Show me the debt service coverage ratio compared to required minimum**
34. **What is the average DSCR for 2024?**
35. **Which months had DSCR below 2.5x?**
36. **Show me the DSCR trend from 2022 to 2024**

### Outstanding Debt
37. **What is the total outstanding debt?**
38. **Show me the outstanding debt trend over time**
39. **What is the debt-to-revenue ratio for 2024?**

## Accounts Receivable (AR)

40. **What was the total accounts receivable for 2023?**
41. **Show me the AR aging breakdown (current, 30 days, 60+ days)**
42. **What percentage of AR is over 60 days old?**
43. **Show me months with high AR (above $1.3M)**

## Monthly Metrics

44. **Show me the monthly revenue and expenses for 2024**
45. **What is the average monthly margin for 2024?**
46. **Which months had negative monthly margin?**
47. **Show me the monthly expenses trend**

## Time-Based Queries

### By Year
48. **Compare total revenue across all years (2022, 2023, 2024)**
49. **What is the year-over-year revenue growth?**
50. **Show me the best performing year by operating margin**

### By Quarter
51. **What was the total revenue for Q1 2024?**
52. **Compare Q1 vs Q2 revenue for 2024**
53. **Which quarter had the highest revenue in 2023?**

### By Month
54. **Show me all data for January 2024**
55. **What was the revenue for the last month?**
56. **Compare January 2024 vs January 2023**

## Complex Analysis Questions

57. **Show me months where revenue exceeded budget AND operating margin was above 18%**
58. **What is the correlation between collection rate and days sales outstanding?**
59. **Show me the top 5 months by actual revenue**
60. **Which months had both high revenue variance and high DSO?**
61. **What is the average revenue per month for months with DSCR above 2.8?**
62. **Show me all metrics for the month with the highest operating margin**

## Summary & Aggregation Questions

63. **Give me a summary of financial performance for 2024**
64. **What are the key financial metrics for the last quarter?**
65. **Show me the overall financial health indicators**
66. **What is the total revenue, expenses, and margin for 2024?**

## Trend Analysis

67. **Show me the revenue trend over the last 3 years**
68. **What is the trend in operating margin from 2022 to 2024?**
69. **Show me how DSCR has changed over time**
70. **What is the trend in non-revenue water percentage?**

## Comparison Questions

71. **Compare 2023 vs 2024 revenue performance**
72. **How does Q1 2024 compare to Q1 2023?**
73. **Compare actual revenue vs budgeted revenue for all of 2024**
74. **Show me the difference between water revenue and actual revenue**

## Filtering & Conditional Questions

75. **Show me all months where operating margin was above 18%**
76. **Which months had collection rate below 94%?**
77. **Show me months with revenue variance greater than $0.4M**
78. **What are the months where DSCR was below the required minimum?**

---

## Testing Tips

### Test Different Question Formats
- Direct questions: "What was the revenue?"
- Comparison questions: "Compare X vs Y"
- Trend questions: "Show me the trend..."
- Summary questions: "Give me a summary..."

### Test Edge Cases
- Questions about dates that don't exist
- Questions with typos or unclear phrasing
- Questions requiring complex joins
- Questions about metrics that might not exist

### Test Natural Language Variations
- "What is..." vs "Show me..." vs "Give me..."
- "Total" vs "Sum" vs "Aggregate"
- "Average" vs "Mean"
- "Trend" vs "Over time" vs "Historical"

### Expected Behaviors
- Should generate valid SQL
- Should execute successfully
- Should return meaningful results
- Should handle edge cases gracefully

---

## Quick Test Script

You can use these questions with the test script:

```bash
python test_questions.py
```

Or test via API:

```bash
curl -X POST http://localhost:8084/api/v0/ai/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "What was the total actual revenue in 2024?"}'
```
