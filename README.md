![ChatGPT Image Apr 26, 2025, 02_40_29 PM](https://github.com/user-attachments/assets/320afee0-1db2-4978-8fc4-28c8e1827e28)
# TrackML

TrackML is a comprehensive tool for tracking and managing machine learning models. It helps users keep track of models they've explored, studied, or plan to use in the future.

## Features

- 📝 Track ML model details including name, developer, type, and parameters
- 🏷️ Organize models with tags and status updates
- 🔍 Search and filter models by various criteria
- 📊 Dashboard view with model statistics and insights
- 🌙 Dark mode support
- 🤖 Auto-fill model information from HuggingFace
- 📈 Model insights and comparative analysis using Gemini AI
- 📱 Responsive design for all devices

## Tech Stack

### Frontend

- React + Vite
- TypeScript
- TailwindCSS
- React Router

### Backend

- Flask
- SQLAlchemy
- Google Gemini API
- HuggingFace API

## Getting Started

### Prerequisites

- Python 3.8+
- Node.js 16+
- npm/yarn

### Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python run.py
```

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

### Environment Variables

Create a `.env` file in the backend directory:

```
GOOGLE_API_KEY=your_gemini_api_key
HF_ACCESS_TOKEN=your_huggingface_token
```

## Project Structure

```
TrackML/
├── backend/
│   ├── models/        # Database models
│   ├── routes/        # API endpoints
│   ├── services/      # Business logic
│   └── config.py      # Configuration
├── frontend/
│   ├── src/
│   │   ├── components/  # Reusable UI components
│   │   ├── pages/       # Page components
│   │   ├── services/    # API client
│   │   └── types/       # TypeScript types
│   └── public/
```

## API Endpoints

- `GET /api/v1/` - List all models
- `GET /api/v1/<id>` - Get specific model
- `POST /api/v1/` - Create new model
- `PUT /api/v1/<id>` - Update model
- `DELETE /api/v1/<id>` - Delete model
- `GET /api/v1/search` - Search models
- `POST /api/v1/autofill` - Auto-fill model details

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
