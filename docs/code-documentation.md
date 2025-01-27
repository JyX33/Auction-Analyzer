# Code Documentation Plan

This document outlines the plan for code documentation for the Blizzard Item Data Extractor project.  The goal is to create documentation that is sufficient for understanding, using, and maintaining the project, focusing on clarity and practicality.

## 1. Code Comments

* **Level of Detail:** Moderate. Inline comments will be used to explain the purpose of functions, classes, and significant code blocks. The focus will be on explaining the "why" behind the code and clarifying non-obvious logic, rather than commenting on every single line.
* **Focus Areas for Comments:**
  * **Complex Logic:**  Algorithms, data processing steps, and intricate control flow.
  * **API Interactions:**  Comments explaining how the script interacts with the Blizzard API, request/response handling, and rate limit management.
  * **Database Operations:**  Comments detailing database schema interactions, queries, and data storage logic.
  * **Concurrency Management:**  Explanations of how `asyncio.Semaphore` is used and how concurrent requests are handled.
  * **Error Handling:**  Comments describing error handling strategies and specific error scenarios.
* **Style:**  Use clear, concise, and grammatically correct English. Comments should be helpful to someone reading the code, including your future self. Follow Python's style conventions for comments (e.g., using docstrings for functions and classes, `#` for inline comments).

**Example - Function Docstring:**

```python
async def fetch_item_data_from_api(item_id: int, session: httpx.AsyncClient) -> dict:
    """
    Fetches item data from the Blizzard API for a given item ID.

    Args:
        item_id: The ID of the item to fetch.
        session: httpx.AsyncClient session for making requests.

    Returns:
        A dictionary containing the item data in JSON format, or None if an error occurs.

    Raises:
        httpx.HTTPError: If the API request fails with a non-429 error status code.
        RateLimitError: If a 429 "Too Many Requests" error is encountered.
    """
    # ... function code ...
```

**Example - Inline Comment:**

```python
await asyncio.sleep(retry_delay)  # Wait before retrying to respect rate limits
```

## 2. README.md File

The `README.md` file at the project root will serve as the primary entry point for project documentation. It will include the following sections:

* **Project Title:** Clear and descriptive title (e.g., "Blizzard Item Data Extractor").

* **Project Description:** A concise overview of what the project does, its purpose, and target users. Focus on explaining "what the project is about" for someone new to it.

* **Features:** A bulleted list of the main features of the data extraction script and the planned API/website (even if frontend is future work).

* **Getting Started:**

  * **Prerequisites:** List any software or accounts required (e.g., Python version, Blizzard API credentials, etc.).

  * **Installation:** Step-by-step instructions on how to set up the project environment (e.g., cloning the repository, creating a virtual environment, /installing dependencies using pip install -r requirements.txt).

  * **Configuration:** Instructions on how to configure the script (e.g., setting Blizzard API credentials, input file location, database setup - if any manual steps are needed).

* **Usage:**

  * **Running the Script:** Detailed instructions on how to run the data extraction script, including command-line arguments, input file format, and expected output.

  * **Example Usage:** Provide example commands and input file snippets to illustrate how to use the script.

* **Database Schema:** Link to the docs/database-schema-part1.md and docs/database-schema-part2.md documents for detailed database schema information.

* **API Documentation:** Mention that API documentation will be available via the built-in Swagger UI when the FastAPI application is running (link to be added later when DevOps is planned).

* **Contact/Author Information:** Your name/contact info (optional, for a personal project).

The README.md will be written in Markdown format for easy readability on platforms like GitHub and in text editors.

## 3. API Documentation (Swagger UI)

For the future REST API built with FastAPI, we will leverage FastAPI's built-in support for Swagger UI and OpenAPI.

* Automatic Generation: FastAPI automatically generates OpenAPI schema and Swagger UI based on your API endpoint definitions, request/response models (using Pydantic), and docstrings in your code.

