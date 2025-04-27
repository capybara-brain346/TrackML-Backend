# AI Model Tracker – Product Development Map (Flask Version)

## 1. Product Goals

| Goal             | Description                                                         |
| ---------------- | ------------------------------------------------------------------- |
| Log Interactions | Let users record every model they’ve seen, used, or saved for later |
| Organize Models  | Filter/search/sort models by status, type, tags, and date           |
| Learn & Reflect  | Attach personal notes, impressions, and comparisons                 |
| Track Progress   | Visualize your exploration journey and revisit your thoughts        |

---

## 2. Key Features

### Milestone 1 – MVP

- [ ] CRUD model entries
- [ ] Dashboard view
- [ ] Filtered model list
- [ ] Notes and tagging
- [ ] Local storage or SQLite
- [ ] React + Tailwind responsive UI

### Milestone 2

- [ ] Autofill from HuggingFace or GitHub
- [ ] Timeline view
- [ ] Model status (Wishlist, Archived)
- [ ] Notes search
- [ ] Import/export (CSV/JSON)

### Milestone 3

- [ ] Compare models side-by-side
- [ ] Auth system (Flask-Login)
- [ ] Markdown note editor
- [ ] Browser extension/bookmarklet
- [ ] Dark mode

---

## 3. Tech Stack

### Frontend

- React + Vite
- TailwindCSS
- shadcn/ui or Chakra UI
- React Router

### Backend (Flask)

- Flask (API)
- Flask-SQLAlchemy (ORM)
- Flask-Migrate (DB migrations)
- Flask-CORS (Cross-origin setup)
- Flask-Login (Authentication)

### Database

- SQLite for MVP → PostgreSQL (for cloud)
- Alembic for migrations (via Flask-Migrate)

### Optional APIs

- HuggingFace Hub API
- GitHub Model Repo scraping
- PapersWithCode integration

---

## 4. Folder Structure

```
modelmate/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── models.py
│   │   ├── routes/
│   │   ├── services/
│   │   └── utils/
│   ├── migrations/
│   └── run.py
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── hooks/
│   │   └── App.tsx
├── .env
├── README.md
└── requirements.txt
```

---

## 5. Core Data Model

```python
class ModelEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    developer = db.Column(db.String(120))
    model_type = db.Column(db.String(50))  # LLM, Vision, etc.
    status = db.Column(db.String(50))  # Tried, Studied, etc.
    date_interacted = db.Column(db.Date)
    tags = db.Column(db.PickleType)  # list of tags
    notes = db.Column(db.Text)
    source_links = db.Column(db.PickleType)  # list of URLs
    parameters = db.Column(db.Integer, nullable=True)
    license = db.Column(db.String(50), nullable=True)
    version = db.Column(db.String(50), nullable=True)
```

---

## 6. Tasks Breakdown

### Setup & Infra

- [ ] Flask project setup
- [ ] Create DB models and schema
- [ ] Set up migrations
- [ ] CORS and API routes

### UI/UX

- [ ] Reusable model card component
- [ ] Filtering/search bar
- [ ] Dashboard summary
- [ ] Markdown editor
- [ ] Dark mode support

### API & Logic

- [ ] API: `/models`, `/models/:id`, `/notes`, `/search`
- [ ] Add model metadata enrichment endpoint
- [ ] Integrate Flask-Login for Milestone 3

### Testing

- [ ] Unit tests with Pytest
- [ ] Frontend tests (Vitest)
- [ ] E2E tests (Cypress)
- [ ] Type-safe TypeScript usage

---

## 7. Deployment

- [ ] Deploy backend to Render/Fly.io
- [ ] Frontend to Vercel/Netlify
- [ ] CI/CD via GitHub Actions
- [ ] Export and backup notes

---

## 8. Future Roadmap

- Embedding-based semantic search (OpenAI or SentenceTransformers)
- Gemini/Langchain summaries of model pages
- Shared/public pages for notes and collections
- Team collaboration features
- AI assistant for model suggestions

---
