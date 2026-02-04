<!-- Copyright (c) 2026 Brothertown Language -->
<!-- Licensed under CC BY-SA 4.0 -->

# Database Provider Comparison

> [!IMPORTANT]
> **Aiven** is the chosen and currently active database provider for this project. This document remains for historical context and technical justification.

This document provides a technical comparison between Supabase, Aiven, and Neon to justify the selection of Aiven for the SNEA Online Shoebox Editor.

## Comparison Matrix

| Feature | Supabase (Free Tier) | Neon (Free Tier) | Aiven (Free Plan) |
| :--- | :--- | :--- | :--- |
| **Connectivity** | **IPv6 Only** (IPv4 costs $10/mo) | IPv4 & IPv6 | **IPv4 & IPv6** |
| **Availability** | 24/7 (Always Awake) | **Cold Start** (Sleeps after 5m) | **24/7 (Always Awake)** |
| **RAM** | Shared / Unspecified | Up to **8 GB** (2 CU) | **1 GB (Dedicated)** |
| **CPU** | Shared | Up to **2 CU** (Shared) | **1 Virtual CPU (Dedicated)** |
| **Storage** | 500 MB | 0.5 GB | **1 GB (SSD)** |
| **PostgreSQL** | PostgreSQL 15 | PostgreSQL 16 | **PostgreSQL 17** |
| **Architecture** | BaaS (Postgres + Extras) | Serverless Postgres | Managed Postgres |
| **Features** | Auth, API, Edge Functions | Auth, Autoscaling, HA, Replicas | Monitoring, Backups |
| **Branching** | No | **Yes (Killer Feature)** | No |
| **Max Connections**| ~50-100 (Shared) | ~100 | **20** |
| **Usage Limit** | 24/7 (Project Pause) | **100 CU-hours/mo** | 24/7 (Unlimited) |

## Detailed Analysis

### 1. Connectivity (IPv4 vs IPv6)
- **Supabase**: Recently moved to IPv6-only for their free tier. Since Streamlit Community Cloud and many local development environments lack robust IPv6 routing, this creates significant connectivity barriers unless paying for a dedicated IPv4 address ($10/month).
- **Aiven & Neon**: Both provide native IPv4 support on their free tiers, ensuring seamless connectivity with Streamlit and local dev machines.

### 2. Performance (Cold Start)
- **Neon**: Uses a serverless model that "scales to zero." While cost-effective, it introduces a **3–5 second delay** (cold start) when the database is accessed after a period of inactivity. The free tier is also limited by **100 CU-hours per month**.
- **Aiven**: Provides a dedicated instance that remains running 24/7. There is **zero latency** on the first query of the day, which is critical for a smooth user experience in the SNEA Editor.

### 3. Resource Allocation (RAM/CPU/Storage)
- **Aiven** provides a robust, predictable resource allocation. While the storage limit is **1 GB**, it is dedicated to your service. For linguistic data (primarily text), 1GB of storage is still substantial for starting a project.

## Why Aiven was Chosen

Based on the requirements of the SNEA Shoebox Editor, **Aiven** was selected for the following reasons:

1.  **Zero-Cost IPv4**: Essential for reliable connectivity from Streamlit Cloud.
2.  **No Cold Starts**: Ensures the editor feels responsive even for the first user of the day.
3.  **Generous Resources**: 1GB RAM and 1GB storage on a dedicated VM are solid for free PostgreSQL hosting.
4.  **Simplicity**: Provides a standard, high-performance PostgreSQL environment without the complexity of a full Backend-as-a-Service (BaaS) like Supabase.

## Aiven Free Tier Details & Limitations

The Aiven Free Plan is available for PostgreSQL and other services indefinitely, without a credit card.

### Included Features:
- **PostgreSQL Version**: 17 (EOL: 8 November 2029).
- **Dedicated VM**: Single node with 1 CPU.
- **RAM**: 1 GB.
- **Storage**: 1 GB disk storage.
- **Uptime**: Always-on (24/7), no cold starts.
- **Maintenance**: Wednesdays after 06:10:45 UTC.
- **Monitoring**: Metrics and logs are included.
- **Backups**: Included.

### Limitations:
- **No VPC**: Cannot create the service in a Virtual Private Cloud.
- **No Static IPs**: IP addresses may change if the service is restarted.
- **No Connection Pooling**: `pgbouncer` is not available on the free tier.
- **Max Connections**: Limited to **20** connections.
- **No Forking**: Cannot fork the database for staging/testing.
- **No SLA**: Not covered under Aiven's 99.99% SLA.
- **No Support**: Only community support is available.
- **Usage Policy**: Aiven may shut down unused services (notifying you first), but they can be powered back on at any time.
