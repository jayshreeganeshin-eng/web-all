"""
AI Integration Engine for web-all.
Supports multiple free AI providers: OpenRouter, Groq, HuggingFace, Ollama (local).
All features work with or without AI enabled.
"""

import asyncio
import json
from pathlib import Path
from typing import Any, Dict, List, Optional

import aiohttp


class AIProvider:
    """Base class for AI providers."""

    def __init__(self, api_key: Optional[str] = None, base_url: str = ""):
        self.api_key = api_key
        self.base_url = base_url

    async def generate(
        self, prompt: str, system_prompt: str = "You are a helpful assistant."
    ) -> str:
        raise NotImplementedError


class OpenRouterProvider(AIProvider):
    """OpenRouter.ai - Free tier available with multiple models."""

    def __init__(self, api_key: str):
        super().__init__(api_key, "https://openrouter.ai/api/v1")

    async def generate(
        self,
        prompt: str,
        system_prompt: str = "You are a helpful assistant.",
        model: str = "mistralai/mistral-7b-instruct:free",
    ) -> str:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://web-all.local",
        }

        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt},
            ],
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/chat/completions", headers=headers, json=payload
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return data["choices"][0]["message"]["content"]
                else:
                    error_text = await resp.text()
                    raise Exception(f"OpenRouter error: {resp.status} - {error_text}")


class GroqProvider(AIProvider):
    """Groq Cloud - Free tier with Llama models."""

    def __init__(self, api_key: str):
        super().__init__(api_key, "https://api.groq.com/openai/v1")

    async def generate(
        self,
        prompt: str,
        system_prompt: str = "You are a helpful assistant.",
        model: str = "llama3-8b-8192",
    ) -> str:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt},
            ],
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/chat/completions", headers=headers, json=payload
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return data["choices"][0]["message"]["content"]
                else:
                    error_text = await resp.text()
                    raise Exception(f"Groq error: {resp.status} - {error_text}")


