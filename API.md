# TrackML API Documentation

## Response Format

All API endpoints return responses in a standardized format:

```json
{
  "success": boolean,
  "message": string,
  "statusCode": number,
  "timestamp": string (ISO format),
  "data": any,
  "error": string (only if success is false)
}
```

## CORS Support

All endpoints support CORS with the following configuration:

- Allowed Origin: http://localhost:5173
- Allowed Methods: GET, POST, PUT, DELETE, OPTIONS
- Allowed Headers: Content-Type, Authorization
- Credentials: true
- All endpoints support OPTIONS preflight requests

## Authentication

### Register User

**POST /api/auth/register**

- Request Body:

```json
{
  "username": string,
  "email": string,
  "password": string
}
```

- Response (201):

```json
{
  "success": true,
  "message": "User registered successfully",
  "statusCode": 201,
  "timestamp": string,
  "data": {
    "user": {
      "id": integer,
      "username": string,
      "email": string,
      "is_active": boolean,
      "created_at": string,
      "workspaces": array
    }
  }
}
```

### Login

**POST /api/auth/login**

- Request Body:

```json
{
  "username": string,
  "password": string
}
```

- Response (200):

```json
{
  "success": true,
  "message": "Login successful",
  "statusCode": 200,
  "timestamp": string,
  "data": {
    "token": string,
    "user": {
      "id": integer,
      "username": string,
      "email": string,
      "is_active": boolean,
      "created_at": string,
      "workspaces": array
    }
  }
}
```

### Verify Token

**POST /api/auth/verify-token**

- Request Body:

```json
{
  "token": string
}
```

- Response (200):

```json
{
  "success": true,
  "message": "Token verified successfully",
  "statusCode": 200,
  "timestamp": string,
  "data": {
    "user": {
      "id": integer,
      "username": string,
      "email": string,
      "is_active": boolean,
      "created_at": string,
      "workspaces": array
    }
  }
}
```

### Change Password

**POST /api/auth/change-password**

- Request Body:

```json
{
  "user_id": integer,
  "old_password": string,
  "new_password": string
}
```

- Response (200):

```json
{
  "success": true,
  "message": "Password changed successfully",
  "statusCode": 200,
  "timestamp": string
}
```

### Update User

**PUT /api/auth/user/{user_id}**

- Request Body:

  - Any user fields to update

- Response (200):

```json
{
  "success": true,
  "message": "User updated successfully",
  "statusCode": 200,
  "timestamp": string,
  "data": {
    "user": {
      "id": integer,
      "username": string,
      "email": string,
      "is_active": boolean,
      "created_at": string,
      "workspaces": array
    }
  }
}
```

### Delete User

**DELETE /api/auth/user/{user_id}**

- Headers:

  - `Authorization`: Bearer token

- Response (200):

```json
{
  "success": true,
  "message": "User deactivated successfully",
  "statusCode": 200,
  "timestamp": string
}
```

## Workspaces

### Create Workspace

**POST /api/workspaces**

- Headers:

  - `Authorization`: Bearer token

- Request Body:

```json
{
  "name": string,
  "description": string (optional)
}
```

- Response (201):

```json
{
  "success": true,
  "message": "Workspace created successfully",
  "statusCode": 201,
  "timestamp": string,
  "data": {
    "id": integer,
    "name": string,
    "description": string,
    "created_at": string,
    "is_default": boolean,
    "user_id": integer,
    "models": array
  }
}
```

### Get User Workspaces

**GET /api/workspaces**

- Headers:

  - `Authorization`: Bearer token

- Response (200):

```json
{
  "success": true,
  "message": "Workspaces retrieved successfully",
  "statusCode": 200,
  "timestamp": string,
  "data": [
    {
      "id": integer,
      "name": string,
      "description": string,
      "created_at": string,
      "is_default": boolean,
      "user_id": integer,
      "models": array
    }
  ]
}
```

### Get Workspace by ID

**GET /api/workspaces/{workspace_id}**

- Headers:

  - `Authorization`: Bearer token

- Response (200):

```json
{
  "success": true,
  "message": "Workspace retrieved successfully",
  "statusCode": 200,
  "timestamp": string,
  "data": {
    "id": integer,
    "name": string,
    "description": string,
    "created_at": string,
    "is_default": boolean,
    "user_id": integer,
    "models": array
  }
}
```

### Update Workspace

**PUT /api/workspaces/{workspace_id}**

- Headers:

  - `Authorization`: Bearer token

- Request Body:

  - Any workspace fields to update

- Response (200):

```json
{
  "success": true,
  "message": "Workspace updated successfully",
  "statusCode": 200,
  "timestamp": string,
  "data": {
    "id": integer,
    "name": string,
    "description": string,
    "created_at": string,
    "is_default": boolean,
    "user_id": integer,
    "models": array
  }
}
```

### Delete Workspace

**DELETE /api/workspaces/{workspace_id}**

- Headers:

  - `Authorization`: Bearer token

- Response (204):

```json
{
  "success": true,
  "message": "Workspace deleted successfully",
  "statusCode": 204,
  "timestamp": string
}
```

### Get Workspace Models

**GET /api/workspaces/{workspace_id}/models**

- Headers:

  - `Authorization`: Bearer token

- Response (200):

```json
{
  "success": true,
  "message": "Workspace models retrieved successfully",
  "statusCode": 200,
  "timestamp": string,
  "data": [
    {
      "id": integer,
      "name": string,
      "developer": string,
      "model_type": string,
      "status": string,
      "date_interacted": string,
      "tags": array,
      "notes": string,
      "source_links": array,
      "parameters": integer,
      "license": string,
      "version": string,
      "user_id": integer,
      "workspace_id": integer,
      "username": string
    }
  ]
}
```

### Add Model to Workspace

