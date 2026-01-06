import httpx
import json
from typing import Dict, List, Optional
from app.core.config import get_settings

settings = get_settings()


class OllamaService:
    def __init__(self):
        self.ollama_host = settings.ollama_host
        self.model = settings.ollama_model

    async def check_connection(self) -> bool:
        """Check if Ollama is available."""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(f"{self.ollama_host}/api/tags")
                return response.status_code == 200
        except Exception:
            return False

    async def pull_model(self, model: str) -> bool:
        """Pull a model if not already available."""
        try:
            async with httpx.AsyncClient(timeout=600.0) as client:
                response = await client.post(
                    f"{self.ollama_host}/api/pull",
                    json={"name": model}
                )
                return response.status_code == 200
        except Exception as e:
            print(f"Error pulling model: {e}")
            return False

    async def reason_about_match(
        self,
        usage_title: str,
        usage_songwriter: str,
        work_title: str,
        work_songwriters: List[str],
        similarity_scores: Dict[str, float]
    ) -> Dict:
        """Use LLM to reason about whether two works match."""

        prompt = f"""You are an expert at matching music works. Analyze if these two entries refer to the same musical work.

USAGE FILE ENTRY:
- Title: "{usage_title}"
- Songwriter: "{usage_songwriter}"

DATABASE WORK:
- Title: "{work_title}"
- Songwriters: {', '.join(work_songwriters)}

SIMILARITY SCORES:
- Title similarity: {similarity_scores.get('title', 0):.2%}
- Songwriter similarity: {similarity_scores.get('songwriter', 0):.2%}
- Vector similarity: {similarity_scores.get('vector', 0):.2%}

Consider:
1. Title variations (abbreviations, punctuation, "the", etc.)
2. Songwriter name variations (initials, order, spelling)
3. Common music industry data entry patterns

Respond with ONLY valid JSON in this exact format:
{{"is_match": true/false, "confidence": 0.0-1.0, "reasoning": "brief explanation"}}"""

        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(
                    f"{self.ollama_host}/api/generate",
                    json={
                        "model": self.model,
                        "prompt": prompt,
                        "stream": False,
                        "options": {
                            "temperature": 0.1,
                            "num_predict": 200
                        }
                    }
                )
                response.raise_for_status()
                data = response.json()
                response_text = data.get("response", "").strip()

                # Try to parse JSON from response
                try:
                    # Find JSON in response
                    start = response_text.find("{")
                    end = response_text.rfind("}") + 1
                    if start >= 0 and end > start:
                        json_str = response_text[start:end]
                        result = json.loads(json_str)
                        return {
                            "is_match": result.get("is_match", False),
                            "confidence": float(result.get("confidence", 0)),
                            "reasoning": result.get("reasoning", "")
                        }
                except json.JSONDecodeError:
                    pass

                return {
                    "is_match": False,
                    "confidence": 0,
                    "reasoning": f"Failed to parse AI response: {response_text[:100]}"
                }

        except Exception as e:
            return {
                "is_match": False,
                "confidence": 0,
                "reasoning": f"AI matching error: {str(e)}"
            }

    async def analyze_batch_matches(
        self,
        candidates: List[Dict]
    ) -> List[Dict]:
        """Analyze multiple potential matches at once."""
        results = []
        for candidate in candidates:
            result = await self.reason_about_match(
                usage_title=candidate["usage_title"],
                usage_songwriter=candidate["usage_songwriter"],
                work_title=candidate["work_title"],
                work_songwriters=candidate["work_songwriters"],
                similarity_scores=candidate["similarity_scores"]
            )
            results.append({
                "usage_record_id": candidate["usage_record_id"],
                "work_id": candidate["work_id"],
                **result
            })
        return results
