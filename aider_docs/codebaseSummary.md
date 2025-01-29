# Codebase Summary

## Key Components and Their Interactions

### 1. Data Extraction Component

- **Purpose:** Fetch item data from Blizzard API
- **Implemented Features:**
  - OAuth authentication with token management
  - Concurrent requests with semaphore control
  - Data transformation pipeline
  - Nested transaction handling
  - Automatic report generation (Markdown/JSON)
- **Key Interactions:**
  - Uses RateLimiter for API call management
  - Integrates with SQLAlchemy async sessions
  - Generates timestamped output reports

### 2. Database Layer

- **Purpose:** Store and manage item data
- **Key Files:** (To be implemented)
  - `database/models.py`: SQLAlchemy models
  - `database/schema.py`: Database schema definitions
  - `database/operations.py`: Database operations
- **Tables:**
  - `items`: Core item information
  - `groups`: User-defined item groups
  - `item_groups`: Junction table for items-groups relationship

### 3. REST API Component

- **Purpose:** Serve item data to clients
- **Key Files:** (To be implemented)
  - `api/main.py`: FastAPI application
  - `api/routes/`: API endpoint implementations
  - `api/models.py`: Pydantic models
- **Endpoints:**
  - Items endpoints
  - Item classes endpoints
  - Groups endpoints

## Data Flow

### 1. Data Ingestion Flow

```
Blizzard API → Rate Limiter → Data Extractor → SQLite Database
```

- Concurrent API requests managed by Semaphore
- Rate limiting with exponential backoff
- Data validation before storage

### 2. API Request Flow

```
Client Request → FastAPI Router → Database Query → JSON Response
```

- Request validation with Pydantic
- Optional filtering and pagination
- Error handling at each step

## External Dependencies

### 1. Blizzard API

- Item data source
- Rate limited access
- Requires API credentials

### 2. Third-Party Libraries

- FastAPI: Web framework
- httpx: HTTP client
- SQLAlchemy: Database ORM
- Pydantic: Data validation
- pytest: Testing framework

## Project Structure

```
project_root/
├── aider_docs/          # Project documentation
├── src/                 # Source code (to be implemented)
│   ├── extractor/      # Data extraction module
│   ├── database/       # Database module
│   └── api/            # REST API module
├── tests/              # Test files (to be implemented)
├── docs/               # Additional documentation
└── output/             # Extraction reports
```

## Recent Changes
- Completed core extraction workflow implementation:
  - Nested transactions for individual items
  - Exponential backoff with jitter in retries
  - Atomic batch processing with rollback
  - Detailed error tracking in reports
- Enhanced rate limiting:
  - Blizzard header-aware rate limiting
  - Dynamic concurrency adjustment
  - Header parsing for limit tracking
- Database improvements:
  - Async schema initialization
  - Environment-based configuration
  - Proper connection pooling

  ```
  project_root/
  ├── src/
  │   ├── extractor/
  │   │   ├── __init__.py
  │   │   ├── api_client.py
  │   │   ├── rate_limiter.py
  │   │   └── main.py
  │   ├── database/
  │   │   ├── __init__.py
  │   │   ├── models.py
  │   │   ├── schema.py
  │   │   └── operations.py
  │   └── api/
  │       ├── __init__.py
  │       ├── main.py
  │       ├── routes/
  │       └── models.py
  ├── tests/
  │   ├── __init__.py
  │   ├── test_extractor/
  │   ├── test_database/
  │   └── test_api/
  ├── docs/
  ├── aider_docs/
  └── output/
  ```

## Development Guidelines

### 1. Code Organization

- Modular structure
- Clear separation of concerns
- Comprehensive documentation

### 2. Testing Strategy

- Unit tests for each component
- Integration tests for workflows
- API endpoint testing

### 3. Error Handling

- Graceful API error handling
- Detailed error logging
- User-friendly error messages

## Future Development

### 1. Planned Improvements

- Database migration system
- Enhanced error reporting
- Performance optimizations
- Group management features

### 2. Technical Debt Considerations

- Monitor database performance
- Review rate limiting effectiveness
- Assess code coverage
- Evaluate API response times

## Notes

- Project is in initial setup phase
- Focus on documentation and architecture
- Preparing for implementation phase
