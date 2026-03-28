# Observability Standards

Observability is the ability to understand what your system is doing in production
without modifying it. If you can't answer "is it working?" and "why is it slow?" from
your dashboards and logs, your system is not observable.

The three pillars are **logs**, **metrics**, and **traces**.

---

## Logging

### What to Log

Log events that are meaningful for debugging and auditing:

- Service startup and shutdown (with config summary, no secrets)
- Incoming requests (method, path, status, duration, request ID)
- Outgoing calls to external services (target, duration, status)
- Business-significant events (user created, payment processed, job completed)
- Errors and warnings with full context (see error-handling standards)
- Background job start/end/failure

### What NOT to Log

- Passwords, tokens, API keys, session IDs
- PII: email addresses, names, phone numbers, IP addresses (unless legally required and protected)
- Full request/response bodies by default (too noisy; log only on error if needed)
- High-frequency events that would flood the log (e.g. every cache hit)

### Log Levels

| Level | Use for |
|-------|---------|
| `DEBUG` | Detailed diagnostic info — off in production by default |
| `INFO` | Normal operation events worth recording |
| `WARN` | Unexpected but handled situations (retry, fallback, deprecated usage) |
| `ERROR` | Unexpected failures that need attention |
| `FATAL` | System cannot continue; process must stop |

Don't over-warn. If a `WARN` fires constantly and no one acts on it, it trains people to ignore all warnings.

### Structured Logs

Use structured (JSON) logging, not free-form strings. Structured logs are queryable.

```json
{
  "level": "error",
  "timestamp": "2024-03-15T10:23:45Z",
  "request_id": "req-abc-123",
  "user_id": "usr-456",
  "op": "create_order",
  "error": "payment_declined",
  "duration_ms": 342
}
```

Every log entry should include: `timestamp`, `level`, `request_id` (for traceability).

---

## Health Checks

Every service that can be deployed must expose a health endpoint.

- **`/health` or `/healthz`**: Returns 200 if the process is running. Used by load balancers and orchestrators.
- **`/ready` or `/readyz`** (optional but recommended): Returns 200 only when the service is ready to handle traffic (DB connected, cache warm, etc.). Used for startup probes.

Keep health checks fast (< 100ms). Don't do heavy computation or slow DB queries in a health check.

---

## Metrics

Metrics answer "how much" and "how often" questions.

### The Four Golden Signals (start here)

1. **Latency** — How long do requests take? (track p50, p95, p99 — not just average)
2. **Traffic** — How many requests per second?
3. **Errors** — What percentage of requests are failing?
4. **Saturation** — How full is the system? (CPU, memory, queue depth, connection pool)

### Metric Types

| Type | Use for |
|------|---------|
| Counter | Things that only go up: requests served, errors, jobs completed |
| Gauge | Things that go up and down: active connections, queue depth, memory usage |
| Histogram | Distribution of values: request latency, payload size |

### Naming

Use consistent naming: `<service>_<subsystem>_<metric>_<unit>`

```
http_request_duration_seconds
db_query_duration_seconds
queue_depth_messages
cache_hit_total
cache_miss_total
```

---

## Distributed Tracing

Tracing shows you what happened across multiple services for a single request.
Add it when you have more than one service or async processing.

### Minimum Requirements

- Generate a unique **trace ID** at the entry point of each request
- Pass it through all downstream calls via headers (e.g. `X-Request-ID`, `traceparent`)
- Log the trace ID in every log line
- Include it in error responses so users can report it to support

### When to Add Full Distributed Tracing

When you have microservices and need to understand cross-service latency or failures,
instrument with a tracing library (OpenTelemetry is the standard). Don't over-engineer
this for a monolith — request IDs in logs are sufficient there.

---

## Alerting

Alerts should be **actionable**. An alert that fires and requires no human action
is noise — it trains people to ignore alerts.

### Alert on Symptoms, Not Causes

| Good (symptom) | Bad (cause) |
|----------------|-------------|
| Error rate > 1% for 5 minutes | Pod CPU > 80% |
| P99 latency > 2s | Memory usage rising |
| Payment success rate < 99% | Disk I/O elevated |

High CPU might be fine. High error rate is never fine. Alert on the user-visible impact.

### Alert Design Principles

- Every alert should have a runbook: "when this fires, do X first, then Y"
- Alerts should be rare enough that on-call engineers take them seriously
- Tune thresholds to eliminate false positives — a noisy alert is worse than no alert
- Group related alerts to avoid alert storms

---

## Anti-Patterns to Avoid

- **No logs in production**: You will be flying blind during incidents
- **Log-and-ignore**: Logging an error but not acting on it
- **Logging secrets**: A log aggregator is not a secrets vault
- **Alert on everything**: Leads to alert fatigue and ignored incidents
- **Average-only metrics**: Averages hide tail latency — always track percentiles
- **No request IDs**: Makes it impossible to correlate logs across a request lifecycle
- **Chatty debug logs in production**: Logging at DEBUG level in production floods the system and costs money
