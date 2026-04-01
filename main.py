from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from openai import OpenAI
import os
import traceback
from pathlib import Path
from dotenv import load_dotenv
import uvicorn

# Load environment variables
load_dotenv()

app = FastAPI(title="Caroline Sarkki Portfolio API", version="1.0.0")

# Configure CORS based on environment
environment = os.getenv("ENVIRONMENT", "development")
if environment == "production":
    # Production: only allow specific origins
    allowed_origins = [
        "https://caroline-sarkki-portfolio.vercel.app",
    ]
    # Allow additional origins from environment variable (comma-separated)
    # Useful for Vercel preview URLs which are dynamic
    additional_origins = os.getenv("ALLOWED_ORIGINS", "")
    if additional_origins:
        allowed_origins.extend([origin.strip() for origin in additional_origins.split(",")])
else:
    # Development: allow local frontend
    allowed_origins = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]

# Add CORS middleware
print(f"CORS Configuration - Environment: {environment}")
print(f"Allowed Origins: {allowed_origins}")
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    error_trace = traceback.format_exc()
    print(f"Unhandled exception: {str(exc)}")
    print(f"Traceback: {error_trace}")
    return JSONResponse(
        status_code=500,
        content={"detail": f"Internal server error"}
    )

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
        # Get the directory where this script is located
        script_dir = Path(__file__).parent
        knowledge_path = script_dir / "knowledge.txt"
        
        with open(knowledge_path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError as e:
        print(f"Error loading knowledge file: {e}")
        return "Knowledge file not found"
    except Exception as e:
        print(f"Error reading knowledge file: {e}")
        return "Error reading knowledge file"

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
        prompt = f"""Based on the following information about Caroline Sarkki, please answer the user's query naturally and concisely:

{knowledge_content}

User Query: {request.query}

**IMPORTANT GUIDELINES:**
- Keep responses brief and conversational
- For simple greetings like "hello" or "hi", respond with just: "Hi! I'm Clio, Caroline's AI assistant. How can I help you learn about her work?"
- For questions about hobbies, interests, personal life, what she does outside of work, what she does for fun, personal activities, professional background, experience, projects, or skills - ANSWER THE QUESTION directly based on the information provided. Do NOT redirect these questions.
- **IMPORTANT**: "hobbies", "outside of work", "personal interests", "what she does for fun", and "personal activities" all refer to the same thing - check the "Personal Interests" section in the knowledge base.
- Format your response using HTML tags for better readability:
  - Use <p> tags for paragraphs
  - Use <ul> and <li> tags for lists
  - Use <strong> tags for bold/important text
  - Use <code> tags for technical terms, languages, and technologies
- **Contact info questions** (how to reach Caroline, email, LinkedIn, portfolio, GitHub, socials): Use **exactly** this HTML structure and wording. Copy URLs from Contact Information in the knowledge base. Never show raw https:// URLs as visible text.
```html
<div class="contact-clio">
<h3>Contact Caroline</h3>
<p><strong>Email</strong><br /><a href="mailto:csarkki.swe@gmail.com">csarkki.swe@gmail.com</a></p>
<p><strong>LinkedIn</strong><br /><a href="https://www.linkedin.com/in/caroline-sarkki-2a5517126/" target="_blank" rel="noopener noreferrer">View Profile</a></p>
<p><strong>Portfolio</strong><br /><a href="https://caroline-sarkki-portfolio.vercel.app/" target="_blank" rel="noopener noreferrer">View Site</a></p>
<p><strong>GitHub</strong><br /><a href="https://github.com/Chocoloco123" target="_blank" rel="noopener noreferrer">View Profile</a></p>
</div>
```
Do not use bullet lists for this layout. Do not wrap contact URLs only in <code>.

**EXAMPLES:**
- If asked "what are her hobbies?" or "what does she do outside of work?" or "what are her interests?" or "what does she do for fun?" or "what does she do for personal activities?" → Answer with her hobbies from the Personal Interests section
- If asked "what does she do outside of work?" → Answer with her hobbies from the Personal Interests section
- If asked "what are her interests?" → Answer with her hobbies from the Personal Interests section
- If asked "what does she do?" → Briefly describe her role at KQED
- If asked "hello" → Just say hello back

Only redirect if the query is completely unrelated to Caroline (e.g., asking about the weather, other people, etc.)."""

        # Call OpenAI API
        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are Clio, Caroline Sarkki's friendly AI assistant. Answer questions directly and naturally. Keep responses brief and conversational.\n\n**CRITICAL: Answer questions about hobbies, interests, personal life, what she does outside of work, what she does for fun, personal activities, professional background, experience, projects, and skills. DO NOT redirect these questions - they are valid!**\n\n**IMPORTANT**: When asked about \"hobbies\", \"outside of work\", \"personal interests\", \"what she does for fun\", or \"personal activities\" - these all refer to the same thing. Check the \"Personal Interests\" section in the knowledge base and answer directly.\n\n**SKILL FORMATTING RULES:**\n\n1. **Bold Section Headings**: Use bold headings followed by comma-separated skills\n   - ✅ CORRECT: `<p><strong>Frontend:</strong> JavaScript, React, TypeScript, Redux</p>`\n   - ✅ CORRECT: `<p><strong>Backend:</strong> Java, Python, Express, FastAPI</p>`\n\n2. **Clean Skills**: Remove any trailing text like \"and\", commas, or periods from individual skills\n   - Clean: \"JavaScript\" not \"JavaScript,\"\n   - Clean: \"React\" not \"React and\"\n\n3. **HTML Structure**: Use this exact format for skill sections:\n   ```html\n   <p><strong>Frontend:</strong> JavaScript, React, TypeScript, Redux</p>\n   <p><strong>Backend:</strong> Java, Python, Express, FastAPI</p>\n   ```\n\n**EXAMPLES:**\n\n**Frontend Skills:**\n```html\n<p><strong>Frontend:</strong> JavaScript, TypeScript, React, Redux, Sass, CSS, A11y</p>\n```\n\n**Backend Skills:**\n```html\n<p><strong>Backend:</strong> Java, Python, Express, FastAPI, Flask, Spring Boot, Sequelize, SQLAlchemy</p>\n```\n\n**Testing & Tools:**\n```html\n<p><strong>Testing:</strong> Jest, Mocha, Postman</p>\n<p><strong>Tools:</strong> Git, Docker, Agile Methodologies, Version Control</p>\n```\n\n**IMPORTANT NOTES:**\n- Use `<strong>` tags for category names with colons\n- Separate skills with commas and spaces\n- Keep \"Agile Methodologies\" as one complete phrase\n- Use `<p>` tags for clean paragraph formatting\n- Always close HTML tags properly\n- Keep responses brief - especially for greetings (1-2 sentences max)\n\nApply this formatting to ALL skill-related responses about Caroline's technical expertise."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=300,
            temperature=0.7
        )

        return {
            "query": request.query,
            "response": response.choices[0].message.content,
            "model_used": "gpt-4o-mini"
        }

    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        # Log the full error for debugging
        error_trace = traceback.format_exc()
        print(f"Error processing query: {str(e)}")
        print(f"Traceback: {error_trace}")
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    reload = os.getenv("ENVIRONMENT", "development") == "development"
    print(f"Starting server on port {port}")
    print(f"Environment: PORT={os.getenv('PORT')}")
    print(f"Auto-reload: {reload}")
    print(f"OpenAI API Key configured: {bool(os.getenv('OPENAI_API_KEY'))}")
    
    if reload:
        # Use import string for reload to work
        uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
    else:
        # Use app object directly when not reloading
        uvicorn.run(app, host="0.0.0.0", port=port, reload=False)
