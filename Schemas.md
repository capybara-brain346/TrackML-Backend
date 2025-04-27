# Database Schemas

## ModelEntry

Represents a machine learning model entry in the system.

| Column           | Type            | Constraints      | Description                          |
|-----------------|-----------------|------------------|--------------------------------------|
| id              | Integer         | Primary Key      | Unique identifier for the model      |
| name            | String(120)     | Not Null        | Name of the model                    |
| developer       | String(120)     |                 | Developer/Creator of the model        |
| model_type      | String(50)      |                 | Type/Category of the model           |
| status          | String(50)      |                 | Current status of the model          |
| date_interacted | Date           |                 | Last interaction date                 |
| tags            | Array[String]   |                 | List of tags associated with model    |
| notes           | Text           |                 | Additional notes about the model      |
| source_links    | Array[String]   |                 | List of source/reference links        |
| parameters      | Integer        |                 | Number of model parameters            |
| license         | String(50)     |                 | License type of the model            |
| version         | String(50)     |                 | Version of the model                  |
| user_id         | Integer        | Foreign Key     | Reference to the owner user          |

## User

Represents a user in the system.

| Column         | Type          | Constraints                | Description                     |
|---------------|---------------|----------------------------|---------------------------------|
| id            | Integer       | Primary Key                | Unique identifier for the user  |
| username      | String(80)    | Unique, Not Null          | User's username                 |
| email         | String(120)   | Unique, Not Null          | User's email address           |
| password_hash | String(256)   | Not Null                  | Hashed password                 |
| is_active     | Boolean       | Default: True             | User account status             |
| created_at    | Date         | Default: Current Date     | Account creation date           |

### Relationships
- One User can have many ModelEntries (One-to-Many)
- Each ModelEntry belongs to one User (Many-to-One)
