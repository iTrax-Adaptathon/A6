from pydantic import BaseModel, Field
from typing import List, Optional, Dict

class TranscriptSegment(BaseModel):
    segment_id: str
    speaker: str
    text: str

class Transcript(BaseModel):
    segments: List[TranscriptSegment]

class Claim(BaseModel):
    claim_id: str
    speaker: str
    segment_id: str
    claim_text: str
    claim_type: str = Field(
        default="factual",
        description="e.g., factual, moral, policy, definition"
    )

class Evidence(BaseModel):
    evidence_id: str
    claim_id: str
    speaker: str
    evidence_text: str
    source: Optional[str] = None
    evidence_type: str = Field(
        default="anecdote",
        description="e.g., statistic, quote, anecdote, study"
    )

class FactCheckResult(BaseModel):
    claim_id: str
    status: str = Field(
        default="questionable",
        description="supported, unsupported, questionable, contradicted"
    )
    source_url: Optional[str] = None
    reasoning: str = ""

class Rebuttal(BaseModel):
    rebuttal_id: str
    responding_speaker: str
    target_claim_id: str
    rebuttal_text: str
    type: str = Field(
        default="direct",
        description="direct, deflection, concession"
    )
    survived: Optional[bool] = None

class SpeakerScore(BaseModel):
    logical_consistency: int = 50
    evidence_quality: int = 50
    rebuttal_strength: int = 50
    relevance: int = 50
    clarity: int = 50
    overall: int = 50

class FinalEvaluation(BaseModel):
    speaker_a: SpeakerScore = Field(default_factory=SpeakerScore)
    speaker_b: SpeakerScore = Field(default_factory=SpeakerScore)
    winner: str = "Tie"
    reason: str = "Analysis completed."

class AnalysisPipelineResult(BaseModel):
    evaluation: FinalEvaluation
    claims: List[Claim] = []
    evidence: List[Evidence] = []
    fact_checks: List[FactCheckResult] = []
    rebuttals: List[Rebuttal] = []
