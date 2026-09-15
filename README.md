# A6
# Debate AI Adjudicator

An automated debate referee, argument-mining, and fact-checking engine powered by FastAPI and local LLMs via Ollama[cite: 4, 7].

The system ingests raw multi-speaker transcripts, extracts factual/moral/policy claims, identifies citations and evidence, performs live web fact-checking, maps rebuttals and concessions, and calculates multi-dimensional evaluation scores to determine a winner[cite: 8, 9, 10, 11, 12, 13, 15].

---

## Architecture Pipeline
PrerequisitesPython 3.10+ installed.  Ollama installed and running locally:Download: https://ollama.comPull the default model:Bashollama pull llama3.2
Installation & SetupClone the repository:Bashgit clone [https://github.com/your-username/debate-ai-adjudicator.git](https://github.com/your-username/debate-ai-adjudicator.git)
cd debate-ai-adjudicator
Create and activate a virtual environment:Bash# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
Install dependencies:Bashpip install -r requirements.txt
Configure environment variables:
Copy .env.example to .env:  Bashcp .env.example .env
Default .env contents:  Ini, TOMLOLLAMA_MODEL=llama3.2
OLLAMA_URL=http://localhost:11434
Running the ApplicationMake sure Ollama is active:Bashollama run llama3.2
Start the FastAPI backend server:Bashuvicorn main:app --reload --port 8000
Open your browser:Frontend UI: http://127.0.0.1:8000/Interactive API Docs (Swagger UI): http://127.0.0.1:8000/docsAPI Usage ExampleEndpoint: POST /analyze  Request Body:JSON{
  "transcript_text": "Alice: Global renewable installations surged by 50 percent last year according to the IEA.\nBob: That is true, but base load demands still rely heavily on fossil fuels during peak evening hours.\nAlice: Battery storage costs have dropped significantly to cover those exact peaks."
}
Response Format:JSON{
  "evaluation": {
    "speaker_a": {
      "logical_consistency": 82,
      "evidence_quality": 80,
      "rebuttal_strength": 75,
      "relevance": 85,
      "clarity": 80,
      "overall": 80
    },
    "speaker_b": {
      "logical_consistency": 72,
      "evidence_quality": 68,
      "rebuttal_strength": 70,
      "relevance": 78,
      "clarity": 75,
      "overall": 73
    },
    "winner": "Alice",
    "reason": "Alice supported key arguments with verifiable industry statistics."
  },
  "claims": [...],
  "evidence": [...],
  "fact_checks": [...],
  "rebuttals": [...]
}