**POST /api/workspaces/{workspace_id}/models/{model_id}**

- Headers:

  - `Authorization`: Bearer token

- Response (204):

```json
{
  "success": true,
  "message": "Model added to workspace successfully",
  "statusCode": 204,
  "timestamp": string
}
```

### Move Model Between Workspaces

**POST /api/workspaces/move-model**

- Headers:

  - `Authorization`: Bearer token

- Request Body:

```json
{
  "model_id": integer,
  "source_workspace_id": integer,
  "target_workspace_id": integer
}
```

- Response (204):

```json
{
  "success": true,
  "message": "Model moved successfully",
  "statusCode": 204,
  "timestamp": string
}
```

## Models

### Create Model

**POST /api/models/models**

- Headers:

  - `Authorization`: Bearer token

- Request Body:

```json
{
  "name": string (required),
  "developer": string (optional),
  "model_type": string (optional),
  "status": string (optional),
  "tags": array (optional),
  "notes": string (optional),
  "source_links": array (optional),
  "parameters": integer (optional),
  "license": string (optional),
  "version": string (optional),
  "workspace_id": integer (optional)
}
```

- Response (201):

```json
{
  "success": true,
  "message": "Model created successfully",
  "statusCode": 201,
  "timestamp": string,
  "data": {
    "id": integer,
    "name": string,
    "developer": string,
    "model_type": string,
    "status": string,
    "date_interacted": string,
    "tags": array,
    "notes": string,
    "source_links": array,
    "parameters": integer,
    "license": string,
    "version": string,
    "user_id": integer,
    "workspace_id": integer,
    "username": string
  }
}
```

### Get Models

**GET /api/models/models**

- Headers:

  - `Authorization`: Bearer token

- Query Parameters:

  - `workspace_id`: Filter by workspace (integer, optional)
  - `query`: Search query (string, optional)
  - `model_type`: Filter by model type (string, optional)
  - `tags`: Filter by tags (array, optional)

- Response (200):

```json
{
  "success": true,
  "message": "Models retrieved successfully",
  "statusCode": 200,
  "timestamp": string,
  "data": [
    {
      "id": integer,
      "name": string,
      "developer": string,
      "model_type": string,
      "status": string,
      "date_interacted": string,
      "tags": array,
      "notes": string,
      "source_links": array,
      "parameters": integer,
      "license": string,
      "version": string,
      "user_id": integer,
      "workspace_id": integer,
      "username": string
    }
  ]
}
```

### Get Model by ID

**GET /api/models/models/{model_id}**

- Headers:

  - `Authorization`: Bearer token

- Response (200):

```json
{
  "success": true,
  "message": "Model retrieved successfully",
  "statusCode": 200,
  "timestamp": string,
  "data": {
    "id": integer,
    "name": string,
    "developer": string,
    "model_type": string,
    "status": string,
    "date_interacted": string,
    "tags": array,
    "notes": string,
    "source_links": array,
    "parameters": integer,
    "license": string,
    "version": string,
    "user_id": integer,
    "workspace_id": integer,
    "username": string
  }
}
```

### Update Model

**PUT /api/models/models/{model_id}**

- Headers:

  - `Authorization`: Bearer token

- Request Body:

  - Any model fields to update

- Response (200):

```json
{
  "success": true,
  "message": "Model updated successfully",
  "statusCode": 200,
  "timestamp": string,
  "data": {
    "id": integer,
    "name": string,
    "developer": string,
    "model_type": string,
    "status": string,
    "date_interacted": string,
    "tags": array,
    "notes": string,
    "source_links": array,
    "parameters": integer,
    "license": string,
    "version": string,
    "user_id": integer,
    "workspace_id": integer,
    "username": string
  }
}
```

### Delete Model

**DELETE /api/models/models/{model_id}**

- Headers:

  - `Authorization`: Bearer token

- Response (204):

```json
{
  "success": true,
  "message": "Model deleted successfully",
  "statusCode": 204,
  "timestamp": string
}
```

### Update Model Tags

**PUT /api/models/models/{model_id}/tags**

- Headers:

  - `Authorization`: Bearer token

- Request Body:

```json
{
  "tags": array
}
```

- Response (200):

```json
{
  "success": true,
  "message": "Tags updated successfully",
  "statusCode": 200,
  "timestamp": string,
  "data": {
    "id": integer,
    "name": string,
    "developer": string,
    "model_type": string,
    "status": string,
    "date_interacted": string,
    "tags": array,
    "notes": string,
    "source_links": array,
    "parameters": integer,
    "license": string,
    "version": string,
    "user_id": integer,
    "workspace_id": integer,
    "username": string
  }
}
```

### Get Model Types

**GET /api/models/models/types**

- Headers:

  - `Authorization`: Bearer token

- Response (200):

```json
{
  "success": true,
  "message": "Model types retrieved successfully",
  "statusCode": 200,
  "timestamp": string,
  "data": array[string]
}
```

### Get All Tags

**GET /api/models/models/tags**

- Headers:

  - `Authorization`: Bearer token

- Response (200):

```json
{
  "success": true,
  "message": "Tags retrieved successfully",
  "statusCode": 200,
  "timestamp": string,
  "data": array[string]
}
```

### Bulk Update Workspace

**POST /api/models/models/bulk-workspace-update**

- Headers:

  - `Authorization`: Bearer token

- Request Body:

```json
{
  "model_ids": array[integer],
  "target_workspace_id": integer
}
```

- Response (200):

```json
{
  "success": true,
  "message": "Successfully moved models to workspace",
  "statusCode": 200,
  "timestamp": string
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

## Error Response Format

All error responses follow this format:

```json
{
  "success": false,
  "message": string,
  "statusCode": number,
  "timestamp": string,
  "error": string (optional)
}
```
