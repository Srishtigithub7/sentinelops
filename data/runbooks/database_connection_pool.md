# Database Connection Pool Runbook

## Symptom

API requests may become slow or return HTTP 503 errors when the
database connection pool is exhausted.

## Indicators

Look for:

- Database connection acquisition time above 1000ms
- Connection pool utilization above 90%
- "Failed to acquire database connection"
- "Database connection timeout"
- Connection pool utilization reaching 100%
- Increasing API latency
- Increasing HTTP 503 responses

## Investigation

1. Check database connection pool utilization.
2. Check active database connections.
3. Check recent application deployments.
4. Look for long-running database queries.
5. Check whether the latest deployment changed database usage.

## Recommended Actions

If the connection pool is exhausted:

1. Investigate the latest deployment.
2. Check for connection leaks.
3. Identify long-running queries.
4. Temporarily increase the connection pool if database capacity allows.
5. Roll back the latest deployment if the issue started immediately after deployment.

## Important

Do not blindly increase the connection pool size.

Verify database capacity first, because increasing connections
can overload the database server.