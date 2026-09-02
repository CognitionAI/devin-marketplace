# APM Performance Metrics Guide

Comprehensive guide to analyzing APM performance metrics.

## Error Rate Analysis

### Calculation
```
Error Rate = (Failed Requests / Total Requests) × 100%
```

### Interpretation
- **< 0.1%:** Excellent - minimal errors
- **0.1% - 1%:** Good - acceptable error rate
- **1% - 5%:** Warning - investigate error patterns
- **> 5%:** Critical - immediate attention required

### Investigation Steps
1. **Identify Error Types:**
   - HTTP status codes (4xx vs 5xx)
   - Exception classes and messages
   - Error distribution by transaction

2. **Temporal Analysis:**
   - When did errors start?
   - Is error rate increasing or stable?
   - Correlation with traffic patterns

3. **Segmentation:**
   - Which transactions have highest error rate?
   - Which hosts are generating errors?
   - Geographic or customer-specific patterns?

### Common Causes
- **4xx Errors:** Client-side issues (bad requests, authentication failures)
- **5xx Errors:** Server-side issues (application crashes, database failures)
- **Timeout Errors:** Slow dependencies, resource exhaustion
- **Connection Errors:** Network issues, service unavailability

## Response Time / Latency

### Key Percentiles
- **Average (mean):** Can be skewed by outliers, use with caution
- **Median (p50):** Typical user experience
- **p95:** 95% of requests faster than this
- **p99:** Catches outlier behavior, important for SLAs

### Interpretation
Response time targets vary by endpoint type:
- **API endpoints:** p95 < 200ms, p99 < 500ms
- **Page loads:** p95 < 1s, p99 < 2s
- **Background jobs:** Depends on job type

### Investigation Steps
1. **Identify Slow Transactions:**
   - Sort by average duration
   - Focus on p95/p99 for outliers
   - Check which transactions miss SLA

2. **Span Analysis:**
   - Break down transaction by span
   - Identify bottleneck (app code, DB, external service)
   - Calculate percentage of time in each span

3. **Pattern Detection:**
   - Consistent slowness vs intermittent spikes
   - Correlated with traffic load
   - Geographic patterns

### Optimization Strategies
- **Database Optimization:** Add indexes, optimize queries, use caching
- **Code Optimization:** Reduce algorithmic complexity, fix N+1 patterns
- **External Service Optimization:** Add timeouts, implement caching, use circuit breakers
- **Resource Scaling:** Increase CPU/memory, add more instances

## Throughput Analysis

### Calculation
```
Throughput = Requests per Minute (rpm)
```

### Interpretation
- **Increasing throughput:** Traffic growth, marketing campaigns
- **Decreasing throughput:** Errors blocking requests, performance degradation
- **Stable throughput:** Consistent load, capacity limits reached

### Investigation Steps
1. **Identify Patterns:**
   - Time-of-day patterns (business hours vs off-hours)
   - Day-of-week patterns (weekday vs weekend)
   - Seasonal patterns (holiday spikes)

2. **Capacity Analysis:**
   - Is throughput hitting infrastructure limits?
   - Are we rate-limited by dependencies?
   - Is autoscaling working correctly?

3. **Correlation:**
   - Does high throughput correlate with errors?
   - Does high throughput cause latency increase?
   - Are certain transactions consuming disproportionate capacity?

## Apdex Score

### Definition
Application Performance Index - user satisfaction metric
- **Satisfied:** Response time ≤ T (target threshold)
- **Tolerating:** Response time between T and 4T
- **Frustrated:** Response time > 4T or error

### Calculation
```
Apdex = (Satisfied + 0.5 × Tolerating) / Total Samples
```

### Interpretation
- **0.94 - 1.0:** Excellent
- **0.85 - 0.93:** Good
- **0.70 - 0.84:** Fair
- **0.50 - 0.69:** Poor
- **< 0.50:** Unacceptable

### Investigation Steps
1. **Identify Degrading Transactions:**
   - Which transactions have lowest Apdex?
   - Has Apdex changed recently?
   - Which transactions affect most users?

2. **Root Cause:**
   - High latency pushing users to Frustrated
   - Errors causing Frustrated categorization
   - Threshold (T) too aggressive

## Transaction Analysis Patterns

### N+1 Query Pattern
**Symptom:** Many database queries for single operation
**Detection:** High database span count in transaction trace
**Solution:** Use batch queries, eager loading, or caching

### Slow External Service Calls
**Symptom:** High external span duration
**Detection:** Analyze span breakdown
**Solution:** Add timeouts, implement caching, use circuit breakers

### Resource Contention
**Symptom:** Latency increases with load
**Detection:** Correlation between throughput and response time
**Solution:** Scale horizontally, optimize resource usage

### Memory Leaks
**Symptom:** Gradual performance degradation, increasing error rate
**Detection:** Memory usage trending upward over time
**Solution:** Profile application, fix leaks, add memory limits

## SLA Monitoring

### Define SLIs (Service Level Indicators)
- Error rate < 0.1%
- p95 response time < 200ms
- p99 response time < 500ms
- Availability > 99.9%

### Calculate SLO (Service Level Objective)
- "99.9% of requests must complete in < 200ms"
- "Error rate must be < 0.1% over 30-day window"

### Monitor Error Budget
- How much error budget is remaining?
- Is burn rate sustainable?
- Need to halt deployments?