class HuggingFaceProvider(AIProvider):
    """HuggingFace Inference API - Free tier available."""

    def __init__(self, api_key: str, model: str = "mistralai/Mistral-7B-Instruct-v0.2"):
        super().__init__(api_key, "https://api-inference.huggingface.co/models")
        self.model = model

    async def generate(
        self, prompt: str, system_prompt: str = "You are a helpful assistant."
    ) -> str:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        full_prompt = f"{system_prompt}\n\nUser: {prompt}\nAssistant:"
        payload = {
            "inputs": full_prompt,
            "parameters": {"max_new_tokens": 512, "temperature": 0.7, "return_full_text": False},
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/{self.model}", headers=headers, json=payload
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    if isinstance(data, list) and len(data) > 0:
                        return data[0].get("generated_text", "")
                    return str(data)
                else:
                    error_text = await resp.text()
                    raise Exception(f"HuggingFace error: {resp.status} - {error_text}")


class OllamaProvider(AIProvider):
    """Ollama - Local AI server (completely free, no API key needed)."""

    def __init__(self, base_url: str = "http://localhost:11434", model: str = "llama3"):
        super().__init__(None, base_url)
        self.model = model

    async def generate(
        self, prompt: str, system_prompt: str = "You are a helpful assistant."
    ) -> str:
        payload = {"model": self.model, "prompt": f"{system_prompt}\n\n{prompt}", "stream": False}

        async with aiohttp.ClientSession() as session:
            async with session.post(f"{self.base_url}/api/generate", json=payload) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return data.get("response", "")
                else:
                    error_text = await resp.text()
                    raise Exception(f"Ollama error: {resp.status} - {error_text}")


class AIEngine:
    """
    Unified AI engine that supports multiple providers.
    Works with or without AI enabled.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.enabled = self.config.get("enabled", False)
        self.provider_name = self.config.get("provider", "ollama")
        self.api_key = self.config.get("api_key")
        self.model = self.config.get("model")
        self.provider = self._initialize_provider()

    def _initialize_provider(self) -> Optional[AIProvider]:
        """Initialize the selected AI provider."""
        if not self.enabled:
            return None

        if self.provider_name == "openrouter":
            if not self.api_key:
                raise ValueError("OpenRouter requires an API key")
            return OpenRouterProvider(self.api_key)

        elif self.provider_name == "groq":
            if not self.api_key:
                raise ValueError("Groq requires an API key")
            return GroqProvider(self.api_key)

        elif self.provider_name == "huggingface":
            if not self.api_key:
                raise ValueError("HuggingFace requires an API key")
            return HuggingFaceProvider(
                self.api_key, self.model or "mistralai/Mistral-7B-Instruct-v0.2"
            )

        elif self.provider_name == "ollama":
            return OllamaProvider(
                self.config.get("base_url", "http://localhost:11434"), self.model or "llama3"
            )

        else:
            raise ValueError(f"Unknown provider: {self.provider_name}")

    async def summarize_content(self, html_content: str, url: str) -> str:
        """Generate a summary of webpage content."""
        if not self.enabled or not self.provider:
            return ""

        # Extract visible text (simple approach)
        import re

        text = re.sub(r"<[^>]+>", " ", html_content)
        text = " ".join(text.split())[:3000]  # Limit length

        prompt = f"""Analyze this webpage content from {url} and provide:
1. A concise summary (2-3 sentences)
2. Main topics covered
3. Key information extracted

Content:
{text}"""

        try:
            return await self.provider.generate(
                prompt,
                system_prompt=(
                    "You are a web content analyzer. Provide clear, structured summaries."
                ),
            )
        except Exception as e:
            print(f"AI summarization failed: {e}")
            return ""

    async def extract_structured_data(self, html_content: str, url: str) -> Dict[str, Any]:
        """Extract structured data (products, articles, etc.) from HTML."""
        if not self.enabled or not self.provider:
            return {}

        import re

        text = re.sub(r"<[^>]+>", " ", html_content)
        text = " ".join(text.split())[:2500]

        prompt = f"""Extract structured data from this webpage: {url}

Content:
{text}

Return a JSON object with:
- type: (product, article, service, contact, etc.)
- title: main title
- description: brief description
- items: list of products/services if found
- contact_info: any contact details
- tags: relevant keywords

Respond ONLY with valid JSON."""

        try:
            response = await self.provider.generate(
                prompt, system_prompt="You are a data extraction expert. Return only valid JSON."
            )
            # Try to parse JSON from response
            import json

            # Find JSON in response
            start = response.find("{")
            end = response.rfind("}") + 1
            if start >= 0 and end > start:
                json_str = response[start:end]
                return json.loads(json_str)
            return {}
        except Exception as e:
            print(f"AI data extraction failed: {e}")
            return {}

    async def auto_tag_content(self, html_content: str, url: str) -> List[str]:
        """Automatically generate tags for content."""
        if not self.enabled or not self.provider:
            return []

        import re

        text = re.sub(r"<[^>]+>", " ", html_content)
        text = " ".join(text.split())[:1500]

        prompt = f"""Generate 5-10 relevant tags/keywords for this content from {url}:

{text}

Return only comma-separated tags, no explanations."""

        try:
            response = await self.provider.generate(prompt)
            tags = [t.strip() for t in response.replace(",", "\n").split("\n") if t.strip()]
            return tags[:10]
        except Exception as e:
            print(f"AI tagging failed: {e}")
            return []

    async def filter_irrelevant_content(self, html_content: str) -> str:
        """Remove navigation, ads, and irrelevant content."""
        if not self.enabled or not self.provider:
            # Fallback: simple heuristic removal
            import re

            text = re.sub(r"<nav[^>]*>.*?</nav>", "", html_content, flags=re.DOTALL | re.IGNORECASE)
            text = re.sub(r"<footer[^>]*>.*?</footer>", "", text, flags=re.DOTALL | re.IGNORECASE)
            text = re.sub(r"<script[^>]*>.*?</script>", "", text, flags=re.DOTALL | re.IGNORECASE)
            text = re.sub(r"<style[^>]*>.*?</style>", "", text, flags=re.DOTALL | re.IGNORECASE)
            return text

        prompt = (
            "Clean this HTML by removing navigation menus, advertisements, footers, "
            "and other non-content elements. Keep only the main article/content. "
            "Return clean HTML.\n\n"
            f"HTML:\n{html_content[:3000]}"
        )

        try:
            return await self.provider.generate(
                prompt, system_prompt="You are an HTML cleaner. Return only cleaned HTML."
            )
        except Exception as e:
            print(f"AI filtering failed: {e}")
            return html_content

    async def analyze_and_enhance(
        self, html_content: str, url: str, output_dir: Path
    ) -> Dict[str, Any]:
        """Complete AI analysis pipeline."""
        results = {"summary": "", "structured_data": {}, "tags": [], "cleaned_html": ""}

        if not self.enabled:
            return results

        print(f"🤖 Running AI analysis on {url}...")

        tasks = []
        tasks.append(self.summarize_content(html_content, url))
        tasks.append(self.extract_structured_data(html_content, url))
        tasks.append(self.auto_tag_content(html_content, url))
        tasks.append(self.filter_irrelevant_content(html_content))

        try:
            (
                results["summary"],
                results["structured_data"],
                results["tags"],
                results["cleaned_html"],
            ) = await asyncio.gather(*tasks, return_exceptions=True)

            # Handle exceptions in results
            for key, value in results.items():
                if isinstance(value, Exception):
                    print(f"AI task {key} failed: {value}")
                    results[key] = (
                        "" if key in ["summary", "cleaned_html"] else ([] if key == "tags" else {})
                    )

            # Save AI results
            ai_report = output_dir / "ai_analysis.json"
            ai_report.parent.mkdir(parents=True, exist_ok=True)

            report_data = {
                "url": url,
                "summary": results["summary"],
                "structured_data": results["structured_data"],
                "tags": results["tags"],
                "analysis_timestamp": asyncio.get_event_loop().time(),
            }

            with open(ai_report, "w", encoding="utf-8") as f:
                json.dump(report_data, f, indent=2, ensure_ascii=False)

            # Save summary as markdown
            if results["summary"]:
                summary_md = output_dir / "SUMMARY.md"
                with open(summary_md, "w", encoding="utf-8") as f:
                    f.write(f"# AI Analysis Summary: {url}\n\n")
                    f.write(f"## Summary\n{results['summary']}\n\n")
                    f.write(f"## Tags\n{', '.join(results['tags'])}\n\n")
                    if results["structured_data"]:
                        structured_json = json.dumps(results["structured_data"], indent=2)
                        f.write(f"## Structured Data\n```json\n{structured_json}\n```\n")

            print(f"✅ AI analysis complete! Saved to {output_dir}")

        except Exception as e:
            print(f"❌ AI analysis pipeline failed: {e}")

        return results


def get_available_providers() -> List[str]:
    """List all available AI providers."""
    return ["openrouter", "groq", "huggingface", "ollama"]


def validate_api_key(provider: str, api_key: str) -> bool:
    """Validate API key format (basic check)."""
    if provider == "ollama":
        return True  # No key needed

    if not api_key or len(api_key) < 10:
        return False

    return True
