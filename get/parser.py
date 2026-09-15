import re
import uuid
from typing import List
from models.schemas import TranscriptSegment, Transcript

def parse_transcript(raw_text: str) -> Transcript:
    """
    Splits raw transcript text into segments by speaker.
    Supports formats like:
      Speaker A: Hello world
      [Alice] Let's discuss...
      Bob - I disagree.
    """
    if not raw_text or not raw_text.strip():
        return Transcript(segments=[])

    lines = raw_text.strip().split("\n")
    segments: List[TranscriptSegment] = []
    
    current_speaker = None
    current_text = []

    # Pattern matches "Speaker Name:", "[Speaker Name]:", or "Speaker Name -"
    speaker_pattern = re.compile(r"^(\[?[A-Za-z0-9 _.-]{2,30}\]?)\s*[:\-]\s*(.*)$")

    for raw_line in lines:
        line = raw_line.strip()
        if not line:
            continue

        match = speaker_pattern.match(line)
        if match:
            # Save the previously accumulated segment
            if current_speaker and current_text:
                segments.append(
                    TranscriptSegment(
                        segment_id=str(uuid.uuid4()),
                        speaker=current_speaker,
                        text=" ".join(current_text).strip()
                    )
                )

            speaker_tag = match.group(1).strip("[] \t")
            initial_text = match.group(2).strip()

            current_speaker = speaker_tag
            current_text = [initial_text] if initial_text else []
        else:
            # Continuation of the current speaker's text
            if current_speaker:
                current_text.append(line)
            else:
                # If transcript starts without a speaker label, default to Speaker 1
                current_speaker = "Speaker 1"
                current_text.append(line)

    # Append the final segment
    if current_speaker and current_text:
        segments.append(
            TranscriptSegment(
                segment_id=str(uuid.uuid4()),
                speaker=current_speaker,
                text=" ".join(current_text).strip()
            )
        )

    return Transcript(segments=segments)
