import json
import uuid
from typing import List, Dict, Any
from models.schemas import Claim, Transcript, Rebuttal
from api.ollama_client import ask_ollama

def parse_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in ["true", "yes", "1"]
    if isinstance(value, (int, float)):
        return bool(value)
    return False

def analyze_rebuttals(claims: List[Claim], transcript: Transcript) -> List[Rebuttal]:
    """
    Identifies interactions where a speaker addresses, counters, deflects,
    or concedes to an existing claim made by another speaker.
    """
    rebuttals: List[Rebuttal] = []
    
    if len(claims) < 2:
        return rebuttals

    valid_claim_ids = {c.claim_id for c in claims}
        
    claims_json = json.dumps([
        {"id": c.claim_id, "speaker": c.speaker, "text": c.claim_text} 
        for c in claims
    ])
    
    prompt = f"""
    Analyze the following list of claims and statements from the participants.
    Identify instances where a speaker directly addresses, counters, deflects, or concedes to a claim made by another speaker.
    Return the result ONLY as a JSON array of objects.
    Each object should have:
    - "responding_speaker": The speaker offering the response.
    - "target_claim_id": The exact ID of the original claim being addressed from the list.
    - "rebuttal_text": A brief description or excerpt of the counter-argument or response.
    - "type": One of "direct", "deflection", or "concession".
    - "survived": Boolean, true if the response effectively stands without being refuted, false otherwise.
    
    Claims:
    {claims_json}
    """
    
    response_text = ask_ollama(prompt, json_format=True)
    
    try:
        extracted_data = json.loads(response_text)
        
        # Normalize wrapper keys
        if isinstance(extracted_data, dict):
            extracted_data = (
                extracted_data.get("rebuttals")
                or extracted_data.get("responses")
                or extracted_data.get("data")
                or [extracted_data]
            )
            
        if not isinstance(extracted_data, list):
            extracted_data = [extracted_data]
            
        for item in extracted_data:
            if not isinstance(item, dict):
                continue

            target_id = item.get("target_claim_id")
            responding_speaker = item.get("responding_speaker")

            # Check for minimum required response fields
            if responding_speaker and target_id in valid_claim_ids:
                rebuttal_type = str(item.get("type", "direct")).lower()
                if rebuttal_type not in ["direct", "deflection", "concession"]:
                    rebuttal_type = "direct"

                rebuttals.append(Rebuttal(
                    rebuttal_id=str(uuid.uuid4()),
                    responding_speaker=str(responding_speaker),
                    target_claim_id=str(target_id),
                    rebuttal_text=str(item.get("rebuttal_text", "")).strip(),
                    type=rebuttal_type,
                    survived=parse_bool(item.get("survived", False))
                ))
    except (json.JSONDecodeError, TypeError, KeyError) as e:
        print(f"[Counter-Response Error] Failed to parse rebuttals: {e}")
        
    return rebuttals
