# TrackML API Documentation

## Response Format

All API endpoints return responses in a standardized format:

```json
{
  "success": boolean,
  "data": any,
  "message": string (optional),
  "error": string (only if success is false),
  "status_code": number
}
```

## CORS Support

All endpoints support CORS with the following configuration:

- Allowed Origin: http://localhost:5173
- Allowed Methods: GET, POST, PUT, DELETE, OPTIONS
- All endpoints support OPTIONS preflight requests

## Models

### Get All Models

**GET /models/ or OPTIONS /models/**

- Returns a list of all models
- Response: Array of model objects wrapped in standard format

```json
{
  "success": true,
  "data": [
    {
      "id": integer,
      "name": string,
      "model_type": string,
      "status": string,
      "tags": array,
      "date_interacted": string
    }
  ],
  "message": "Models retrieved successfully",
  "error": null,
  "status_code": 200
}
```

### Get Model by ID

**GET /models/{id} or OPTIONS /models/{id}**

- Parameters:
  - `id`: Model ID (integer)
- Response: Model object wrapped in standard format
- Error (404): If model not found

```json
{
  "success": true,
  "data": {
    "id": integer,
    "name": string,
    "model_type": string,
    "status": string,
    "tags": array,
    "date_interacted": string
  },
  "message": "Model retrieved successfully",
  "error": null,
  "status_code": 200
}
```

### Create Model

**POST /models/ or OPTIONS /models/**

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

- Response: Created model object wrapped in standard format with status code 201

```json
{
  "success": true,
  "data": {
    "id": integer,
    "name": string,
    "model_type": string,
    "status": string,
    "tags": array,
    "date_interacted": string
  },
  "message": "Model created successfully",
  "error": null,
  "status_code": 201
}
```

### Update Model

**PUT /models/{id} or OPTIONS /models/{id}**

- Parameters:
  - `id`: Model ID (integer)
- Request Body: Any model fields to update
- Response: Updated model object wrapped in standard format

```json
{
  "success": true,
  "data": {
    "id": integer,
    "name": string,
    "model_type": string,
    "status": string,
    "tags": array,
    "date_interacted": string
  },
  "message": "Model updated successfully",
  "error": null,
  "status_code": 200
}
```

### Delete Model

**DELETE /models/{id} or OPTIONS /models/{id}**

- Parameters:
  - `id`: Model ID (integer)
- Response:
  - Status code: 204
  - Body: Standard format with `data: null` and success message

```json
{
  "success": true,
  "data": null,
  "message": "Model deleted successfully",
  "error": null,
  "status_code": 204
}
```

### Search Models

**GET /models/search or OPTIONS /models/search**

- Query Parameters:
  - `q`: Search query (string)
  - `type`: Model type filter
  - `status`: Status filter
  - `tag`: Tag filter
- Response: Array of matching model objects wrapped in standard format

```json
{
  "success": true,
  "data": [
    {
      "id": integer,
      "name": string,
      "model_type": string,
      "status": string,
      "tags": array,
      "date_interacted": string
    }
  ],
  "message": "Models retrieved successfully",
  "error": null,
  "status_code": 200
}
```

### Autofill Model

**POST /models/autofill or OPTIONS /models/autofill**

- Request Body (multipart/form-data):

  - `model_id`: string - ID of the model to autofill information for
  - `model_links[]`: array of strings - Optional list of URLs containing model information
  - `files[]`: array of files - Optional PDF and DOC/DOCX files containing model information

- Response:

```json
{
  "success": boolean,
  "data": {
    "response": string
  },
  "status_code": number
}
```

- Note: Files are temporarily stored and automatically cleaned up after processing
- Supported file types: PDF (.pdf), Word documents (.doc, .docx)

### Get Model Insights

**GET /models/{id}/insights or OPTIONS /models/{id}/insights**

- Parameters:
  - `id`: Model ID (integer)
- Response: RAG-generated insights about the model wrapped in standard format

```json
{
  "success": true,
  "data": {
    "insights": string
  },
  "message": "Model insights retrieved successfully",
  "error": null,
  "status_code": 200
}
```

### Compare Models

**POST /models/insights/compare or OPTIONS /models/insights/compare**

- Request Body:

```json
{
  "model_ids": array[integer]
}
```

- Response: RAG-generated comparative analysis wrapped in standard format
- Errors:
  - 400: No model IDs provided
  - 404: No models found

```json
{
  "success": true,
  "data": {
    "analysis": string
  },
  "message": "Model comparison analysis retrieved successfully",
  "error": null,
  "status_code": 200
}
```

## Authentication

### Register User

**POST /auth/register or OPTIONS /auth/register**

- Request Body:

```json
{
  "username": string,
  "email": string,
  "password": string
}
```

- Response: Created user object wrapped in standard format with status code 201

```json
{
  "success": true,
  "data": {
    "token": string,
    "user": {
      "id": integer,
      "username": string,
      "email": string,
      "is_active": boolean
    }
  },
  "message": "User registered successfully",
  "error": null,
  "status_code": 201
}
```

### Login

**POST /auth/login or OPTIONS /auth/login**

- Request Body:

```json
{
  "email": string,
  "password": string
}
```

- Response: User object with auth token wrapped in standard format

```json
{
  "success": true,
  "data": {
    "token": string,
    "user": {
      "id": integer,
      "username": string,
      "email": string,
      "is_active": boolean
    }
  },
  "message": "User logged in successfully",
  "error": null,
  "status_code": 200
}
```

### Verify Token

**GET /auth/verify-token or OPTIONS /auth/verify-token**

- Headers:
  - `Authorization`: Bearer token
- Response: User object wrapped in standard format

```json
{
  "success": true,
  "data": {
    "user": {
      "id": integer,
      "username": string,
      "email": string,
      "is_active": boolean
    }
  },
  "message": "Token verified successfully",
  "error": null,
  "status_code": 200
}
```

### Update User

**PUT /auth/user/{id} or OPTIONS /auth/user/{id}**

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

- Response: Updated user object wrapped in standard format

```json
{
  "success": true,
  "data": {
    "id": integer,
    "username": string,
    "email": string,
    "is_active": boolean
  },
  "message": "User updated successfully",
  "error": null,
  "status_code": 200
}
```

### Delete User

**DELETE /auth/user/{id} or OPTIONS /auth/user/{id}**

- Parameters:
  - `id`: User ID (integer)
- Response: Success message wrapped in standard format

```json
{
  "success": true,
  "data": null,
  "message": "User deactivated successfully",
  "error": null,
  "status_code": 200
}
```

## Common HTTP Status Codes

- 200: Success
- 201: Created
- 204: No Content
- 400: Bad Request
- 401: Unauthorized
- 404: Not Found
- 500: Server Error

## CORS Response Headers

All responses include the following CORS headers:

- Access-Control-Allow-Origin: http://localhost:5173
- Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS
- Access-Control-Allow-Headers: Content-Type, Authorization
