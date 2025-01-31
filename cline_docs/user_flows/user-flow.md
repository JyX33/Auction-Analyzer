# User Flow Documentation

## 1. Data Extraction Process User Flow

This section describes the user flow for the data extraction script, which is responsible for fetching item data from the Blizzard API and storing it in the SQLite database.

### 1.1. Data Extraction Script Flow Diagram

```mermaid
graph LR
    A[Start Script] --> B(Read Item IDs from TXT File);
    B --> C{Initialize SQLite Database Connection};
    C --> D{Fetch Item Classes from Blizzard API <br> `/data/wow/item-class/index`};
    D --> E{Process Each Item Class};
    E --> F{Fetch Subclasses for Class <br> `/data/wow/item-class/{class_id}`};
    F --> G{Store Class and Subclass Data in DB <br> (groups table - future enhancement)};
    G --> H{Read Item IDs from Input File};
    H --> I{Initialize Concurrency Semaphore (limit=20)};
    I --> J{For Each Item ID in Input List};
    J --> K{Acquire Semaphore (limit concurrent requests)};
    K --> L[Construct Item Search API URL <br> `/data/wow/search/item?id={item_id}`];
    L --> M[Send Asynchronous API Request <br> (using httpx)];
    M --> N{Receive API Response};
    N -- 200 OK --> O[Parse JSON Response];
    N -- 429 Error --> P[Handle Rate Limit: <br> Exponential Backoff & Retry];
    O --> Q[Extract Item Name from Response];
    Q --> R[Extract Item Class & Subclass IDs from Response];  {{Or use pre-fetched class/subclass data? - Clarify this point}}
    R --> S[Insert/Update Item Data in 'items' Table <br> (item_id, name, class_id, class_name, subclass_id, subclass_name)];
    S --> T[Release Semaphore];
    T --> U{Log Success for Item ID};
    U --> V{Next Item ID or All Items Processed?};
    V -- Next Item ID --> J;
    V -- All Items Processed --> W[Generate Extraction Report];
    W --> X{Close DB Connection};
    X --> Y[End Script];
    P --> K; {{ Retry Request after Delay }}
    N -- Other Error (e.g., 500) --> Z[Log API Error for Item ID];
    Z --> T; {{ Release Semaphore & Continue }}
```

### 1.2. Detailed Steps

1. **Start Script:** The data extraction script is initiated (e.g., run from the command line).
2. **Read Item IDs from TXT File:** The script reads the list of item IDs from the specified text file.  Item IDs are expected to be comma-separated in the file.
3. **Initialize SQLite Database Connection:**  The script establishes a connection to the SQLite database file. This connection will be used throughout the script's execution.
4. **Fetch Item Classes from Blizzard API:** The script makes an initial API call to `/data/wow/item-class/index` to retrieve a list of all item classes and their IDs.
5. **Process Each Item Class & Fetch Subclasses:** For each item class obtained in the previous step, the script calls `/data/wow/item-class/{class_id}` to get the list of subclasses associated with that class.
6. **Store Class and Subclass Data in Database:**  *(Future Enhancement)*  Currently, we are primarily focused on item data.  Storing class and subclass names in a separate `classes` and `subclasses` table could be a future optimization. For now, we will store class and subclass names directly with each item in the `items` table.
7. **Read Item IDs from Input File:** (Redundant step in diagram - combined with step 2 in description) The script reads the list of item IDs from the input file.
8. **Initialize Concurrency Semaphore:** An `asyncio.Semaphore` is initialized with a limit of 20 to control the number of concurrent API requests.
9. **For Each Item ID in Input List:** The script iterates through each item ID from the input list.
10. **Acquire Semaphore:** Before making an API request for an item, the script acquires a slot from the semaphore. This ensures that no more than 20 requests are in flight simultaneously.
11. **Construct Item Search API URL:**  The script constructs the Blizzard API URL for searching item details using the current `item_id`.  The endpoint used is `/data/wow/search/item?id={item_id}`. *(Note: We are using the US endpoint as per your earlier example. Confirm region consistency if needed.)*
12. **Send Asynchronous API Request:**  The script sends an asynchronous HTTP GET request to the Blizzard API using `httpx`.
13. **Receive API Response:** The script waits for and receives the API response.
14. **Handle API Response (200 OK):** If the response status code is 200 OK:
    * **Parse JSON Response:** The script parses the JSON response body.
    * **Extract Item Name from Response:** The script extracts the item name from the parsed JSON data.
    * **Extract Item Class & Subclass IDs from Response:** The script extracts the item's class and subclass IDs from the response. *(Note: We might be able to get class and subclass names directly from the pre-fetched class/subclass data to avoid extra API calls - to be clarified.)*
    * **Insert/Update Item Data in 'items' Table:** The script inserts a new record into the `items` table with the extracted item data (item\_id, item\_name, item\_class\_id, item\_class\_name, item\_subclass\_id, item\_subclass\_name) or updates an existing record if the `item_id` already exists.
    * **Release Semaphore:** The script releases the semaphore slot, allowing another concurrent request to proceed.
    * **Log Success for Item ID:**  The script logs a success message, indicating that the item data was successfully processed and stored for the current `item_id`.
15. **Handle API Response (429 Error - Rate Limit):** If the response status code is 429 (Too Many Requests):
    * **Handle Rate Limit: Exponential Backoff & Retry:** The script implements a rate limit handling strategy, such as exponential backoff. It waits for a certain duration (initially short, increasing with each consecutive 429 error) and then retries the API request for the same `item_id`.
    * **Retry Request:** After the delay, the script retries sending the API request (goes back to step K in Part 1 diagram).