* Interactive Documentation: Swagger UI provides an interactive web interface to explore the API endpoints, their parameters, request bodies, and response schemas. It also allows making test API requests directly from the browser.

* Accessing Swagger UI: Once the FastAPI application is running, Swagger UI will be accessible at a default URL (e.g., /docs or /swagger). This URL will be documented in the README.md and devops.md documents.

* Docstrings for API Endpoints: To enhance the Swagger UI documentation, we will write clear and informative docstrings for all API endpoint functions in FastAPI. These docstrings will be used to populate descriptions in Swagger UI.

**Example - FastAPI Endpoint Docstring:**

```python
@app.get("/items/{item_id}", response_model=Item)
async def read_item(item_id: int):
    """
    Retrieve an item by its ID.

    Args:
        item_id: The ID of the item to retrieve.

    Returns:
        Item: The item data in JSON format.

    Raises:
        HTTPException (status_code=404): If the item is not found.
    """
    # ... endpoint code ...
```

## 4. Architecture Diagrams

(Currently, no separate architecture diagrams are planned. The Mermaid diagram in user-flow.md and the database schema diagram in database-schema-part1.md are considered sufficient for initial documentation. We can add more diagrams later if needed.)

## 5. Critical Documentation and Workflow

### 5.1 Documentation Management

Maintain a 'aider_docs' folder in the root directory (create if it doesn't exist) with the following essential files:

1. projectRoadmap.md

   * Purpose: High-level goals, features, completion criteria, and progress tracker
   * Update: When high-level goals change or tasks are completed
   * Include: A "completed tasks" section to maintain progress history
   * Format: Use headers (##) for main goals, checkboxes for tasks (- [ ] / - [x])
   * Content: List high-level project goals, key features, completion criteria, and track overall progress
   * Include considerations for future scalability when relevant

2. currentTask.md

   * Purpose: Current objectives, context, and next steps. This is your primary guide.
   * Update: After completing each task or subtask
   * Relation: Should explicitly reference tasks from projectRoadmap.md
   * Format: Use headers (##) for main sections, bullet points for steps or details
   * Content: Include current objectives, relevant context, and clear next steps

3. techStack.md

   * Purpose: Key technology choices and architecture decisions
   * Update: When significant technology decisions are made or changed
   * Format: Use headers (##) for main technology categories, bullet points for specifics
   * Content: Detail chosen technologies, frameworks, and architectural decisions with brief justifications

4. codebaseSummary.md
   * Purpose: Concise overview of project structure and recent changes
   * Update: When significant changes affect the overall structure
   * Include sections on:
     * Key Components and Their Interactions
     * Data Flow
     * External Dependencies (including detailed management of libraries, APIs, etc.)
     * Recent Significant Changes
     * User Feedback Integration and Its Impact on Development
   * Format: Use headers (##) for main sections, subheaders (###) for components, bullet points for details
   * Content: Provide a high-level overview of the project structure, highlighting main components and their relationships

### 5.2 Additional Documentation

* Create reference documents for future developers as needed, storing them in the aider_docs folder
* Examples include styleAesthetic.md or wireframes.md
* Note these additional documents in codebaseSummary.md for easy reference

### 5.3 Adaptive Workflow

* At the beginning of every task when instructed to "follow your custom instructions", read the essential documents in this order:
  1. projectRoadmap.md (for high-level context and goals)
  2. currentTask.md (for specific current objectives)
  3. techStack.md
  4. codebaseSummary.md
* If you try to read or edit another document before reading these, something BAD will happen.
* Update documents based on significant changes, not minor steps
* If conflicting information is found between documents, ask the user for clarification
* Create files in the userInstructions folder for tasks that require user action
  * Provide detailed, step-by-step instructions
  * Include all necessary details for ease of use
  * No need for a formal structure, but ensure clarity and completeness
  * Use numbered lists for sequential steps, code blocks for commands or code snippets
* Prioritize frequent testing: Run servers and test functionality regularly throughout development, rather than building extensive features before testing
