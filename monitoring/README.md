# Monitoring Setup for Typo Blog App

This directory contains the monitoring configuration for the Typo Blog application using Prometheus and Grafana.

## Files

- **prometheus.yml**: Prometheus scrape configuration for the deployed Azure Web App
- **docker-compose.monitoring.yml**: Docker Compose file to run Prometheus + Grafana locally
- **grafana-dashboard.json**: Pre-configured Grafana dashboard for visualizing app metrics

## Metrics Endpoints

The Typo Blog app exposes the following endpoints:

- **Health Check**: `https://sof-typo-webapp-2004.azurewebsites.net/health`
  - Returns: `{"status": "healthy", "uptime_seconds": <uptime>}`
  
- **Metrics**: `https://sof-typo-webapp-2004.azurewebsites.net/metrics`
  - Returns: Prometheus-formatted metrics including:
    - `typo_request_count_total`: Total number of HTTP requests by method, endpoint, and status
    - `typo_request_latency_seconds`: Request latency histogram
    - `typo_error_count_total`: Total error count
    - Standard Python/process metrics (CPU, memory, GC stats)

## Running Monitoring Stack Locally

To run Prometheus and Grafana locally to monitor your deployed Azure app:

```bash
# From the monitoring directory
cd monitoring
docker-compose -f docker-compose.monitoring.yml up -d
```

This will start:
- **Prometheus** on http://localhost:9090
- **Grafana** on http://localhost:3000 (credentials: admin/admin)

### Accessing Grafana

1. Open http://localhost:3000
2. Login with `admin` / `admin`
3. The Typo Blog dashboard should be automatically loaded
4. If not, import `grafana-dashboard.json` manually

### Accessing Prometheus

1. Open http://localhost:9090
2. Go to Status > Targets to verify the app is being scraped
3. Use the Graph tab to query metrics manually

## Example Prometheus Queries

```promql
# Request rate per second
rate(typo_request_count_total[5m])

# 95th percentile latency
histogram_quantile(0.95, rate(typo_request_latency_seconds_bucket[5m]))

# Error rate
rate(typo_request_count_total{http_status=~"5.."}[5m])

# Memory usage
process_resident_memory_bytes

# App uptime
(time() - process_start_time_seconds)
```

## Stopping the Monitoring Stack

```bash
docker-compose -f docker-compose.monitoring.yml down
```

To also remove volumes (all data):
```bash
docker-compose -f docker-compose.monitoring.yml down -v
```

## Production Deployment

For production monitoring:

1. Deploy Prometheus to a VM or container platform
2. Configure it to scrape the Azure Web App metrics endpoint
3. Set up Grafana with the provided dashboard
4. Configure alerting rules in Prometheus
5. Set up alert notifications in Grafana (email, Slack, etc.)

## Notes

- The current configuration scrapes metrics every 10 seconds
- Metrics retention is set to Prometheus defaults (15 days)
- The health endpoint is scraped every 30 seconds
- All metrics are labeled with app, instance, and region for filtering
