# Production Database Specification (Aiven)

This document records the configuration and capabilities of the production Aiven PostgreSQL instance as of 2026-02-03.

## Core Information
- **Engine**: PostgreSQL 17.7
- **Host**: Aiven Cloud
- **Plan**: Free Tier (AWS US-East-1)
- **Max Connections**: 20
- **Storage/RAM**: ~1GB (as per Aiven Free Plan)

## Locale & Encoding
- **Encoding**: `UTF8`
- **Collation (`LC_COLLATE`)**: `en_US.UTF-8`
- **Character Type (`LC_CTYPE`)**: `en_US.UTF-8`
- **TimeZone**: `GMT`

## Extensions (Plugins)
Currently installed extensions:
- `plpgsql`: 1.0
- `vector`: 0.8.1 (pgvector)

## Local Development Alignment (pgserver)
- **Compatibility**: The project targets PostgreSQL 16.2 features to ensure compatibility between local development (`pgserver` 16.2) and production (Aiven 17.7). Developers must avoid PostgreSQL 17-exclusive syntax or features.
- **Extensions**: `pgvector` (vector) is now enabled in production. Local development environments using `pgserver` also support `pgvector` out of the box (as it is included in the wheels).
- **Data Integrity**: The use of `en_US.UTF-8` collation in production is standard. For SNEA linguistic data, custom NFD sorting is handled at the application level (SQLAlchemy/Python), so standard collation is sufficient.

## Schema
Tables currently defined (as of last inspection):
- (List was empty during inspection as Phase 3 migration is pending)
