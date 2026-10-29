# Lab7-Rita-Abou-Fares

A Python user-management application built with Flask and SQLite, with automated
tests written using pytest. The application exposes a JSON API for creating,
retrieving, updating, and deleting users.

## Project structure

| File | Description |
| --- | --- |
| `app.py` | Creates the Flask application, enables CORS, initializes the database, and defines the API routes. |
| `database.py` | Manages the SQLite connection, table creation, initial data, and user CRUD operations. |
| `test_user_Rita_Abou_Fares.py` | Contains pytest fixtures and tests for database initialization, database operations, and individual-user API operations. |
| `requirements.txt` | Lists Flask, Flask-Cors, and pytest dependencies. |
| `.gitignore` | Excludes the virtual environment, generated database, and Python and pytest caches. |

`database.db` is generated in the project folder when the application first runs.

## Installation

From the project folder in PowerShell, create a virtual environment and install
the dependencies:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

SQLite support is included in Python's standard library.

## Run the application

```powershell
.\.venv\Scripts\python.exe app.py
```

The API runs locally at `http://127.0.0.1:5000`.

## Database

The `users` table contains the following fields:

| Field | Description |
| --- | --- |
| `user_id` | Automatically generated integer primary key. |
| `name` | User's full name. |
| `email` | Email address. |
| `phone` | Phone number stored as text. |
| `address` | Address. |
| `country` | Country. |

All fields are required. When `create_db_table()` creates the users table, it
inserts the initial Rita Abou Fares record. Later calls preserve existing records
and do not reinsert deleted users.

`database.py` provides `insert_user()`, `get_users()`, `get_user_by_id()`,
`update_user()`, and `delete_user()`. Queries use parameters for supplied values,
and returned user records are Python dictionaries. `get_users()` returns a list
ordered by user ID.

## API endpoints

| Method | Route | Description |
| --- | --- | --- |
| GET | `/api/users` | Returns all users as a JSON array. |
| GET | `/api/users/<user_id>` | Returns a single user as a JSON object. |
| POST | `/api/users/add` | Creates a user from a JSON request and returns the saved record, including its generated ID. |
| PUT | `/api/users/update` | Updates the user identified by `user_id` and returns the updated record. |
| DELETE | `/api/users/delete/<user_id>` | Deletes the user and returns a JSON status message. |

POST and PUT requests use the `Content-Type: application/json` header. To add a
user, send all five user-detail fields:

```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "phone": "067765434567",
  "address": "Beirut",
  "country": "Lebanon"
}
```

For an update, include `user_id` along with all five fields. Successful operations
return HTTP status `200`. A lookup for an unknown user ID returns `{}` with
status `200`. A successful deletion returns:

```json
{"status": "User deleted successfully"}
```

## Tests

Run the test suite from the project folder:

```powershell
.\.venv\Scripts\python.exe -m pytest
```

The tests cover first-run database creation and initial data, inserting and
retrieving users, updating and deleting records, and the corresponding
individual-user API operations. API assertions check HTTP status codes, JSON
response data, and persisted database changes.

Pytest fixtures provide sample users and a separate temporary SQLite database
for each test. The database path is redirected with `monkeypatch`, so the suite
preserves the application's `database.db`. API tests use Flask's test client
and do not require a running server.
