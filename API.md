# TrackML API Documentation

## Models

### Get All Models

**GET /**

- Returns a list of all models
- Response: Array of model objects

```json
[
  {
    "id": integer,
    "name": string,
    "model_type": string,
    "status": string,
    "tags": array,
    "date_interacted": string
  }
]
```

### Get Model by ID

**GET /{id}**

- Parameters:
  - `id`: Model ID (integer)
- Response: Model object
- Error (404): If model not found

### Create Model

**POST /**

- Request Body:

```json
{
  "name": string,
  "model_type": string,
  "status": string,
  "tags": array,
  "date_interacted": string (ISO format)
}
```

- Response: Created model object (201)

### Update Model

**PUT /{id}**

- Parameters:
  - `id`: Model ID (integer)
- Request Body: Any model fields to update
- Response: Updated model object
- Error (404): If model not found

### Delete Model

**DELETE /{id}**

- Parameters:
  - `id`: Model ID (integer)
- Response: Empty (204)
- Error (404): If model not found

### Search Models

**GET /search**

- Query Parameters:
  - `q`: Search query (string)
  - `type`: Model type filter
  - `status`: Status filter
  - `tag`: Tag filter
- Response: Array of matching model objects

### Autofill Model

**POST /autofill**

- Request Body:

```json
{
  "model_id": string,
  "model_links": array[string]
}
```

- Response: Agent-generated model information

### Get Model Insights

**GET /{id}/insights**

- Parameters:
  - `id`: Model ID (integer)
- Response: RAG-generated insights about the model
- Error (404): If model not found

### Compare Models

**POST /insights/compare**

- Request Body:

```json
{
  "model_ids": array[integer]
}
```

- Response: RAG-generated comparative analysis
- Errors:
  - 400: No model IDs provided
  - 404: No models found

## Authentication

### Register User

**POST /auth/register**

- Request Body:

```json
{
  "username": string,
  "email": string,
  "password": string
}
```

- Response: Created user object (201)
- Errors:
  - 400: Missing fields or duplicate username/email
  - 500: Server error

### Login

**POST /auth/login**

- Request Body:

```json
{
  "email": string,
  "password": string
}
```

- Response: User object with auth token
- Errors:
  - 400: Missing fields
  - 401: Invalid credentials

### Update User

**PUT /auth/user/{id}**

- Parameters:
  - `id`: User ID (integer)
- Request Body (all fields optional):

```json
{
  "username": string,
  "email": string,
  "password": string,
  "is_active": boolean
}
```

- Response: Updated user object
- Errors:
  - 404: User not found
  - 400: Duplicate username/email

### Delete User

**DELETE /auth/user/{id}**

- Parameters:
  - `id`: User ID (integer)
- Response: Success message
- Errors:
  - 404: User not found
  - 500: Server error
