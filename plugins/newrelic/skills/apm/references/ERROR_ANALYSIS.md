# Error Analysis Guide

Comprehensive guide for analyzing and diagnosing application errors.

## Error Classification

### HTTP Status Code Categories

**Client Errors (4xx):**
- **400 Bad Request:** Malformed request, validation error
- **401 Unauthorized:** Authentication required or failed
- **403 Forbidden:** Authenticated but not authorized
- **404 Not Found:** Resource doesn't exist
- **429 Too Many Requests:** Rate limit exceeded

**Server Errors (5xx):**
- **500 Internal Server Error:** Unhandled exception
- **502 Bad Gateway:** Upstream service error
- **503 Service Unavailable:** Service temporarily down
- **504 Gateway Timeout:** Upstream service timeout

### Error Severity Levels

**Critical:**
- Complete service outage
- Data loss or corruption
- Security breach

**High:**
- Core functionality broken
- Affecting many users
- SLA violation

**Medium:**
- Non-critical feature broken
- Affecting some users
- Workaround available

**Low:**
- Minor issue
- Affecting few users
- No SLA impact

## Error Investigation Process

### Step 1: Quantify the Problem
- What is the current error rate?
- How many users affected?
- Which transactions/endpoints?
- When did errors start?

### Step 2: Categorize Errors
- Group by error type/message
- Group by status code
- Group by transaction name
- Identify most frequent errors

### Step 3: Analyze Error Messages
- Read full error message and stack trace
- Identify exception type
- Locate error source (file and line number)
- Understand failure mode

### Step 4: Find Patterns
- Time-based patterns (time of day, specific times)
- Load-based patterns (errors under high load)
- User-based patterns (specific customers, regions)
- Input-based patterns (specific request parameters)

### Step 5: Trace Root Cause
- Review transaction traces with errors
- Check span timing before error
- Analyze database queries
- Review external service calls
- Check infrastructure logs

## Common Error Patterns

### Database Connection Errors
**Symptoms:**
- "Connection refused"
- "Too many connections"
- "Connection pool exhausted"

**Investigation:**
1. Check database availability and health
2. Review connection pool size vs load
3. Check for connection leaks (not closing connections)
4. Monitor concurrent connection count

**Solutions:**
- Increase connection pool size
- Fix connection leaks in application code
- Add connection timeouts
- Scale database if needed

### Timeout Errors
**Symptoms:**
- HTTP 504 Gateway Timeout
- "Read timeout"
- "Connection timeout"

**Investigation:**
1. Identify which service is timing out
2. Check response time of slow service
3. Review timeout configuration
4. Analyze load on slow service

**Solutions:**
- Increase timeout if legitimately slow operation
- Optimize slow service
- Implement retry logic with exponential backoff
- Add circuit breaker to fail fast

### Null Pointer / Reference Errors
**Symptoms:**
- NullPointerException (Java)
- AttributeError: 'NoneType' (Python)
- Cannot read property of null (JavaScript)

**Investigation:**
1. Read stack trace to find null object
2. Trace back to where object should be initialized
3. Check for missing data validation
4. Review recent code changes

**Solutions:**
- Add null checks and validation
- Use optional types or default values
- Improve error handling

### Resource Exhaustion
**Symptoms:**
- OutOfMemoryError
- "Disk full"
- "Too many open files"

**Investigation:**
1. Check resource usage trends
2. Look for memory leaks or disk space growth
3. Review resource limits
4. Identify resource-heavy operations

**Solutions:**
- Increase resource limits
- Fix memory/disk leaks
- Add resource cleanup code
- Implement resource pooling

### Dependency Failures
**Symptoms:**
- External API errors
- Database unavailable
- Message queue connection failed

**Investigation:**
1. Verify dependency health and availability
2. Check network connectivity
3. Review authentication/authorization
4. Look for rate limiting

**Solutions:**
- Implement circuit breaker pattern
- Add fallback behavior
- Cache responses when possible
- Monitor dependency SLAs

## Error Rate Spike Diagnosis

### Sudden Spike (immediate)
**Likely Causes:**
- Recent deployment with bugs
- Dependency outage
- Infrastructure failure
- DDoS or unusual traffic pattern

**Investigation:**
1. Check deployment timeline
2. Review dependency health
3. Check infrastructure alerts
4. Analyze traffic patterns

### Gradual Increase
**Likely Causes:**
- Memory leak causing progressive failure
- Data growth causing performance degradation
- Resource exhaustion over time
- Slow dependency degradation

**Investigation:**
1. Analyze error rate trend over time
2. Correlate with resource usage trends
3. Check data volume growth
4. Review long-running processes

### Intermittent Spikes
**Likely Causes:**
- Scheduled jobs causing load
- Retry storms
- Cache invalidation causing load spikes
- Time-based triggers

**Investigation:**
1. Identify spike timing pattern
2. Check for scheduled operations
3. Review retry logic and backoff
4. Analyze cache hit rates

## Error Resolution Strategies

### Quick Fixes
- Rollback recent deployment
- Restart failing services
- Scale up infrastructure
- Enable maintenance mode

### Short-term Solutions
- Apply hotfix for critical bugs
- Increase resource limits
- Add circuit breakers
- Implement rate limiting

### Long-term Solutions
- Refactor problematic code
- Improve error handling
- Add comprehensive monitoring
- Implement chaos engineering tests

## Error Monitoring Best Practices

### Alert on Error Rate
- Set baseline error rate threshold
- Alert on significant deviation
- Use anomaly detection
- Segment by critical vs non-critical endpoints

### Track Error Trends
- Monitor error rate over time
- Track by error type
- Segment by transaction and host
- Correlate with deployments

### Error Budget Management
- Define acceptable error rate (e.g., 0.1%)
- Track error budget consumption
- Pause deployments if budget exhausted
- Prioritize reliability work

### Post-Mortem Analysis
- Document incident timeline
- Identify root cause
- List contributing factors
- Define action items to prevent recurrence
