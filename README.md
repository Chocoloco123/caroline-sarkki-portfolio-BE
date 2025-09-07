# Caroline Sarkki Portfolio API

A simple FastAPI-based backend service that provides information about Caroline Sarkki's professional background using OpenAI's GPT-4o-mini model.

## Features

- **Homepage (`/`)**: Provides API information and available endpoints
- **Query Endpoint (`/query`)**: Accepts queries about Caroline's background and returns AI-generated responses
- **OpenAI Integration**: Uses GPT-4o-mini model for intelligent responses
- **Docker Support**: Fully containerized with Docker and Docker Compose

## Setup

### Prerequisites

- Python 3.11+
- Docker and Docker Compose (optional)
- OpenAI API key

### Local Development

1. **Clone and navigate to the project directory**
   ```bash
   cd caroline_sarkki_portfolio_BE
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env and add your OpenAI API key
   ```

5. **Run the application**
   ```bash
   python main.py
   ```

The API will be available at `http://localhost:8000`

### Docker Setup

1. **Set up environment variables**
   ```bash
   export OPENAI_API_KEY=your_openai_api_key_here
   ```

2. **Run with Docker Compose**
   ```bash
   docker-compose up --build
   ```

The API will be available at `http://localhost:8000`

## API Endpoints

### GET `/`
Returns information about the API and available endpoints.

### POST `/query`
Accepts a JSON body with a `query` field and returns an AI-generated response about Caroline's background.

**Request Body:**
```json
{
  "query": "What projects has Caroline worked on at KQED?"
}
```

**Response:**
```json
{
  "query": "What projects has Caroline worked on at KQED?",
  "response": "Caroline has worked on several key projects at KQED...",
  "model_used": "gpt-4o-mini"
}
```

## Project Structure

```
.
├── main.py                 # FastAPI application
├── requirements.txt        # Python dependencies
├── knowledge.txt          # Knowledge base about Caroline
├── Dockerfile             # Docker configuration
├── docker-compose.yml     # Docker Compose configuration
└── README.md              # This file
```

## Environment Variables

- `OPENAI_API_KEY`: Your OpenAI API key (required)

## Technologies Used

- **FastAPI**: Modern, fast web framework for building APIs
- **OpenAI**: AI model integration
- **Pydantic**: Data validation
- **Uvicorn**: ASGI server
- **Docker**: Containerization
