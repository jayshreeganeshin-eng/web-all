"""
Design token extractor for Figma-compatible design systems.
Extracts colors, typography, spacing, and other design tokens.
"""

import re
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
from bs4 import BeautifulSoup
from dataclasses import dataclass, field, asdict
import logging
import json

logger = logging.getLogger(__name__)


@dataclass
class ColorToken:
    """Represents a color design token."""
    name: str
    value: str
    type: str  # hex, rgb, rgba, hsl
    usage_count: int = 0
    category: Optional[str] = None  # primary, secondary, accent, neutral


@dataclass
class TypographyToken:
    """Represents a typography design token."""
    name: str
    font_family: str
    font_size: str
    font_weight: str
    line_height: str
    letter_spacing: str = ""


@dataclass
class SpacingToken:
    """Represents a spacing design token."""
    name: str
    value: str
    scale: str  # px, rem, em


@dataclass
class DesignTokens:
    """Container for all design tokens."""
    colors: Dict[str, ColorToken] = field(default_factory=dict)
    typography: Dict[str, TypographyToken] = field(default_factory=dict)
    spacing: Dict[str, SpacingToken] = field(default_factory=dict)
    shadows: Dict[str, Any] = field(default_factory=dict)
    border_radius: Dict[str, Any] = field(default_factory=dict)
    breakpoints: Dict[str, str] = field(default_factory=dict)


