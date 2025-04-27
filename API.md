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
  "source": "huggingface" | "github",
  "identifier": string
}
```
- Response: Model information
- Errors:
  - 400: Missing source/identifier
  - 400: Invalid source
  - 404: Failed to extract information

### Get Model Insights
**GET /{id}/insights**
- Parameters:
  - `id`: Model ID (integer)
- Response: Model insights object
- Error (404): If model not found

### Compare Models
**POST /insights/compare**
- Request Body:
```json
{
  "model_ids": array[integer]
}
```
- Response: Comparison analysis
- Errors:
  - 400: No model IDs provided
  - 404: No models found
