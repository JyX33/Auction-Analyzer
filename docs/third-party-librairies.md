# Third-Party Libraries Documentation

This document lists and describes the third-party Python libraries that will be used in the backend development for the Blizzard Item Data Extractor project.

## 1. Core Backend Framework

* **FastAPI:**
  * **Version:** Latest stable version (e.g., `^0.109.0`)
  * **Description:** A modern, fast (high-performance), web framework for building APIs with Python 3.7+ based on standard Python type hints.
  * **Rationale:** Chosen for its high performance, asynchronous support (essential for handling concurrent API requests to the Blizzard API), automatic data validation using Pydantic, dependency injection, and excellent documentation. It simplifies API development and is well-suited for building efficient and scalable backends.

* **Uvicorn:**
  * **Version:** Latest stable version (e.g., `^0.27.0`)
  * **Description:** An ASGI (Asynchronous Server Gateway Interface) server implementation for Python.
  * **Rationale:**  Used to run the FastAPI application. Uvicorn is a lightweight, fast, and production-ready ASGI server, ideal for serving asynchronous Python web applications.

## 2. Database Interaction

* **SQLAlchemy:**
  * **Version:** Latest stable version (e.g., `^2.0.0`)
  * **Description:** A powerful and comprehensive SQL toolkit and Object-Relational Mapper (ORM) for Python.
  * **Rationale:** While we are using SQLite initially, SQLAlchemy provides an abstraction layer over different database systems. Using SQLAlchemy from the start will make it easier to switch to a more robust database like PostgreSQL in the future if needed. It offers features like schema definition, database migrations, and object-relational mapping, making database interactions more manageable and less error-prone.

* **Databases (python-databases):**
  * **Version:** Latest stable version (e.g., `^0.9.2`)
  * **Description:** An asynchronous database library for Python that provides async support for various databases, including SQLite, PostgreSQL, and MySQL. It is built to work seamlessly with `asyncio` and ASGI frameworks like FastAPI.
  * **Rationale:**  Provides the necessary asynchronous database drivers to work with SQLite in an asynchronous FastAPI application. It's designed to be lightweight and efficient, and integrates well with SQLAlchemy for schema definition and migration.

* **SQLite (sqlite3 - Python Standard Library):**
  * **Version:** Included with Python standard library.
  * **Description:**  A C library that provides a lightweight disk-based database that doesn’t require a separate server process and allows accessing the database via a nonstandard variant of the SQL query language.
  * **Rationale:** Chosen as the initial database for its simplicity, file-based nature, and ease of setup for a personal project. Python's standard library `sqlite3` module provides the necessary bindings to interact with SQLite databases.

## 3. HTTP Client for Blizzard API

* **httpx:**
  * **Version:** Latest stable version (e.g., `^0.26.0`)
  * **Description:** A next-generation HTTP client for Python. It supports both HTTP/1.1 and HTTP/2, and provides both synchronous and asynchronous APIs.
  * **Rationale:** Selected for making asynchronous HTTP requests to the Blizzard API. `httpx` is designed for modern asynchronous Python applications, offering excellent performance, a clean API, and features like connection pooling and HTTP/2 support. Its asynchronous nature is crucial for making concurrent requests efficiently within the FastAPI backend.

## 4. Data Validation and Settings Management

* **Pydantic:**
  * **Version:** Latest stable version (e.g., `^2.6.0`)
  * **Description:** Data validation and settings management using Python type hinting.
  * **Rationale:**  FastAPI uses Pydantic for request body validation, response serialization, and dependency injection.  It's a powerful library for ensuring data quality and managing application settings. Although FastAPI includes it, explicitly mentioning it highlights its importance in the project.

## 5. Asynchronous Operations and Concurrency

* **asyncio (Python Standard Library):**
  * **Version:** Included with Python standard library.
  * **Description:**  A library to write concurrent code using the `async/await` syntax.
  * **Rationale:**  Python's built-in asynchronous programming library. `asyncio` is fundamental for handling concurrent API requests to the Blizzard API and for building a non-blocking, efficient backend with FastAPI. We will use `asyncio.Semaphore` for controlling the concurrency level.

## 6. Testing

* **pytest:**
  * **Version:** Latest stable version (e.g., `^8.0.0`)
  * **Description:** A mature and full-featured Python testing framework.
  * **Rationale:**  Chosen for writing unit tests and integration tests for the backend. `pytest` simplifies test writing and execution with features like auto-discovery of tests, fixtures, and plugins.

* **httpx.TestClient:**
  * **Version:**  Part of the `httpx` library.
  * **Description:**  Provides a test client for testing ASGI applications directly in-memory, without needing to start a server.
  * **Rationale:**  `httpx`'s `TestClient` is ideal for testing FastAPI endpoints. It allows for easy sending of requests to the API within tests and verifying responses.

## 7. Other Utilities (Python Standard Library)

We will also utilize various modules from the Python standard library for general utility functions, data manipulation, and system interactions, such as:

* `json` for JSON data handling.
* `os` for operating system interactions.
* `typing` for type hints.
* `asyncio.Semaphore` for concurrency control.
* `time` for time-related functions (e.g., delays for rate limiting).

---
