import os
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Optional
from dotenv import load_dotenv

# Load local environment variables from .env
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("main")

from career_service import CareerKnowledgeService
from ai_service import AIService

app = FastAPI(title="CareerGuide AI", description="Student Career Guidance Chatbot API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Services
career_service = CareerKnowledgeService()
ai_service = AIService(career_service)

# Pydantic Request Models
class MessageItem(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    message: str
    history: Optional[List[MessageItem]] = []

@app.post("/api/chat")
def chat_endpoint(request: ChatRequest):
    history_dicts = [{"role": item.role, "content": item.content} for item in request.history] if request.history else []
    result = ai_service.process_chat_request(request.message, history_dicts)
    return result

# Serve static frontend files if static directory exists
static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

    @app.get("/")
    def read_root():
        return FileResponse(os.path.join(static_dir, "index.html"))

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8080))
    logger.info(f"Starting CareerGuide AI server on port {port}...")
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
