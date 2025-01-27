# API Documentation

## 1. Introduction

This document describes the RESTful API for accessing game item data. The API is designed to provide structured access to item information, classes, subclasses, and user-defined groups, stored in the backend database.  All API endpoints return data in JSON format.

## 2. Base URL

The base URL for all API endpoints will be:

`/api/v1`

(Note: This is a placeholder. The actual base URL will depend on your deployment environment.)

## 3. Authentication and Authorization

*For the initial version of this API, no authentication or authorization is implemented.*  The API is intended for public read-only access to item data.

*In future versions, if needed, authentication (e.g., API keys or JWT) and authorization mechanisms can be added to control access, especially if group management features are introduced via the API.*

## 4. Endpoints

### 4.1. Items Endpoints

#### 4.1.1. Get Item by ID

* **Endpoint:** `GET /api/v1/items/{item_id}`
* **Description:** Retrieves detailed information for a specific item.
* **Path Parameters:**
  * `item_id` (integer): The unique identifier of the item.
* **Request Body:** None.
* **Response Body (200 OK):**

    ```json
    {
      "item_id": 12345,
      "item_name": "Example Item Name",
      "item_class_id": 4,
      "item_class_name": "Armor",
      "item_subclass_id": 3,
      "item_subclass_name": "Plate",
      "display_subclass_name": "Plate Armor",
      "groups": ["Group Name 1", "Group Name 2"]  // List of group names the item belongs to (can be empty)
    }
    ```

  * `groups` field will be included if group information is requested (e.g., via query parameter in the future). For now, let's assume it's always included as an empty array if the item is not in any group, or an array of group names if it is.
* **Error Responses:**
  * **404 Not Found:** If the item with the given `item_id` does not exist.
  * **500 Internal Server Error:** For unexpected server errors.

#### 4.1.2. List Items (with Filtering and Pagination)

* **Endpoint:** `GET /api/v1/items`
* **Description:** Retrieves a list of items, with optional filtering and pagination.
* **Query Parameters:**
  * `page` (integer, optional, default: 1): Page number for pagination.
  * `page_size` (integer, optional, default: 15): Number of items per page.
  * `item_class_name` (string, optional): Filter items by item class name (e.g., "Weapon", "Consumable").
  * `item_subclass_name` (string, optional): Filter items by item subclass name (e.g., "Sword", "Potion").
  * *More filters can be added in the future (e.g., by group, item name search, etc.)*
* **Request Body:** None.
* **Response Body (200 OK):**

    ```json
    {
      "page": 1,
      "page_size": 15,
      "total_items": 120,
      "total_pages": 8,
      "items": [
        {
          "item_id": 12345,
          "item_name": "Example Item 1",
          "item_class_name": "Armor",
          "item_subclass_name": "Plate"
        },
        {
          "item_id": 67890,
          "item_name": "Example Item 2",
          "item_class_name": "Weapon",
          "item_subclass_name": "Sword"
        },
        // ... more items (up to page_size)
      ]
    }
    ```

* **Error Responses:**
  * **400 Bad Request:**  For invalid query parameters (e.g., non-integer page/page_size).
  * **500 Internal Server Error:** For unexpected server errors.

### 4.2. Item Classes Endpoints

#### 4.2.1. List Item Classes

* **Endpoint:** `GET /api/v1/item-classes`
* **Description:** Retrieves a list of all item classes.
* **Request Body:** None.
* **Response Body (200 OK):**

    ```json
    [
      {
        "item_class_id": 0,
        "item_class_name": "Consumable"
      },
      {
        "item_class_id": 2,
        "item_class_name": "Weapon"
      },
      // ... more item classes
    ]
    ```

* **Error Responses:**
  * **500 Internal Server Error:** For unexpected server errors.

#### 4.2.2. List Subclasses for an Item Class

* **Endpoint:** `GET /api/v1/item-classes/{class_id}/subclasses`
* **Description:** Retrieves a list of subclasses for a specific item class.
* **Path Parameters:**
  * `class_id` (integer): The ID of the item class.
