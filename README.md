# MAPA Backend

A comprehensive Python-based microservices architecture for MAPA, providing spatial data management, user authentication, API gateway functionality, and service integration capabilities.

## Overview

MAPA Backend is built using FastAPI and follows a microservices architecture pattern with shared libraries. The system supports multi-tenancy, provides comprehensive spatial/GIS functionality, and includes OAuth2/OIDC authentication with robust API management.

## Architecture

### 🏗️ Microservices (`apps/`)

- **`application/`** - Content page and application management service
- **`gateway/`** - API gateway with routing, parameter mapping, and integrations  
- **`manage/`** - User, organization, role, and client management service
- **`mock_app/`** - Mock service for testing and development
- **`runtime/`** - Runtime execution service with async task queues
- **`service/`** - Integration service handling HTTP, SOAP, spatial data, and functions
- **`spatial/`** - Spatial/GIS data management (maps, layers, connections)
- **`sso/`** - Single Sign-On service with OIDC/OAuth2 support

### 📚 Shared Libraries (`libs/`)

- **`core/`** - Base database, entity, repository, and service classes
- **`app/`** - Common FastAPI app utilities, security, and middleware
- **`manage/`, `gateway/`, `spatial/`, `service/`** - Domain-specific shared models
- **`test/`** - Test utilities and fixtures

## Features

- **Multi-tenant Architecture** - Complete tenant isolation with Row Level Security (RLS)
- **Spatial Data Management** - Full GIS capabilities with PostGIS integration
- **OAuth2/OIDC Authentication** - Comprehensive SSO with JWT tokens
- **API Gateway** - Centralized routing, parameter mapping, and service integration
- **Service Integration** - HTTP, SOAP, spatial services, and custom functions
- **Async Task Processing** - Background job execution with queue management
- **Microservices Communication** - Event-driven architecture with message bus
- **Comprehensive Testing** - Unit and integration tests across all services

## Quick Start

### Prerequisites

- Python 3.12+
- PostgreSQL with PostGIS extension
- Poetry for dependency management
- Redis (for caching and queues)

### Environment Setup

Each service uses Poetry for dependency management:

```bash
# Navigate to any service directory
cd apps/[service_name]  # or libs/[lib_name]

# Install dependencies
poetry install

# Activate virtual environment
poetry shell
```

### Running Services

Start individual services from their respective directories:

```bash
# From service directory (e.g., apps/spatial/)
uvicorn spatial.main:app --reload --port 8001

# Or for gateway service
uvicorn gateway.main:app --reload --port 8000
```

### Database Setup

Services using databases require Alembic migrations:

```bash
# From service directory with migrations
alembic upgrade head
```

## Development

### Bulk Dependency Updates

Update all Poetry dependencies across the project:

```bash
python tools/update_all.py
```

### Testing

Run tests from each service directory:

```bash
pytest                    # Run all tests
pytest tests/test_*.py    # Run specific test file
pytest -v                 # Verbose output
```

### Code Quality

```bash
pylint [service_name]/    # Run linting
```

## Configuration

Services use YAML-based configuration:
- `config.yml` - Base configuration
- `config.dev.yml` - Development environment
- `config.prod.yml` - Production environment

## Database Schema

- **PostgreSQL** with PostGIS for spatial data
- **Multi-tenant** with tenant-specific version tables
- **Entity-Repository-Service** pattern
- **Async SQLAlchemy** for database operations

## Service Communication

- **Gateway-centric** - All external communication through gateway
- **Message Bus** - Event-driven inter-service communication
- **REST APIs** - Standard HTTP/JSON interfaces
- **Dependency Injection** - Container-based service management

## Key Technologies

- **FastAPI** - Modern, fast web framework
- **SQLAlchemy** - Async ORM with PostgreSQL
- **PostGIS** - Spatial database extension
- **Alembic** - Database migration management
- **Poetry** - Dependency and package management
- **pytest** - Testing framework
- **RabbitMQ** - Message broker for async communication

## Service Responsibilities

| Service | Purpose |
|---------|---------|
| **Gateway** | Route requests, authentication, parameter mapping |
| **Manage** | User/organization management, permissions, invitations |
| **SSO** | Authentication, OAuth2/OIDC flows, token management |
| **Spatial** | GIS data, maps, layers, spatial queries and transformations |
| **Service** | Integration hub for external services and data processing |
| **Application** | Content management and application configuration |
| **Runtime** | Async task execution and background jobs |

## Documentation

Additional documentation available in `docs/`:
- Database migration guide
- Service-specific documentation
- API status codes reference
- Library usage guides

## License

[License information]

## Contributing

[Contributing guidelines]