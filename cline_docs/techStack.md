# Technology Stack Documentation

## Core Technologies

### Backend Framework

- **FastAPI** (Latest stable version)
  - High-performance Python web framework
  - Built-in async support
  - Automatic OpenAPI documentation
  - Data validation with Pydantic
  - Dependency injection system

### Programming Language

- **Python 3.x**
  - Modern Python features
  - Strong async support
  - Rich ecosystem of libraries
  - Type hinting capabilities

## Frontend Technologies

### Core Framework and Runtime

- **Bun**
  - JavaScript runtime and tooling
  - Built-in bundler and test runner
  - NPM-compatible package manager
  - TypeScript support out of the box

### UI Framework and Components

- **React with TypeScript**
  - Type-safe component development
  - Improved developer experience
  - Better error catching
  - Enhanced code maintainability

- **shadcn/ui**
  - Customizable component library
  - Tailwind CSS integration
  - Accessible components
  - Modern design system

### State Management

- **Jotai**
  - Atomic state management
  - TypeScript-first approach
  - Minimal boilerplate
  - React Suspense support

### Data Visualization

- **Recharts**
  - React-based charting library
  - Responsive design
  - Customizable components
  - TypeScript support

### Testing

- **Vitest**
  - Fast test runner
  - ESM-first approach
  - Compatible with Bun
  - Jest-like API

## Database

### Primary Database

- **SQLite**
  - File-based database
  - No separate server required
  - Suitable for initial development
  - Easy backup and version control
  - Potential future migration path to PostgreSQL

### Database Tools

- **SQLAlchemy**
  - SQL toolkit and ORM
  - Database abstraction layer
  - Schema management
  - Future migration support

- **Databases (python-databases)**
  - Async database support
  - SQLite compatibility
  - Integration with FastAPI

## HTTP and API

### HTTP Client

- **httpx**
  - Modern async HTTP client
  - HTTP/1.1 and HTTP/2 support
  - Connection pooling
  - Retry mechanisms
  - SSL/TLS support

### API Documentation

- **Swagger UI** (via FastAPI)
  - Interactive API documentation
  - Built-in testing interface
  - OpenAPI specification
  - Automatic schema generation

## Data Validation and Settings

### Validation Library

- **Pydantic**
  - Data validation using type annotations
  - Settings management
  - JSON schema generation
  - Integration with FastAPI

## Asynchronous Operations

### Concurrency Management

- **asyncio** (Python Standard Library)
  - Async/await syntax
  - Event loop management
  - Concurrent operations
  - Semaphore for rate limiting

### Rate Limiting

- Custom implementation using:
  - asyncio.Semaphore for concurrency control
  - Exponential backoff for retries
  - Request pooling

## Development Tools

### Version Control

- **Git**
  - Source code management
  - Feature branch workflow
  - Version tracking

### Code Quality

- **Type Hints**
  - Static type checking
  - Code documentation
  - IDE support

## Standard Library Utilities

### Core Utilities

- **json**: JSON data handling
- **os**: Operating system interactions
- **typing**: Type hint support
- **time**: Time-related functions

## Architecture Decisions

### Database Choice

- SQLite chosen for:
  - Simplicity of setup
  - File-based nature
  - Sufficient for initial scale
  - Easy development workflow

### API Design

- RESTful architecture
- JSON response format
- Pagination support
- Filtering capabilities
- Error handling standards

### Frontend Architecture

- Component-based structure
- Atomic state management with Jotai
- Type-safe data fetching
- Responsive design principles

### Concurrency Model

- Async-first approach
- Controlled concurrency
- Rate limit compliance
- Error resilience

## Future Considerations

### Potential Upgrades

- PostgreSQL migration path
- Authentication system
- Caching layer
- Performance monitoring
- API analytics

### Scalability Plans

- Database scaling strategy
- API request handling
- Concurrent user support
- Data volume management

## Development Environment and Execution

- A dedicated Python virtual environment is used to isolate dependencies.
- Use the "uv" command to invoke Python commands in Powershell on Windows.
- Ensure the virtual environment is activated prior to running backend services.
- Example command to start the backend:
  - uv run src/api/main.py
- The isolated environment ensures consistency and avoids dependency conflicts.
