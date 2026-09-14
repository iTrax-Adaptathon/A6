import json
import uuid
from typing import List
from models.schemas import Transcript, Claim
from api.ollama_client import ask_ollama

def extract_claims(transcript: Transcript) -> List[Claim]:
    """
    Analyzes segments from the transcript to extract core claims and classify them.
    """
    claims: List[Claim] = []
    
    for segment in transcript.segments:
        if not segment.text.strip():
            continue

        prompt = f"""
        Analyze the following text spoken by {segment.speaker} and extract the main propositions or claims made.
        Return the result ONLY as a JSON array of objects.
        Each object should have:
        - "claim_text": The claim or assertion made.
        - "claim_type": The type of claim (must be one of: "factual", "moral", "policy", "definition").
        
        Speaker: {segment.speaker}
        Text: "{segment.text}"
        """
        
        response_text = ask_ollama(prompt, json_format=True)
        
        try:
            extracted_data = json.loads(response_text)
            
            # Normalize response if the model wrapped the list in a dictionary key
            if isinstance(extracted_data, dict):
                extracted_data = (
                    extracted_data.get("claims")
                    or extracted_data.get("propositions")
                    or extracted_data.get("data")
                    or [extracted_data]
                )

            if not isinstance(extracted_data, list):
                extracted_data = [extracted_data]
            
            for item in extracted_data:
                if isinstance(item, dict) and "claim_text" in item and item["claim_text"]:
                    claim_type = item.get("claim_type", "factual")
                    if str(claim_type).lower() not in ["factual", "moral", "policy", "definition"]:
                        claim_type = "factual"

                    claims.append(Claim(
                        claim_id=str(uuid.uuid4()),
                        speaker=segment.speaker,
                        segment_id=segment.segment_id,
                        claim_text=str(item["claim_text"]).strip(),
                        claim_type=str(claim_type).lower()
                    ))
        except (json.JSONDecodeError, TypeError, KeyError) as e:
            print(f"[Claims Extraction Error] Failed to parse response for segment {segment.segment_id}: {e}")
            continue

    return claims
