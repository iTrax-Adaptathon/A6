from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from get.parser import parse_transcript
from l1.claims import extract_claims
from l2.evidence import extract_evidence
from l3.verification import check_facts
from counter_response.analysis import analyze_rebuttals
from l4.scoring import generate_scores
from models.schemas import AnalysisPipelineResult

router = APIRouter(prefix="", tags=["Debate Analysis"])

class TranscriptRequest(BaseModel):
    transcript_text: str = Field(
        ...,
        description="Raw transcript text formatted by speaker turns (e.g., 'Speaker A: ...')",
        example="Speaker A: Global temperatures rose 1.1 degrees Celsius.\nSpeaker B: That study was questioned."
    )

@router.post("/analyze", response_model=AnalysisPipelineResult)
def analyze_debate(request: TranscriptRequest):
    """
    Executes the full debate processing pipeline:
    1. Parses transcript turns into speaker segments.
    2. Extracts factual, moral, and policy claims.
    3. Finds supporting citations and evidence.
    4. Runs web verification for factual assertions.
    5. Maps counter-responses and concessions.
    6. Produces multi-dimensional adjudication scores.
    """
    raw_text = request.transcript_text.strip()
    if not raw_text:
        raise HTTPException(status_code=400, detail="Transcript text cannot be empty.")
    
    try:
        # Step 1: Parse
        transcript = parse_transcript(raw_text)
        if not transcript.segments:
            raise HTTPException(
                status_code=422,
                detail="Could not detect speaker segments. Format input like 'Speaker Name: Statement'."
            )

        # Step 2: Claims extraction (L1)
        claims = extract_claims(transcript)

        # Step 3: Evidence extraction (L2)
        evidence = extract_evidence(claims, transcript)

        # Step 4: Fact check factual claims (L3)
        fact_checks = check_facts(claims, evidence)

        # Step 5: Counter-response tracking
        rebuttals = analyze_rebuttals(claims, transcript)

        # Step 6: Final evaluation & scoring (L4)
        evaluation = generate_scores(
            transcript=transcript,
            claims=claims,
            evidence=evidence,
            fact_checks=fact_checks,
            rebuttals=rebuttals
        )

        return AnalysisPipelineResult(
            evaluation=evaluation,
            claims=claims,
            evidence=evidence,
            fact_checks=fact_checks,
            rebuttals=rebuttals
        )

    except HTTPException:
        raise
    except Exception as e:
        print(f"[Analyze Route Error] Unhandled pipeline failure: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Pipeline processing failed: {str(e)}"
        )