* **Request Body:** None.
* **Response Body (200 OK):**

    ```json
    [
      {
        "item_subclass_id": 7,
        "item_subclass_name": "Swords"
      },
      {
        "item_subclass_id": 8,
        "item_subclass_name": "Axes"
      },
      // ... more subclasses for the given class_id
    ]
    ```

* **Error Responses:**
  * **404 Not Found:** If the item class with the given `class_id` does not exist.
  * **500 Internal Server Error:** For unexpected server errors.

### 4.3. Groups Endpoints

#### 4.3.1. List Groups

* **Endpoint:** `GET /api/v1/groups`
* **Description:** Retrieves a list of all user-defined item groups.
* **Request Body:** None.
* **Response Body (200 OK):**

    ```json
    [
      {
        "group_id": 1,
        "group_name": "TWW Bags"
      },
      {
        "group_id": 2,
        "group_name": "Leveling Weapons"
      },
      // ... more groups
    ]
    ```

* **Error Responses:**
  * **500 Internal Server Error:** For unexpected server errors.

#### 4.3.2. Get Group by ID

* **Endpoint:** `GET /api/v1/groups/{group_id}`
* **Description:** Retrieves details for a specific item group.
* **Path Parameters:**
  * `group_id` (integer): The unique identifier of the group.
* **Request Body:** None.
* **Response Body (200 OK):**

    ```json
    {
      "group_id": 1,
      "group_name": "TWW Bags",
      "items": [  // List of items in this group (can be empty)
        {
          "item_id": 12345,
          "item_name": "Example Item 1",
          "item_class_name": "Container",
          "item_subclass_name": "Bag"
        },
        {
          "item_id": 98765,
          "item_name": "Example Item 2",
          "item_class_name": "Container",
          "item_subclass_name": "Bag"
        },
        // ... more items in the group
      ]
    }
    ```

* **Error Responses:**
  * **404 Not Found:** If the group with the given `group_id` does not exist.
  * **500 Internal Server Error:** For unexpected server errors.

#### 4.3.3. List Items in a Group

* **Endpoint:** `GET /api/v1/groups/{group_id}/items`
* **Description:** Retrieves a list of items belonging to a specific group.
* **Path Parameters:**
  * `group_id` (integer): The unique identifier of the group.
* **Query Parameters:**  (Pagination can be added here if needed for very large groups, but let's keep it simple for now).
* **Request Body:** None.
* **Response Body (200 OK):**

    ```json
    [
      {
        "item_id": 12345,
        "item_name": "Example Item 1",
        "item_class_name": "Container",
        "item_subclass_name": "Bag"
      },
      {
        "item_id": 98765,
        "item_name": "Example Item 2",
        "item_class_name": "Container",
        "item_subclass_name": "Bag"
      },
      // ... more items in the group
    ]
    ```

* **Error Responses:**
  * **404 Not Found:** If the group with the given `group_id` does not exist.
  * **500 Internal Server Error:** For unexpected server errors.

## 5. Pagination

For endpoints that return lists of items (e.g., `/api/v1/items`), pagination is implemented using the following query parameters:

* `page`: Specifies the page number to retrieve (default is 1).
* `page_size`: Specifies the number of items per page (default is 15).

The response body for paginated endpoints will include metadata about pagination, such as `page`, `page_size`, `total_items`, and `total_pages`.

## 6. Filtering

The `/api/v1/items` endpoint supports filtering items by `item_class_name` and `item_subclass_name` using query parameters.  Multiple filters can be combined (implicitly using AND logic).

## 7. Error Handling

The API uses standard HTTP status codes to indicate the outcome of requests.  Error responses typically include:

* **400 Bad Request:**  Indicates that the request was malformed or invalid (e.g., invalid parameters).
* **404 Not Found:**  Indicates that the requested resource was not found.
* **500 Internal Server Error:** Indicates an unexpected error on the server side.

Error responses may include a simple JSON body with an `error` message (e.g., `{"error": "Item not found"}`).

---
