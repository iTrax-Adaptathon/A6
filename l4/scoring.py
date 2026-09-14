import json
from typing import List, Any, Dict
from models.schemas import FinalEvaluation, SpeakerScore, Claim, Evidence, FactCheckResult, Rebuttal, Transcript
from api.ollama_client import ask_ollama

def safe_score(val: Any, default: int = 50) -> int:
    try:
        score = int(float(val))
        return max(0, min(100, score))
    except (ValueError, TypeError):
        return default

def build_speaker_score(data: Dict[str, Any]) -> SpeakerScore:
    return SpeakerScore(
        logical_consistency=safe_score(data.get("logical_consistency")),
        evidence_quality=safe_score(data.get("evidence_quality")),
        rebuttal_strength=safe_score(data.get("rebuttal_strength")),
        relevance=safe_score(data.get("relevance")),
        clarity=safe_score(data.get("clarity")),
        overall=safe_score(data.get("overall")),
    )

def generate_scores(
    transcript: Transcript,
    claims: List[Claim],
    evidence: List[Evidence],
    fact_checks: List[FactCheckResult],
    rebuttals: List[Rebuttal]
) -> FinalEvaluation:
    """
    Computes comparative debate evaluation scores across multiple argumentative dimensions.
    """
    # Extract unique speakers
    speakers = list(dict.fromkeys([seg.speaker for seg in transcript.segments if seg.speaker]))
    if len(speakers) < 2:
        speakers = ["Speaker A", "Speaker B"]
        
    speaker_a, speaker_b = speakers[0], speakers[1]
    
    data_summary = {
        "speaker_a": speaker_a,
        "speaker_b": speaker_b,
        "claims_count": len(claims),
        "evidence_count": len(evidence),
        "fact_checks": [{"id": fc.claim_id, "status": fc.status} for fc in fact_checks],
        "rebuttals_count": len(rebuttals)
    }
    
    prompt = f"""
    You are an objective analytical debate adjudicator. Analyze the provided summary of claims, evidence, verification results, and responses.
    Generate integer evaluation scores (from 0 to 100) for each speaker across the five dimensions.
    
    Speakers: {speaker_a} and {speaker_b}
    Analysis Summary: {json.dumps(data_summary)}
    
    Return ONLY a JSON object conforming strictly to this format:
    {{
      "speaker_a": {{
        "logical_consistency": 75,
        "evidence_quality": 80,
        "rebuttal_strength": 70,
        "relevance": 85,
        "clarity": 80,
        "overall": 78
      }},
      "speaker_b": {{
        "logical_consistency": 70,
        "evidence_quality": 65,
        "rebuttal_strength": 75,
        "relevance": 80,
        "clarity": 75,
        "overall": 73
      }},
      "winner": "{speaker_a}",
      "reason": "Detailed justification of the scoring outcome"
    }}
    """
    
    response_text = ask_ollama(prompt, json_format=True)
    
    try:
        data = json.loads(response_text)
        
        # Look for speaker data under standard keys, speaker names, or lowercase names
        s_a_raw = (
            data.get("speaker_a")
            or data.get(speaker_a)
            or data.get(speaker_a.lower())
            or {}
        )
        s_b_raw = (
            data.get("speaker_b")
            or data.get(speaker_b)
            or data.get(speaker_b.lower())
            or {}
        )
        
        winner = str(data.get("winner", "Tie")).strip()
        reason = str(data.get("reason", "Analysis completed based on logical structure and verification.")).strip()

        return FinalEvaluation(
            speaker_a=build_speaker_score(s_a_raw if isinstance(s_a_raw, dict) else {}),
            speaker_b=build_speaker_score(s_b_raw if isinstance(s_b_raw, dict) else {}),
            winner=winner,
            reason=reason
        )
    except (json.JSONDecodeError, TypeError, KeyError) as e:
        print(f"[Scoring Error] Failed to parse evaluation scores: {e}")
        return FinalEvaluation(
            speaker_a=SpeakerScore(),
            speaker_b=SpeakerScore(),
            winner="Tie",
            reason="Failed to parse detailed AI scoring metrics."
        )
