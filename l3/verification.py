import json
import re
from typing import List, Dict
from models.schemas import Claim, Evidence, FactCheckResult
from api.ollama_client import ask_ollama

try:
    from ddgs import DDGS
except ImportError:
    try:
        from duckduckgo_search import DDGS
    except ImportError:
        DDGS = None

def check_facts(claims: List[Claim], evidence_list: List[Evidence]) -> List[FactCheckResult]:
    """
    Cross-references factual claims against live web search snippets via DuckDuckGo.
    """
    results: List[FactCheckResult] = []
    
    # Map claim_id to Claim object
    claim_map: Dict[str, Claim] = {c.claim_id: c for c in claims}
    processed_claim_ids = set()
    
    # Only verify factual claims
    for ev in evidence_list:
        claim = claim_map.get(ev.claim_id)
        if not claim or claim.claim_type.lower() != "factual":
            continue
            
        if claim.claim_id in processed_claim_ids:
            continue
        processed_claim_ids.add(claim.claim_id)

        # 1. Clean and truncate search query
        clean_text = re.sub(r'["\']', '', claim.claim_text).strip()
        words = clean_text.split()[:8]
        search_query = " ".join(words)
        
        search_results = []
        if DDGS is not None and search_query:
            try:
                with DDGS() as ddgs:
                    for r in ddgs.text(search_query, max_results=3):
                        search_results.append(r)
            except Exception as e:
                print(f"[Search Warning] DDG search failed for query '{search_query}': {e}")

        # If no search results could be retrieved
        if not search_results:
            results.append(FactCheckResult(
                claim_id=claim.claim_id,
                status="unsupported",
                source_url=None,
                reasoning="No external sources found or search engine unavailable to verify the claim."
            ))
            continue

        # 2. Ollama evaluates reference material
        search_context = "\n".join([
            f"Source ({r.get('href', 'unknown')}): {r.get('body', '')}"
            for r in search_results
        ])
        
        prompt = f"""
        Evaluate whether the provided reference material supports, contradicts, or leaves questionable the given claim and supporting evidence.
        Return the result ONLY as a JSON object with:
        - "status": One of "supported", "unsupported", "questionable", "contradicted"
        - "reasoning": A concise explanation of the evaluation

        Claim: "{claim.claim_text}"
        Evidence: "{ev.evidence_text}"
        
        Reference Material:
        {search_context}
        """
        
        response_text = ask_ollama(prompt, json_format=True)
        try:
            data = json.loads(response_text)
            status = str(data.get("status", "questionable")).lower()
            if status not in ["supported", "unsupported", "questionable", "contradicted"]:
                status = "questionable"
                
            results.append(FactCheckResult(
                claim_id=claim.claim_id,
                status=status,
                source_url=search_results[0].get("href"),
                reasoning=str(data.get("reasoning", "Verification evaluation completed.")).strip()
            ))
        except (json.JSONDecodeError, TypeError, KeyError) as e:
            print(f"[Verification Error] Failed to parse fact-check JSON for claim {claim.claim_id}: {e}")
            results.append(FactCheckResult(
                claim_id=claim.claim_id,
                status="questionable",
                source_url=search_results[0].get("href") if search_results else None,
                reasoning="Failed to parse AI evaluation of fact check."
            ))
            
    return results
