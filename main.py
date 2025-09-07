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

Please provide a helpful and accurate response based on the information provided above. Format your response using HTML tags for better readability:

- Use <p> tags for paragraphs
- Use <ul> and <li> tags for lists
- Use <strong> tags for bold/important text
- Use <code> tags for technical terms, languages, and technologies
- Use <h3> tags for section headers when appropriate

Example formats:
- For lists: "<p>Here are Caroline's projects:</p><ul><li><strong>Project Name</strong>: Description</li></ul>"
- For technologies: "<p>Caroline uses <code>React</code>, <code>Python</code>, and <code>PostgreSQL</code></p>"
- For structured content: "<p>Caroline's experience includes:</p><ul><li><strong>Frontend</strong>: <code>JavaScript</code>, <code>React</code></li><li><strong>Backend</strong>: <code>Python</code>, <code>Java</code></li></ul>"

If the query is not related to Caroline's professional background, experience, or projects, please politely redirect the conversation back to her professional information."""

        # Call OpenAI API
        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are Caroline Sarkki's helpful robot assistant. You speak in first person as her AI helper, providing information about Caroline's background, experience, and projects. Always be professional, friendly, and accurate in your responses. Use phrases like 'I can tell you about Caroline's experience with...' or 'Based on Caroline's background, I can share that...'"},
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
