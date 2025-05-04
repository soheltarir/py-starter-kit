# Python DDD Starter Kit

A comprehensive starter kit that demonstrates how to build scalable Python applications following Domain-Driven Design (DDD) principles with dependency injection. This template provides a solid foundation for building complex applications while maintaining clean architecture and separation of concerns.

## Project Structure

The project follows a Domain-Driven Design (DDD) architecture with a clear separation of concerns:

```
├── src/
│   ├── domain/          # Domain models, entities, value objects, and domain services
│   ├── application/     # Application services, use cases, and DTOs
│   ├── infrastructure/  # External services implementation, repositories, and adapters
│   ├── presentation/    # API controllers, CLI commands, and other interfaces
│   ├── observability/   # Monitoring, logging, and tracing implementations
│   └── utils/          # Common utilities and helpers
├── tests/              # Test suites
├── deployments/        # Deployment configurations and scripts
└── main.py            # Application entry point
```

### Layer Responsibilities

- **Domain Layer**: Contains the core business logic, entities, value objects, and domain services. This layer is independent of external concerns.
- **Application Layer**: Orchestrates the flow of data and implements use cases by coordinating domain objects.
- **Infrastructure Layer**: Provides implementations for interfaces defined in the domain layer and handles external concerns.
- **Presentation Layer**: Handles the presentation logic and converts data between the application layer and external formats.

## Features

- [x] Domain-Driven Design (DDD) architecture
- [x] Dependency Injection using Python-Dependency-Injector
- [x] Poetry for dependency management
- [x] Configuration Management using Pydantic Settings
- [x] Custom Logger
- [x] Unit test setup with pytest

### Presentation Layer

- [x] FastAPI as the REST presentation layer
- [ ] Model Context Protocol (MCP)
- [ ] WebSocket support
- [x] Background job processing using Celery

### Databases

- [x] MongoDB support using Beanie
- [ ] SQL support using SQLAlchemy
- [ ] SQL Database Migration management using Alembic
- [ ] Neo4j graph database
- [ ] Caching layer using Redis

## Getting Started

1. Clone this repository
2. Install Tool Dependencies
   1. **Poetry**: Dependency management - https://python-poetry.org/
   1. **Taskfile**: Task runner for development operations - https://taskfile.dev/
   2. **Docker**: Containerization https://www.docker.com/
2. Install python dependencies using Poetry:
   ```bash
   poetry install
   ```
3. Copy `.env.example` to `.env` and adjust the configuration
4. Run the application:
   ```bash
   poetry run python main.py
   ```

For all other available commands, run the following:
```shell
task -l
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
