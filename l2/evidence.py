import json
import uuid
from typing import List, Dict
from models.schemas import Claim, Evidence, Transcript
from api.ollama_client import ask_ollama

def extract_evidence(claims: List[Claim], transcript: Transcript) -> List[Evidence]:
    """
    Examines context around each claim to extract citations, statistics, anecdotes, or studies.
    """
    all_evidence: List[Evidence] = []
    
    # Map segment_id to segment text for fast context retrieval
    segment_map: Dict[str, str] = {seg.segment_id: seg.text for seg in transcript.segments}
    
    for claim in claims:
        segment_text = segment_map.get(claim.segment_id, "")
        
        prompt = f"""
        Analyze the following claim and the accompanying source context.
        Identify any evidence, citations, data, or supporting material provided to support the claim.
        Return the result ONLY as a JSON array of objects.
        If no supporting evidence is provided, return an empty array [].
        Each object should have:
        - "evidence_text": The text of the supporting evidence.
        - "source": The cited source or attribution (if explicitly mentioned, otherwise null).
        - "evidence_type": Type of evidence (statistic, quote, anecdote, study).
        
        Claim: "{claim.claim_text}"
        Context: "{segment_text}"
        """
        
        response_text = ask_ollama(prompt, json_format=True)
        
        try:
            extracted_data = json.loads(response_text)
            
            # Normalize dictionary wrapper patterns
            if isinstance(extracted_data, dict):
                extracted_data = (
                    extracted_data.get("evidence")
                    or extracted_data.get("data")
                    or [extracted_data]
                )
                
            if not isinstance(extracted_data, list):
                extracted_data = [extracted_data]
            
            for item in extracted_data:
                if isinstance(item, dict) and item.get("evidence_text"):
                    ev_type = str(item.get("evidence_type", "anecdote")).lower()
                    if ev_type not in ["statistic", "quote", "anecdote", "study"]:
                        ev_type = "anecdote"

                    all_evidence.append(Evidence(
                        evidence_id=str(uuid.uuid4()),
                        claim_id=claim.claim_id,
                        speaker=claim.speaker,
                        evidence_text=str(item["evidence_text"]).strip(),
                        source=item.get("source"),
                        evidence_type=ev_type
                    ))
        except (json.JSONDecodeError, TypeError, KeyError) as e:
            print(f"[Evidence Extraction Error] Failed to parse evidence for claim {claim.claim_id}: {e}")
            continue
            
    return all_evidence