class DesignTokenExtractor:
    """
    Extracts design tokens from HTML/CSS.
    
    Outputs Figma-compatible JSON format.
    """
    
    def __init__(self):
        self.tokens = DesignTokens()
        self.raw_colors: Dict[str, int] = {}
        self.raw_spacing: Dict[str, int] = {}
    
    def extract_from_html(self, html: str) -> DesignTokens:
        """Extract design tokens from HTML content."""
        soup = BeautifulSoup(html, 'lxml')
        
        # Extract inline styles
        self._extract_inline_styles(soup)
        
        # Extract from <style> tags
        style_tags = soup.find_all('style')
        for style in style_tags:
            if style.string:
                self._extract_from_css(style.string)
        
        # Extract from linked stylesheets (would need to fetch them)
        link_tags = soup.find_all('link', rel='stylesheet')
        for link in link_tags:
            href = link.get('href')
            if href:
                logger.info(f"Would extract from stylesheet: {href}")
        
        # Organize tokens
        self._organize_color_tokens()
        self._organize_spacing_tokens()
        
        return self.tokens
    
    def _extract_inline_styles(self, soup: BeautifulSoup):
        """Extract styles from inline style attributes."""
        for element in soup.find_all(True, style=True):
            style = element.get('style', '')
            self._parse_style_attribute(style)
    
    def _parse_style_attribute(self, style: str):
        """Parse a style attribute string."""
        for prop in style.split(';'):
            if ':' not in prop:
                continue
            
            key, value = prop.split(':', 1)
            key = key.strip().lower()
            value = value.strip()
            
            if key == 'color':
                self._record_color(value)
            elif key == 'background-color':
                self._record_color(value)
            elif key == 'background':
                # Handle background shorthand
                self._extract_color_from_background(value)
            elif key in ['font-size', 'margin', 'padding', 'gap']:
                self._record_spacing(value)
            elif key == 'font-family':
                self._record_typography(key, value)
            elif key == 'box-shadow':
                self._record_shadow(value)
            elif key == 'border-radius':
                self._record_border_radius(value)
    
    def _extract_from_css(self, css_content: str):
        """Extract tokens from CSS content."""
        # Extract color variables
        color_patterns = [
            r'--([a-zA-Z0-9_-]+):\s*(#[0-9a-fA-F]{3,8})',
            r'--([a-zA-Z0-9_-]+):\s*(rgb\([^)]+\))',
            r'--([a-zA-Z0-9_-]+):\s*(rgba\([^)]+\))',
            r'--([a-zA-Z0-9_-]+):\s*(hsl\([^)]+\))',
        ]
        
        for pattern in color_patterns:
            matches = re.findall(pattern, css_content)
            for name, value in matches:
                self._record_color(value, name)
        
        # Extract spacing variables
        spacing_pattern = r'--([a-zA-Z0-9_-]+):\s*(\d+(?:\.\d+)?(?:px|rem|em|%))'
        matches = re.findall(spacing_pattern, css_content)
        for name, value in matches:
            if any(kw in name.lower() for kw in ['spacing', 'space', 'gap', 'margin', 'padding']):
                self._record_spacing(value, name)
        
        # Extract Tailwind classes
        self._extract_tailwind_classes(css_content)
    
    def _extract_tailwind_classes(self, css_content: str):
        """Extract design tokens from Tailwind CSS."""
        # Color utilities
        bg_colors = re.findall(r'\.bg-([a-zA-Z0-9-]+)\s*\{[^}]*background-color:\s*([^;]+)', css_content)
        for name, value in bg_colors:
            self._record_color(value, f"tailwind-{name}")
        
        # Text colors
        text_colors = re.findall(r'\.text-([a-zA-Z0-9-]+)\s*\{[^}]*color:\s*([^;]+)', css_content)
        for name, value in text_colors:
            self._record_color(value, f"tailwind-text-{name}")
        
        # Spacing
        spacing_patterns = [
            (r'\.m-(\d+)\s*\{[^}]*margin:\s*([^;]+)', 'margin'),
            (r'\.p-(\d+)\s*\{[^}]*padding:\s*([^;]+)', 'padding'),
            (r'\.gap-(\d+)\s*\{[^}]*gap:\s*([^;]+)', 'gap'),
        ]
        
        for pattern, prop_type in spacing_patterns:
            matches = re.findall(pattern, css_content)
            for _, value in matches:
                self._record_spacing(value)
    
    def _record_color(self, value: str, name: Optional[str] = None):
        """Record a color value."""
        if not value or value in ['transparent', 'inherit', 'initial', 'unset']:
            return
        
        # Normalize color value
        value = value.strip().lower()
        
        if value not in self.raw_colors:
            self.raw_colors[value] = 0
        self.raw_colors[value] += 1
        
        if name and name not in self.tokens.colors:
            color_type = self._detect_color_type(value)
            self.tokens.colors[name] = ColorToken(
                name=name,
                value=value,
                type=color_type,
            )
    
    def _extract_color_from_background(self, value: str):
        """Extract color from background shorthand property."""
        # Simple extraction - would need more sophisticated parsing for production
        color_match = re.search(r'(#[0-9a-fA-F]{3,8}|rgb\([^)]+\)|rgba\([^)]+\)|hsl\([^)]+\))', value)
        if color_match:
            self._record_color(color_match.group(1))
    
    def _record_spacing(self, value: str, name: Optional[str] = None):
        """Record a spacing value."""
        if not value or value in ['auto', 'inherit', 'initial', 'unset']:
            return
        
        value = value.strip()
        
        if value not in self.raw_spacing:
            self.raw_spacing[value] = 0
        self.raw_spacing[value] += 1
        
        if name and name not in self.tokens.spacing:
            scale = self._detect_scale(value)
            self.tokens.spacing[name] = SpacingToken(
                name=name,
                value=value,
                scale=scale,
            )
    
    def _record_typography(self, prop: str, value: str):
        """Record typography values."""
        if prop == 'font-family':
            # Create a default typography token
            if 'base' not in self.tokens.typography:
                self.tokens.typography['base'] = TypographyToken(
                    name='base',
                    font_family=value,
                    font_size='16px',
                    font_weight='400',
                    line_height='1.5',
                )
    
    def _record_shadow(self, value: str):
        """Record shadow values."""
        if not value or value in ['none', 'inherit', 'initial']:
            return
        
        shadow_name = f"shadow_{len(self.tokens.shadows) + 1}"
        self.tokens.shadows[shadow_name] = {
            "name": shadow_name,
            "value": value,
            "type": "boxShadow",
        }
    
    def _record_border_radius(self, value: str):
        """Record border radius values."""
        if not value or value in ['0', 'inherit', 'initial']:
            return
        
        radius_name = f"radius_{len(self.tokens.border_radius) + 1}"
        self.tokens.border_radius[radius_name] = {
            "name": radius_name,
            "value": value,
            "type": "borderRadius",
        }
    
    def _detect_color_type(self, value: str) -> str:
        """Detect the type of color value."""
        if value.startswith('#'):
            return 'hex'
        elif value.startswith('rgb('):
            return 'rgb'
        elif value.startswith('rgba('):
            return 'rgba'
        elif value.startswith('hsl('):
            return 'hsl'
        elif value.startswith('hsla('):
            return 'hsla'
        return 'unknown'
    
    def _detect_scale(self, value: str) -> str:
        """Detect the scale unit of a spacing value."""
        if 'rem' in value:
            return 'rem'
        elif 'em' in value:
            return 'em'
        elif '%' in value:
            return 'percent'
        return 'px'
    
    def _organize_color_tokens(self):
        """Organize colors by frequency and category."""
        # Sort colors by usage count
        sorted_colors = sorted(
            self.raw_colors.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        # Assign categories based on usage
        for i, (color, count) in enumerate(sorted_colors[:20]):  # Top 20 colors
            if i == 0:
                category = 'primary'
            elif i < 5:
                category = 'secondary'
            elif i < 10:
                category = 'accent'
            else:
                category = 'neutral'
            
            token_name = f"color-{category}-{i + 1}"
            
            if token_name not in self.tokens.colors:
                self.tokens.colors[token_name] = ColorToken(
                    name=token_name,
                    value=color,
                    type=self._detect_color_type(color),
                    usage_count=count,
                    category=category,
                )
    
    def _organize_spacing_tokens(self):
        """Organize spacing into a scale."""
        # Sort spacing values
        sorted_spacing = sorted(
            self.raw_spacing.items(),
            key=lambda x: self._parse_spacing_value(x[0])
        )
        
        # Create spacing scale
        for i, (value, count) in enumerate(sorted_spacing[:15]):  # Top 15 spacing values
            token_name = f"spacing-{i}"
            
            if token_name not in self.tokens.spacing:
                self.tokens.spacing[token_name] = SpacingToken(
                    name=token_name,
                    value=value,
                    scale=self._detect_scale(value),
                )
    
    def _parse_spacing_value(self, value: str) -> float:
        """Parse spacing value to float for sorting."""
        match = re.match(r'(\d+(?:\.\d+)?)', value)
        if match:
            return float(match.group(1))
        return 0.0
    
    def to_figma_json(self) -> Dict[str, Any]:
        """Export tokens in Figma-compatible JSON format."""
        figma_tokens = {
            "colors": {},
            "typography": {},
            "spacing": {},
            "shadows": {},
            "borderRadius": {},
        }
        
        # Colors
        for name, token in self.tokens.colors.items():
            figma_tokens["colors"][name] = {
                "value": token.value,
                "type": "color",
                "description": f"{token.category or 'custom'} color",
            }
        
        # Typography
        for name, token in self.tokens.typography.items():
            figma_tokens["typography"][name] = {
                "fontFamily": token.font_family,
                "fontWeight": token.font_weight,
                "fontSize": token.font_size,
                "lineHeight": token.line_height,
                "letterSpacing": token.letter_spacing,
                "type": "typography",
            }
        
        # Spacing
        for name, token in self.tokens.spacing.items():
            figma_tokens["spacing"][name] = {
                "value": token.value,
                "type": "dimension",
            }
        
        # Shadows
        for name, token in self.tokens.shadows.items():
            figma_tokens["shadows"][name] = token
        
        # Border Radius
        for name, token in self.tokens.border_radius.items():
            figma_tokens["borderRadius"][name] = token
        
        return figma_tokens
    
    def export_to_file(self, output_path: str) -> str:
        """Export design tokens to JSON file."""
        figma_json = self.to_figma_json()
        
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w') as f:
            json.dump(figma_json, f, indent=2)
        
        logger.info(f"Design tokens exported to {output_file}")
        return str(output_file)
    
    def get_summary(self) -> Dict[str, int]:
        """Get summary of extracted tokens."""
        return {
            "colors": len(self.tokens.colors),
            "typography": len(self.tokens.typography),
            "spacing": len(self.tokens.spacing),
            "shadows": len(self.tokens.shadows),
            "border_radius": len(self.tokens.border_radius),
        }
