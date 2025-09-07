from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from openai import OpenAI
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI(title="Caroline Sarkki Portfolio API", version="1.0.0")

# Initialize OpenAI client (will be created when needed)
client = None

class QueryRequest(BaseModel):
    query: str

def get_openai_client():
    """Get OpenAI client, creating it if needed"""
    global client
    if client is None:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise HTTPException(status_code=500, detail="OpenAI API key not configured")
        client = OpenAI(api_key=api_key)
    return client

def load_knowledge():
    """Load the knowledge file content"""
    try:
        with open("knowledge.txt", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return "Knowledge file not found"

@app.get("/health")
async def health_check():
    """Health check endpoint for Railway"""
    return {"status": "healthy", "message": "API is running"}

@app.get("/")
async def root():
    """Homepage with API information"""
    return {
        "message": "Welcome to Caroline Sarkki's Portfolio API",
        "description": "This API provides information about Caroline Sarkki, a full stack software engineer with 3+ years of experience at KQED.",
        "endpoints": {
            "/query": {
                "method": "POST",
                "description": "Send a query about Caroline Sarkki's background, experience, or projects",
                "request_body": {
                    "query": "string - Your question about Caroline's experience, projects, or background"
                }
            },
            "/health": {
                "method": "GET",
                "description": "Health check endpoint"
            }
        },
        "contact": {
            "linkedin": "https://www.linkedin.com/in/caroline-sarkki-2a5517126/",
            "portfolio": "https://chocoloco123.github.io/index.html",
            "github": "https://github.com/Chocoloco123",
            "email": "csarkki.swe@gmail.com"
        }
    }

@app.post("/query")
async def query_caroline_info(request: QueryRequest):
    """Process queries about Caroline Sarkki using OpenAI"""
    try:
        # Get OpenAI client
        openai_client = get_openai_client()
        
        # Load knowledge base
        knowledge_content = load_knowledge()
        
        # Prepare the prompt for OpenAI
        prompt = f"""Based on the following information about Caroline Sarkki, please answer the user's query:

{knowledge_content}

User Query: {request.query}

Please provide a helpful and accurate response based on the information provided above. If the query is not related to Caroline's professional background, experience, or projects, please politely redirect the conversation back to her professional information."""

        # Call OpenAI API
        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that provides information about Caroline Sarkki, a full stack software engineer. Always be professional and accurate in your responses."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500,
            temperature=0.7
        )
        
        return {
            "query": request.query,
            "response": response.choices[0].message.content,
            "model_used": "gpt-4o-mini"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    print(f"Starting server on port {port}")
    print(f"Environment: PORT={os.getenv('PORT')}")
    print(f"OpenAI API Key configured: {bool(os.getenv('OPENAI_API_KEY'))}")
    uvicorn.run(app, host="0.0.0.0", port=port)
