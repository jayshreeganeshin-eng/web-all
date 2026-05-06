"""
SEO Analysis utilities for web-all.
Analyzes cloned websites for SEO metrics and recommendations.
"""

import re
from pathlib import Path
from typing import Dict, List, Optional
from bs4 import BeautifulSoup
from datetime import datetime


class SEOAnalyzer:
    """Analyze websites for SEO best practices."""
    
    def __init__(self, site_dir: str):
        self.site_dir = Path(site_dir)
        self.results = {
            "analyzed_at": datetime.now().isoformat(),
            "pages": [],
            "summary": {},
            "recommendations": [],
        }
    
    def analyze_page(self, html_path: Path) -> Dict:
        """Analyze a single HTML page for SEO factors."""
        try:
            content = html_path.read_text(encoding='utf-8')
            soup = BeautifulSoup(content, 'lxml')
            
            # Extract SEO elements
            title = soup.find('title')
            title_text = title.get_text(strip=True) if title else ""
            title_length = len(title_text)
            
            meta_desc = soup.find('meta', attrs={'name': 'description'})
            description = meta_desc.get('content', '') if meta_desc else ""
            desc_length = len(description)
            
            meta_keywords = soup.find('meta', attrs={'name': 'keywords'})
            keywords = meta_keywords.get('content', '') if meta_keywords else ""
            
            # Count headings
            h1_tags = soup.find_all('h1')
            h2_tags = soup.find_all('h2')
            h3_tags = soup.find_all('h3')
            
            # Count images and check alt text
            images = soup.find_all('img')
            images_with_alt = sum(1 for img in images if img.get('alt'))
            
            # Count links
            internal_links = 0
            external_links = 0
            for link in soup.find_all('a', href=True):
                href = link['href']
                if href.startswith(('http://', 'https://')):
                    external_links += 1
                else:
                    internal_links += 1
            
            # Word count
            text_content = soup.get_text(separator=' ', strip=True)
            word_count = len(text_content.split())
            
            # Check for canonical URL
            canonical = soup.find('link', rel='canonical')
            canonical_url = canonical.get('href', '') if canonical else ""
            
            # Check for robots meta
            robots = soup.find('meta', attrs={'name': 'robots'})
            robots_content = robots.get('content', '') if robots else ""
            
            # Check for Open Graph tags
            og_tags = {}
            for prop in ['og:title', 'og:description', 'og:image', 'og:url', 'og:type']:
                og_tag = soup.find('meta', property=prop)
                if og_tag:
                    og_tags[prop] = og_tag.get('content', '')
            
            # Check for Twitter Card tags
            twitter_tags = {}
            for name in ['twitter:card', 'twitter:title', 'twitter:description', 'twitter:image']:
                tw_tag = soup.find('meta', attrs={'name': name})
                if tw_tag:
                    twitter_tags[name] = tw_tag.get('content', '')
            
            # Generate issues
            issues = []
            if not title_text:
                issues.append("Missing <title> tag")
            elif title_length < 30 or title_length > 60:
                issues.append(f"Title length ({title_length}) should be between 30-60 characters")
            
            if not description:
                issues.append("Missing meta description")
            elif desc_length < 50 or desc_length > 160:
                issues.append(f"Description length ({desc_length}) should be between 50-160 characters")
            
            if len(h1_tags) == 0:
                issues.append("Missing H1 heading")
            elif len(h1_tags) > 1:
                issues.append(f"Multiple H1 tags found ({len(h1_tags)})")
            
            if images and images_with_alt < len(images):
                issues.append(f"{len(images) - images_with_alt} images missing alt text")
            
            if word_count < 300:
                issues.append(f"Low word count ({word_count}) - consider adding more content")
            
            return {
                "path": str(html_path.relative_to(self.site_dir)),
                "title": title_text,
                "title_length": title_length,
                "description": description,
                "description_length": desc_length,
                "h1_count": len(h1_tags),
                "h2_count": len(h2_tags),
                "h3_count": len(h3_tags),
                "images_total": len(images),
                "images_with_alt": images_with_alt,
                "internal_links": internal_links,
                "external_links": external_links,
                "word_count": word_count,
                "has_canonical": bool(canonical_url),
                "robots": robots_content,
                "open_graph": og_tags,
                "twitter_card": twitter_tags,
                "issues": issues,
                "score": self._calculate_score(title_length, desc_length, h1_tags, images, images_with_alt, word_count, issues),
            }
        except Exception as e:
            return {
                "path": str(html_path.relative_to(self.site_dir)),
                "error": str(e),
                "score": 0,
            }
    
    def _calculate_score(self, title_len, desc_len, h1_tags, images, images_with_alt, word_count, issues) -> int:
        """Calculate SEO score (0-100)."""
        score = 100
        
        # Title scoring
        if title_len == 0:
            score -= 20
        elif not (30 <= title_len <= 60):
            score -= 10
        
        # Description scoring
        if desc_len == 0:
            score -= 20
        elif not (50 <= desc_len <= 160):
            score -= 10
        
        # H1 scoring
        if len(h1_tags) == 0:
            score -= 15
        elif len(h1_tags) > 1:
            score -= 10
        
        # Image alt scoring
        if images and images_with_alt < len(images):
            score -= min(15, (len(images) - images_with_alt) * 3)
        
        # Word count scoring
        if word_count < 300:
            score -= 10
        elif word_count < 500:
            score -= 5
        
        # Issue penalties
        score -= len(issues) * 2
        
        return max(0, min(100, score))
    
    def analyze_site(self) -> Dict:
        """Analyze all HTML pages in the site."""
        html_files = list(self.site_dir.rglob('*.html')) + list(self.site_dir.rglob('*.htm'))
        
        for html_file in html_files:
            page_result = self.analyze_page(html_file)
            self.results["pages"].append(page_result)
        
        # Calculate summary
        if self.results["pages"]:
            scores = [p.get('score', 0) for p in self.results["pages"] if 'error' not in p]
            self.results["summary"] = {
                "total_pages": len(self.results["pages"]),
                "average_score": round(sum(scores) / len(scores), 1) if scores else 0,
                "pages_with_issues": sum(1 for p in self.results["pages"] if p.get('issues')),
                "total_issues": sum(len(p.get('issues', [])) for p in self.results["pages"]),
            }
        
        # Generate recommendations
        self._generate_recommendations()
        
        return self.results
    
    def _generate_recommendations(self):
        """Generate SEO recommendations based on analysis."""
        recommendations = []
        
        pages_missing_title = sum(1 for p in self.results["pages"] if not p.get('title'))
        if pages_missing_title > 0:
            recommendations.append(f"Add <title> tags to {pages_missing_title} page(s)")
        
        pages_missing_desc = sum(1 for p in self.results["pages"] if not p.get('description'))
        if pages_missing_desc > 0:
            recommendations.append(f"Add meta descriptions to {pages_missing_desc} page(s)")
        
        pages_multiple_h1 = sum(1 for p in self.results["pages"] if p.get('h1_count', 0) > 1)
        if pages_multiple_h1 > 0:
            recommendations.append(f"Fix multiple H1 tags on {pages_multiple_h1} page(s)")
        
        total_images_no_alt = sum(
            p.get('images_total', 0) - p.get('images_with_alt', 0) 
            for p in self.results["pages"]
        )
        if total_images_no_alt > 0:
            recommendations.append(f"Add alt text to {total_images_no_alt} image(s)")
        
        low_word_count_pages = sum(1 for p in self.results["pages"] if p.get('word_count', 0) < 300)
        if low_word_count_pages > 0:
            recommendations.append(f"Expand content on {low_word_count_pages} page(s) with less than 300 words")
        
        pages_no_canonical = sum(1 for p in self.results["pages"] if not p.get('has_canonical'))
        if pages_no_canonical > 0:
            recommendations.append(f"Add canonical URLs to {pages_no_canonical} page(s)")
        
        pages_no_og = sum(1 for p in self.results["pages"] if not p.get('open_graph'))
        if pages_no_og > 0:
            recommendations.append(f"Add Open Graph tags to {pages_no_og} page(s) for better social sharing")
        
        self.results["recommendations"] = recommendations
    
    def generate_report(self, output_path: Optional[str] = None) -> str:
        """Generate an HTML SEO report."""
        if not self.results.get("summary"):
            self.analyze_site()
        
        if output_path is None:
            output_path = str(self.site_dir / "seo_report.html")
        
        # Sort pages by score
        sorted_pages = sorted(self.results["pages"], key=lambda x: x.get('score', 0))
        
        pages_html = ""
        for page in sorted_pages[:50]:  # Show first 50 pages
            score = page.get('score', 0)
            score_color = "#10b981" if score >= 80 else "#f59e0b" if score >= 60 else "#ef4444"
            
            issues_html = ""
            for issue in page.get('issues', []):
                issues_html += f"<li style='color: #ef4444;'>{issue}</li>"
            
            pages_html += f"""
            <tr>
                <td>{page.get('path', 'N/A')}</td>
                <td style="text-align: center; color: {score_color}; font-weight: bold;">{score}/100</td>
                <td>{page.get('title', 'N/A')[:50]}</td>
                <td>{page.get('word_count', 0)}</td>
                <td>{page.get('h1_count', 0)}</td>
                <td>{len(page.get('issues', []))}</td>
            </tr>
            """
            if issues_html:
                pages_html += f'<tr><td colspan="6"><ul style="margin: 0.5rem 0;">{issues_html}</ul></td></tr>'
        
        recommendations_html = ""
        for rec in self.results.get("recommendations", []):
            recommendations_html += f"<li>{rec}</li>"
        
        avg_score = self.results.get("summary", {}).get("average_score", 0)
        score_color = "#10b981" if avg_score >= 80 else "#f59e0b" if avg_score >= 60 else "#ef4444"
        
        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SEO Analysis Report - web-all</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            max-width: 1400px;
            margin: 0 auto;
            padding: 2rem;
            background: #f5f5f5;
        }}
        .container {{
            background: white;
            padding: 2rem;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        h1 {{ color: #667eea; }}
        .score-display {{
            font-size: 4rem;
            font-weight: bold;
            color: {score_color};
            text-align: center;
            margin: 2rem 0;
        }}
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1rem;
            margin: 2rem 0;
        }}
        .stat-card {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 1.5rem;
            border-radius: 8px;
            text-align: center;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 2rem;
        }}
        th, td {{
            padding: 0.75rem;
            text-align: left;
            border-bottom: 1px solid #e0e0e0;
        }}
        th {{
            background: #f5f5f5;
            font-weight: 600;
        }}
        .recommendations {{
            background: #fef3c7;
            padding: 1.5rem;
            border-radius: 8px;
            margin: 2rem 0;
        }}
        .recommendations h2 {{
            color: #92400e;
            margin-top: 0;
        }}
        .recommendations li {{
            color: #78350f;
            margin: 0.5rem 0;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🔍 SEO Analysis Report</h1>
        <p>Generated: {self.results["analyzed_at"]}</p>
        <p>Site: {self.site_dir}</p>
        
        <div class="score-display">{avg_score}/100</div>
        <p style="text-align: center; font-size: 1.25rem;">Average SEO Score</p>
        
        <div class="stats-grid">
            <div class="stat-card">
                <div style="font-size: 2rem; font-weight: bold;">{self.results.get('summary', {}).get('total_pages', 0)}</div>
                <div>Total Pages</div>
            </div>
            <div class="stat-card">
                <div style="font-size: 2rem; font-weight: bold;">{self.results.get('summary', {}).get('pages_with_issues', 0)}</div>
                <div>Pages with Issues</div>
            </div>
            <div class="stat-card">
                <div style="font-size: 2rem; font-weight: bold;">{self.results.get('summary', {}).get('total_issues', 0)}</div>
                <div>Total Issues</div>
            </div>
        </div>
        
        <div class="recommendations">
            <h2>📋 Recommendations</h2>
            <ul>
                {recommendations_html or '<li>No critical issues found!</li>'}
            </ul>
        </div>
        
        <h2>Page Analysis</h2>
        <table>
            <thead>
                <tr>
                    <th>Page</th>
                    <th>Score</th>
                    <th>Title</th>
                    <th>Words</th>
                    <th>H1s</th>
                    <th>Issues</th>
                </tr>
            </thead>
            <tbody>
                {pages_html}
            </tbody>
        </table>
    </div>
</body>
</html>
"""
        
        Path(output_path).write_text(html_content, encoding='utf-8')
        return output_path


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        analyzer = SEOAnalyzer(sys.argv[1])
        results = analyzer.analyze_site()
        report_path = analyzer.generate_report()
        print(f"SEO Analysis Complete!")
        print(f"Average Score: {results.get('summary', {}).get('average_score', 0)}/100")
        print(f"Report saved to: {report_path}")
    else:
        print("Usage: python seo_analyzer.py <site_directory>")