16. **Handle API Response (Other Errors - e.g., 500):** If the response status code is any other error (e.g., 500 Internal Server Error):
    * **Log API Error for Item ID:** The script logs an error message, indicating that an API error occurred for the current `item_id`, including the error details from the API response.
    * **Release Semaphore:** The script releases the semaphore slot.
    * **Continue to Next Item:** The script proceeds to the next item ID in the input list.
17. **Next Item ID or All Items Processed?:** The script checks if there are more item IDs to process in the input list.
    * **Next Item ID:** If there are more items, the script proceeds to the next `item_id` (goes back to step J in Part 1 diagram).
    * **All Items Processed:** If all item IDs have been processed, the script moves to the next step.
18. **Generate Extraction Report:** Once all items are processed, the script generates a report summarizing the data extraction process.  *(Report details to be defined - see next questions).*
19. **Close DB Connection:** The script closes the connection to the SQLite database.
20. **End Script:** The data extraction script execution is completed.

### 1.3. Report Generation

After processing all item IDs, the script will generate two report files in the `output/` subdirectory:

1. **Markdown Report (`extraction_report.md`):** A human-readable report in Markdown format, summarizing the extraction process.
2. **JSON Report (`extraction_report_dd-MM-YYYY-HHmmss.json`):** A structured report in JSON format, containing detailed data for programmatic access and analysis. The filename will include a timestamp (day-month-year-hour-minute-second) to ensure uniqueness for each run.

#### 1.3.1. Markdown Report Content (`extraction_report.md`)

The Markdown report will include the following sections:

```markdown
# Item Data Extraction Report - [Date and Time of Generation]

## Summary

- **Total Items Processed:** [Number of items attempted to process]
- **Start Time:** [Timestamp of when the script started]
- **End Time:** [Timestamp of when the script finished]
- **Total Duration:** [Total time taken for the extraction process, e.g., "HH:MM:SS"]
- **Total Blizzard API Requests:** [Number of API requests made]
- **Rate Limit Retries:** [Number of times requests were retried due to rate limiting]
- **Average Processing Time per Item (Excluding Retries):** [Average time in seconds or milliseconds]

## Success Summary

- **Total Successful Items:** [Number of items successfully extracted and stored]
- **Successful Item IDs:**
  [List of item IDs that were successfully processed, each on a new line]

## Error Summary

- **Total Failed Items:** [Number of items that encountered errors during processing]
- **Failed Item IDs:**
  [List of item IDs that failed processing, each on a new line]
- **Error Type Breakdown:**
  - **Rate Limit Errors:** [Number of rate limit errors encountered]
  - **API Server Errors:** [Number of general API server errors (e.g., 500 errors)]
  - **Database Errors:** [Number of database insertion/update errors]

### Detailed Errors

[If there were errors, this section will be present]

For each failed item, the following details are provided:

- **Item ID:** [Item ID]
  - **Error Type:** [Error category: Rate Limit Error, API Server Error, Database Error]
  - **Error Message:** [Specific error message received or generated]
```

#### 1.3.2. JSON Report Content (extraction_report_dd-MM-YYYY-HHmmss.json)

The JSON report will have the following structure:

```json
{
  "report_metadata": {
    "start_time": "[ISO 8601 Timestamp]",
    "end_time": "[ISO 8601 Timestamp]",
    "total_duration_seconds": [Total duration in seconds],
    "total_items_processed": [Number of items attempted],
    "total_api_requests": [Number of API requests],
    "rate_limit_retries": [Number of retries],
    "average_processing_time_per_item_seconds": [Average time per item]
  },
  "success_summary": {
    "total_successful_items": [Number of successful items],
    "successful_item_ids": [
      [Item ID 1],
      [Item ID 2],
      // ... list of successful item IDs
    ]
  },
  "error_summary": {
    "total_failed_items": [Number of failed items],
    "failed_item_ids": [
      [Item ID 1],
      [Item ID 2],
      // ... list of failed item IDs
    ],
    "error_type_counts": {
      "rate_limit_errors": [Number of rate limit errors],
      "api_server_errors": [Number of API server errors],
      "database_errors": [Number of database errors]
    },
    "detailed_errors": [
      {
        "item_id": [Failed Item ID 1],
        "error_type": "Rate Limit Error",
        "error_message": "[Specific error message]"
      },
      {
        "item_id": [Failed Item ID 2],
        "error_type": "API Server Error",
        "error_message": "[Specific error message]"
      },
      // ... list of detailed errors
    ]
  }
}
```

#### 1.3.3. Report File Location

Both extraction_report.md and extraction_report_dd-MM-YYYY-HHmmss.json files will be saved in a newly created output/ subdirectory within the script's execution directory. If the output/ directory does not exist, the script will create it.

### 1.4. Logging

The script will implement comprehensive logging to record the execution process, aid in debugging, and monitor performance.  Logging will be output to both the console (for immediate visibility) and a log file (for persistent, structured records).

#### 1.4.1. Logging Levels

The following logging levels will be used to categorize log messages by severity and detail:

* **DEBUG:**  Detailed information for developers, enabled during debugging. (e.g., API request URLs, detailed steps within functions).
* **INFO:** General informational messages about script progress and important events during normal operation. (e.g., script start/end, item processing success, report generation).
* **WARNING:**  Indicates potential issues or unusual situations that are not errors but should be investigated. (e.g., rate limit retries, unexpected API data).
* **ERROR:** Logs errors that prevent the script from completing a task for a specific item or operation. (e.g., API rate limit errors, other API errors, database errors).

#### 1.4.2. Log Content

Each log message will include:

* **Timestamp:**  ISO 8601 format (e.g., `2024-08-03### 1.4. Logging (To be Detailed)
