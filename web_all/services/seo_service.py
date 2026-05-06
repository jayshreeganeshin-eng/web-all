"""
SEO Service with AI-powered analysis and recommendations.
"""
import asyncio
from typing import Dict, List, Optional, Any
from bs4 import BeautifulSoup
import httpx
from web_all.utils.ai_engine import AIEngine


class SEOService:
    """Service for performing SEO analysis with AI enhancements."""

    def __init__(self, ai_provider: str = "ollama", ai_model: Optional[str] = None):
        """Initialize SEO Service with AI engine."""
        # Create config dict for AIEngine
        config = {
            "enabled": True,
            "provider": ai_provider,
            "model": ai_model,
            "api_key": None,  # User should set via env or config
            "base_url": "http://localhost:11434" if ai_provider == "ollama" else ""
        }
        self.ai_engine = AIEngine(config)
        self.timeout = httpx.Timeout(30.0)

    async def analyze_url(self, url: str) -> Dict[str, Any]:
        """
        Perform comprehensive SEO analysis on a URL.
        
        Returns:
            Dictionary containing SEO metrics and AI recommendations.
        """
        result = {
            "url": url,
            "status": "pending",
            "metrics": {},
            "ai_analysis": {}
        }

        try:
            # Fetch the page
            async with httpx.AsyncClient(timeout=self.timeout, follow_redirects=True) as client:
                response = await client.get(url, headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                })
                response.raise_for_status()
                
                html = response.text
                soup = BeautifulSoup(html, 'html.parser')
                
                # Basic SEO metrics
                result["metrics"] = self._extract_basic_metrics(soup, html)
                
                # AI-powered analysis
                result["ai_analysis"] = await self._perform_ai_analysis(soup, url)
                
                result["status"] = "completed"
                
        except Exception as e:
            result["status"] = "failed"
            result["error"] = str(e)
            
        return result

    def _extract_basic_metrics(self, soup: BeautifulSoup, html: str) -> Dict[str, Any]:
        """Extract basic SEO metrics from parsed HTML."""
        metrics = {}
        
        # Title tag
        title = soup.find('title')
        metrics['title_tag'] = title.string.strip() if title and title.string else ""
        metrics['title_length'] = len(metrics['title_tag']) if metrics['title_tag'] else 0
        
        # Meta description
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        metrics['meta_description'] = meta_desc.get('content', '') if meta_desc else ""
        metrics['meta_description_length'] = len(metrics['meta_description'])
        
        # Headings
        metrics['h1_count'] = len(soup.find_all('h1'))
        metrics['h2_count'] = len(soup.find_all('h2'))
        metrics['h3_count'] = len(soup.find_all('h3'))
        
        # Images
        images = soup.find_all('img')
        metrics['image_count'] = len(images)
        metrics['images_without_alt'] = sum(1 for img in images if not img.get('alt'))
        
        # Links
        links = soup.find_all('a', href=True)
        metrics['internal_links'] = 0
        metrics['external_links'] = 0
        # Count would need base URL to determine internal vs external
        
        # Word count
        text = soup.get_text(separator=' ', strip=True)
        metrics['word_count'] = len(text.split())
        
        # Check for common SEO issues
        issues = []
        if metrics['title_length'] == 0:
            issues.append("Missing title tag")
        elif metrics['title_length'] < 30 or metrics['title_length'] > 60:
            issues.append(f"Title length ({metrics['title_length']}) should be between 30-60 characters")
            
        if metrics['meta_description_length'] == 0:
            issues.append("Missing meta description")
        elif metrics['meta_description_length'] < 120 or metrics['meta_description_length'] > 160:
            issues.append(f"Meta description length ({metrics['meta_description_length']}) should be between 120-160 characters")
            
        if metrics['h1_count'] == 0:
            issues.append("Missing H1 heading")
        elif metrics['h1_count'] > 1:
            issues.append(f"Multiple H1 headings found ({metrics['h1_count']})")
            
        if metrics['images_without_alt'] > 0:
            issues.append(f"{metrics['images_without_alt']} images missing alt text")
            
        metrics['issues'] = issues
        metrics['issue_count'] = len(issues)
        
        return metrics

    async def _perform_ai_analysis(self, soup: BeautifulSoup, url: str) -> Dict[str, Any]:
        """Use AI to analyze content and provide recommendations."""
        ai_result = {
            "score": 0,
            "recommendations": [],
            "suggested_title": "",
            "suggested_description": "",
            "keywords": []
        }
        
        try:
            # Extract main content
            text_content = soup.get_text(separator=' ', strip=True)[:3000]  # Limit for API
            title = soup.find('title')
            current_title = title.string.strip() if title and title.string else ""
            meta_desc = soup.find('meta', attrs={'name': 'description'})
            current_desc = meta_desc.get('content', '') if meta_desc else ""
            
            # Prompt for AI analysis
            prompt = f"""Analyze this webpage content for SEO optimization:

URL: {url}
Current Title: {current_title}
Current Description: {current_desc}

Content Sample:
{text_content}

Provide a JSON response with:
1. seo_score (0-100): Overall SEO score
2. recommendations (list): Top 5 actionable SEO recommendations
3. suggested_title: Optimized title tag (50-60 characters)
4. suggested_description: Optimized meta description (150-160 characters)
5. keywords (list): Top 10 relevant keywords for this content

Respond ONLY with valid JSON."""

            response = await self.ai_engine.generate_async(prompt)
            
            # Parse AI response (assuming it returns JSON)
            import json
            try:
                # Try to extract JSON from response
                import re
                json_match = re.search(r'\{.*\}', response, re.DOTALL)
                if json_match:
                    ai_data = json.loads(json_match.group())
                    ai_result["score"] = ai_data.get("seo_score", 0)
                    ai_result["recommendations"] = ai_data.get("recommendations", [])
                    ai_result["suggested_title"] = ai_data.get("suggested_title", "")
                    ai_result["suggested_description"] = ai_data.get("suggested_description", "")
                    ai_result["keywords"] = ai_data.get("keywords", [])
            except:
                # If parsing fails, provide basic analysis
                ai_result["recommendations"] = ["Consider improving content quality", "Add more relevant keywords"]
                
        except Exception as e:
            ai_result["error"] = str(e)
            
        return ai_result

    async def generate_seo_content(self, topic: str, keywords: List[str], 
                                   content_type: str = "blog_post",
                                   tone: str = "professional") -> str:
        """Generate SEO-optimized content using AI."""
        
        prompt = f"""Write a {content_type} about: {topic}

Target Keywords: {', '.join(keywords)}
Tone: {tone}

Requirements:
- Include primary keywords naturally in the first paragraph
- Use H2 and H3 subheadings with secondary keywords
- Write engaging, informative content (800-1000 words)
- Include a call-to-action at the end
- Optimize for search engines while maintaining readability

Generate the content now."""

        content = await self.ai_engine.generate_async(prompt)
        return content

    async def optimize_existing_content(self, content: str, keywords: List[str]) -> str:
        """Use AI to optimize existing content for better SEO."""
        
        prompt = f"""Optimize the following content for SEO with these keywords: {', '.join(keywords)}

Original Content:
{content[:2000]}  # Limit for API

Please:
1. Improve keyword placement naturally
2. Suggest better headings (H1, H2, H3)
3. Enhance readability
4. Add meta title and description suggestions
5. Maintain the original meaning

Return the optimized content."""

        optimized = await self.ai_engine.generate_async(prompt)
        return optimized
