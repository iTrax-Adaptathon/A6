import json
import uuid
from typing import List, Dict
from models.schemas import Claim, Transcript, Rebuttal
from api.ollama_client import ask_ollama
def analyze_rebuttals(claims: List[Claim], transcript: Transcript) -> List[Rebuttal]:
    rebuttals = []
    if len(claims) < 2:
        return rebuttals
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
    - "target_claim_id": The ID of the original claim being addressed.
    - "rebuttal_text": A brief description or excerpt of the counter-argument or response.
    - "type": One of "direct", "deflection", or "concession".
    - "survived": Boolean, true if the response effectively stands without being refuted, false otherwise.
    Claims:
    {claims_json}
    """
    response_text = ask_ollama(prompt, json_format=True)
    try:
        extracted_data = json.loads(response_text)
        if not isinstance(extracted_data, list):
            if 'rebuttals' in extracted_data:
                extracted_data = extracted_data['rebuttals']
            else:
                extracted_data = [extracted_data]
        for item in extracted_data:
            if 'responding_speaker' in item and 'target_claim_id' in item:
                rebuttals.append(Rebuttal(
                    rebuttal_id=str(uuid.uuid4()),
                    responding_speaker=item['responding_speaker'],
                    target_claim_id=item['target_claim_id'],
                    rebuttal_text=item.get('rebuttal_text', ''),
                    type=item.get('type', 'direct'),
                    survived=item.get('survived')
                ))
    except json.JSONDecodeError:
        print(f"Failed to parse JSON from Ollama for Counter-Response: {response_text}")
    return rebuttals
