import uuid
from typing import List
from models.schemas import TranscriptSegment, Transcript
import re
SPEAKER_LINE_PATTERN = re.compile(r'^([A-Za-z][A-Za-z0-9 ]{0,24}):\s*(.*)$')
def parse_transcript(raw_text: str) -> Transcript:
    """
    Splits the raw transcript text into segments by speaker.
    Expected format: 
    Speaker A: Hello
    Speaker B: Hi
    """
    lines = raw_text.strip().split('\n')
    segments = []
    
    current_speaker = None
    current_text = []
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # Simple heuristic: looking for "SpeakerName:" or similar at the start of a line
       match = SPEAKER_LINE_PATTERN.match(line)
if match:
    # Save previous segment
    if current_speaker:
        segments.append(TranscriptSegment(
            segment_id=str(uuid.uuid4()),
            speaker=current_speaker,
            text=" ".join(current_text)
        ))

    current_speaker = match.group(1).strip()
    current_text = [match.group(2).strip()]
else:
    if current_speaker:
        current_text.append(line)
                
    # Add last segment
    if current_speaker:
        segments.append(TranscriptSegment(
            segment_id=str(uuid.uuid4()),
            speaker=current_speaker,
            text=" ".join(current_text)
        ))
        
    return Transcript(segments=segments)
