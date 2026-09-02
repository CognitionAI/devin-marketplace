# NRQL Patterns Reference

Extended query patterns for the New Relic MCP skill. Load this file when the main SKILL.md
doesn't cover the specific query pattern needed.

---

## Table of Contents
1. [Aggregation Functions](#aggregation-functions)
2. [Advanced FACET Patterns](#advanced-facet-patterns)
3. [Subqueries](#subqueries)
4. [Infrastructure Queries](#infrastructure-queries)
5. [Kafka Queries](#kafka-queries)
6. [Log Queries](#log-queries)
7. [Distributed Tracing Queries](#distributed-tracing-queries)
8. [Custom Events](#custom-events)

---

## Aggregation Functions

```nrql
count(*)                              -- total event count
uniqueCount(attribute)                -- distinct values
average(attribute)                    -- mean
sum(attribute)                        -- total
min(attribute) / max(attribute)       -- extremes
percentile(duration, 50, 75, 95, 99)  -- distribution
rate(count(*), 1 minute)              -- events per time unit
stddev(attribute)                     -- standard deviation
histogram(duration, width:10, buckets:20)  -- latency histogram
latest(attribute)                     -- most recent value
earliest(attribute)                   -- oldest value
```

---

## Advanced FACET Patterns

**Multi-attribute FACET:**
```nrql
SELECT count(*) FROM TransactionError
FACET appName, error.class
SINCE 1 hour ago
```

**FACET CASES (custom bucketing):**
```nrql
SELECT count(*) FROM Transaction
FACET CASES(
  WHERE duration < 0.1 AS 'fast',
  WHERE duration < 0.5 AS 'ok',
  WHERE duration >= 0.5 AS 'slow'
)
SINCE 1 hour ago
```

**Limit FACET cardinality:**
```nrql
SELECT count(*) FROM Log
WHERE level = 'ERROR'
FACET message
SINCE 1 hour ago
LIMIT 25
```

---

## Subqueries

**Compare current vs. previous window:**
```nrql
SELECT average(duration) AS 'now',
       (SELECT average(duration) FROM Transaction SINCE 2 hours ago UNTIL 1 hour ago) AS 'prev'
FROM Transaction
SINCE 1 hour ago
```

**Filter with subquery result:**
```nrql
SELECT count(*) FROM Transaction
WHERE appName IN (
  SELECT uniques(appName) FROM TransactionError
  WHERE error.class = 'TimeoutException'
  SINCE 1 hour ago
)
SINCE 1 hour ago
```

---

## Infrastructure Queries

**Host CPU and memory:**
```nrql
SELECT average(cpuPercent), average(memoryUsedPercent)
FROM SystemSample
FACET hostname
SINCE 1 hour ago
TIMESERIES AUTO
```

**Disk I/O:**
```nrql
SELECT average(diskReadBytesPerSecond), average(diskWriteBytesPerSecond)
FROM SystemSample
FACET hostname
SINCE 30 minutes ago
```

**Network throughput:**
```nrql
SELECT sum(receiveBytesPerSecond), sum(transmitBytesPerSecond)
FROM NetworkSample
FACET hostname
SINCE 1 hour ago
TIMESERIES AUTO
```

**Process CPU top 10:**
```nrql
SELECT average(cpuPercent), average(memoryResidentSizeBytes)
FROM ProcessSample
FACET processDisplayName
SINCE 30 minutes ago
LIMIT 10
```

---

## Kafka Queries

**Consumer lag:**
```nrql
SELECT max(consumer_lag) FROM KafkaConsumerSample
FACET consumerGroup, topic
SINCE 30 minutes ago
TIMESERIES AUTO
```

**Producer throughput:**
```nrql
SELECT rate(sum(producer_message_rate), 1 minute)
FROM KafkaProducerSample
FACET clientId, topic
SINCE 1 hour ago
```

**Message latency p99:**
```nrql
SELECT percentile(request_latency_avg, 99)
FROM KafkaProducerSample
FACET topic
SINCE 1 hour ago
```

**Partition balance:**
```nrql
SELECT count(*) FROM KafkaBrokerSample
FACET broker, topic
SINCE 1 hour ago
```

---

## Log Queries

**Error log count by message:**
```nrql
SELECT count(*) FROM Log
WHERE level IN ('ERROR', 'CRITICAL')
FACET message
SINCE 1 hour ago
LIMIT 50
```

**Logs for a specific entity:**
```nrql
SELECT message, level, timestamp FROM Log
WHERE entity.guid = '<guid>'
ORDER BY timestamp DESC
SINCE 30 minutes ago
LIMIT 100
```

**Log trend over time:**
```nrql
SELECT count(*) FROM Log
WHERE level = 'ERROR'
TIMESERIES 5 minutes
SINCE 3 hours ago
```

**Search log text:**
```nrql
SELECT message FROM Log
WHERE message LIKE '%NullPointerException%'
SINCE 1 hour ago
LIMIT 50
```

---

## Distributed Tracing Queries

**Slowest spans by service:**
```nrql
SELECT average(duration.ms), count(*) FROM Span
WHERE service.name = 'checkout-api'
FACET name
SINCE 1 hour ago
LIMIT 20
```

**Database query duration:**
```nrql
SELECT average(duration.ms) AS 'Avg ms', count(*) AS 'Count'
FROM Span
WHERE category = 'datastore'
FACET db.statement
SINCE 1 hour ago
LIMIT 20
```

**External HTTP calls:**
```nrql
SELECT average(duration.ms), count(*) FROM Span
WHERE span.kind = 'client' AND http.url IS NOT NULL
FACET http.url
SINCE 1 hour ago
LIMIT 20
```

**Trace error rate:**
```nrql
SELECT percentage(count(*), WHERE otel.status_code = 'ERROR')
FROM Span
FACET service.name
SINCE 1 hour ago
```

---

## Custom Events

**Query your custom event type:**
```nrql
SELECT * FROM MyCustomEvent
WHERE environment = 'production'
SINCE 1 hour ago
LIMIT 20
```

**Funnel analysis:**
```nrql
SELECT funnel(session,
  WHERE step = 'view_product' AS 'Viewed',
  WHERE step = 'add_to_cart' AS 'Added to Cart',
  WHERE step = 'checkout' AS 'Checkout',
  WHERE step = 'purchase' AS 'Purchased'
)
FROM PageAction
SINCE 1 day ago
```