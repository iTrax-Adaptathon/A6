import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import analyze
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Debate AI Analyzer Backend")

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins; restrict to specific frontend URLs in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the debate analysis routes
app.include_router(analyze.router)

@app.get("/")
def read_root():
    return {
        "message": "App is running",
        "ollama_url": os.getenv("OLLAMA_URL", "http://localhost:11434"),
        "ollama_model": os.getenv("OLLAMA_MODEL", "llama3.2")
    }
