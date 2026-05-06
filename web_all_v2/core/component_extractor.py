"""
Component extractor for identifying reusable UI components.
Analyzes HTML/CSS to extract buttons, cards, modals, etc.
"""

import re
from typing import Dict, List, Any, Optional
from pathlib import Path
from bs4 import BeautifulSoup
from dataclasses import dataclass, field, asdict
import logging

logger = logging.getLogger(__name__)


@dataclass
class Component:
    """Represents a UI component."""
    type: str
    name: str
    html: str
    css_properties: Dict[str, str] = field(default_factory=dict)
    variants: List[str] = field(default_factory=list)
    accessibility: Dict[str, Any] = field(default_factory=dict)
    framework_hints: List[str] = field(default_factory=list)
    file_path: Optional[str] = None


class ComponentExtractor:
    """
    Extracts reusable UI components from HTML.
    
    Identifies:
    - Buttons
    - Cards
    - Modals/Dialogs
    - Navigation menus
    - Forms
    - Input fields
    - Tables
    - Lists
    - Typography elements
    """
    
    # Component detection patterns
    COMPONENT_PATTERNS = {
        'button': [
            r'<button[^>]*>.*?</button>',
            r'<input[^>]*type=["\']submit["\'][^>]*>',
            r'<a[^>]*class=["\'][^"\']*btn[^"\']*["\'][^>]*>.*?</a>',
        ],
        'card': [
            r'<div[^>]*class=["\'][^"\']*(?:card|tile|panel)[^"\']*["\'][^>]*>.*?</div>',
        ],
        'modal': [
            r'<div[^>]*class=["\'][^"\']*(?:modal|dialog|popup)[^"\']*["\'][^>]*>.*?</div>',
        ],
        'navigation': [
            r'<nav[^>]*>.*?</nav>',
            r'<ul[^>]*class=["\'][^"\']*nav[^"\']*["\'][^>]*>.*?</ul>',
        ],
        'form': [
            r'<form[^>]*>.*?</form>',
        ],
        'input': [
            r'<input[^>]*/?>',
            r'<textarea[^>]*>.*?</textarea>',
            r'<select[^>]*>.*?</select>',
        ],
        'table': [
            r'<table[^>]*>.*?</table>',
        ],
        'list': [
            r'<ul[^>]*>.*?</ul>',
            r'<ol[^>]*>.*?</ol>',
        ],
    }
    
    def __init__(self):
        self.components: Dict[str, List[Component]] = {}
        self.component_counter: Dict[str, int] = {}
    
    def extract_from_html(self, html: str, source_url: str = "") -> Dict[str, List[Component]]:
        """Extract all components from HTML content."""
        soup = BeautifulSoup(html, 'lxml')
        
        # Extract by type
        for component_type in self.COMPONENT_PATTERNS.keys():
            self.components[component_type] = []
            self._extract_component_type(soup, component_type, source_url)
        
        # Analyze CSS for each component
        self._analyze_component_styles(soup)
        
        # Check accessibility
        self._check_accessibility()
        
        # Detect framework hints
        self._detect_frameworks(soup)
        
        logger.info(f"Extracted {sum(len(v) for v in self.components.values())} components")
        
        return self.components
    
    def _extract_component_type(self, soup: BeautifulSoup, component_type: str, source_url: str):
        """Extract components of a specific type."""
        extractors = {
            'button': self._extract_buttons,
            'card': self._extract_cards,
            'modal': self._extract_modals,
            'navigation': self._extract_navigation,
            'form': self._extract_forms,
            'input': self._extract_inputs,
            'table': self._extract_tables,
            'list': self._extract_lists,
        }
        
        if component_type in extractors:
            extractors[component_type](soup, source_url)
    
    def _extract_buttons(self, soup: BeautifulSoup, source_url: str):
        """Extract button components."""
        for btn in soup.find_all(['button', 'input']):
            if btn.name == 'input' and btn.get('type') not in ['submit', 'button', 'reset']:
                continue
            
            btn_html = str(btn)
            name = self._generate_component_name('button')
            
            component = Component(
                type='button',
                name=name,
                html=btn_html,
                css_properties=self._get_inline_styles(btn),
                accessibility={
                    'has_aria': bool(btn.get('aria-label') or btn.get('aria-labelledby')),
                    'has_text': bool(btn.get_text(strip=True)),
                },
                framework_hints=self._get_class_hints(btn),
            )
            
            self.components['button'].append(component)
    
    def _extract_cards(self, soup: BeautifulSoup, source_url: str):
        """Extract card components."""
        for card in soup.find_all(['div', 'article', 'section']):
            classes = card.get('class', [])
            if any('card' in c.lower() or 'tile' in c.lower() for c in classes):
                card_html = str(card)
                name = self._generate_component_name('card')
                
                component = Component(
                    type='card',
                    name=name,
                    html=card_html,
                    css_properties=self._get_inline_styles(card),
                    framework_hints=self._get_class_hints(card),
                )
                
                self.components['card'].append(component)
    
    def _extract_modals(self, soup: BeautifulSoup, source_url: str):
        """Extract modal/dialog components."""
        for modal in soup.find_all(['div', 'dialog']):
            classes = modal.get('class', [])
            if any('modal' in c.lower() or 'dialog' in c.lower() or 'popup' in c.lower() for c in classes):
                modal_html = str(modal)
                name = self._generate_component_name('modal')
                
                component = Component(
                    type='modal',
                    name=name,
                    html=modal_html,
                    css_properties=self._get_inline_styles(modal),
                    framework_hints=self._get_class_hints(modal),
                )
                
                self.components['modal'].append(component)
    
    def _extract_navigation(self, soup: BeautifulSoup, source_url: str):
        """Extract navigation components."""
        for nav in soup.find_all(['nav', 'ul']):
            if nav.name == 'ul' and not any('nav' in c.lower() for c in nav.get('class', [])):
                continue
            
            nav_html = str(nav)
            name = self._generate_component_name('navigation')
            
            component = Component(
                type='navigation',
                name=name,
                html=nav_html,
                css_properties=self._get_inline_styles(nav),
                framework_hints=self._get_class_hints(nav),
            )
            
            self.components['navigation'].append(component)
    
    def _extract_forms(self, soup: BeautifulSoup, source_url: str):
        """Extract form components."""
        for form in soup.find_all('form'):
            form_html = str(form)
            name = self._generate_component_name('form')
            
            component = Component(
                type='form',
                name=name,
                html=form_html,
                css_properties=self._get_inline_styles(form),
                accessibility={
                    'has_action': bool(form.get('action')),
                    'has_method': bool(form.get('method')),
                },
                framework_hints=self._get_class_hints(form),
            )
            
            self.components['form'].append(component)
    
    def _extract_inputs(self, soup: BeautifulSoup, source_url: str):
        """Extract input components."""
        for inp in soup.find_all(['input', 'textarea', 'select']):
            inp_html = str(inp)
            input_type = inp.get('type', 'text') if inp.name == 'input' else inp.name
            name = self._generate_component_name(f'input_{input_type}')
            
            component = Component(
                type='input',
                name=name,
                html=inp_html,
                css_properties=self._get_inline_styles(inp),
                accessibility={
                    'has_label': False,  # Would need to check for associated label
                    'has_placeholder': bool(inp.get('placeholder')),
                    'has_aria': bool(inp.get('aria-label')),
                },
                framework_hints=self._get_class_hints(inp),
            )
            
            self.components['input'].append(component)
    
    def _extract_tables(self, soup: BeautifulSoup, source_url: str):
        """Extract table components."""
        for table in soup.find_all('table'):
            table_html = str(table)
            name = self._generate_component_name('table')
            
            component = Component(
                type='table',
                name=name,
                html=table_html,
                css_properties=self._get_inline_styles(table),
                framework_hints=self._get_class_hints(table),
            )
            
            self.components['table'].append(component)
    
    def _extract_lists(self, soup: BeautifulSoup, source_url: str):
        """Extract list components."""
        for lst in soup.find_all(['ul', 'ol']):
            # Skip navigation lists (already extracted)
            if any('nav' in c.lower() for c in lst.get('class', [])):
                continue
            
            list_html = str(lst)
            name = self._generate_component_name('list')
            
            component = Component(
                type='list',
                name=name,
                html=list_html,
                css_properties=self._get_inline_styles(lst),
                framework_hints=self._get_class_hints(lst),
            )
            
            self.components['list'].append(component)
    
    def _generate_component_name(self, component_type: str) -> str:
        """Generate a unique component name."""
        if component_type not in self.component_counter:
            self.component_counter[component_type] = 0
        
        self.component_counter[component_type] += 1
        count = self.component_counter[component_type]
        
        return f"{component_type}_{count}"
    
    def _get_inline_styles(self, element) -> Dict[str, str]:
        """Extract inline styles from an element."""
        style = element.get('style', '')
        if not style:
            return {}
        
        styles = {}
        for prop in style.split(';'):
            if ':' in prop:
                key, value = prop.split(':', 1)
                styles[key.strip()] = value.strip()
        
        return styles
    
    def _get_class_hints(self, element) -> List[str]:
        """Get class names that hint at frameworks."""
        classes = element.get('class', [])
        hints = []
        
        for cls in classes:
            if cls.startswith('tw-') or cls.startswith('sm:') or cls.startswith('md:') or cls.startswith('lg:'):
                hints.append('tailwind')
            elif cls.startswith('Mui') or cls.startswith('makeStyles'):
                hints.append('material-ui')
            elif cls.startswith('chakra-'):
                hints.append('chakra-ui')
            elif cls.startswith('ant-'):
                hints.append('antd')
            elif cls.startswith('shadcn-') or cls.startswith('ui-'):
                hints.append('shadcn')
        
        return list(set(hints))
    
    def _analyze_component_styles(self, soup: BeautifulSoup):
        """Analyze CSS for component styling."""
        # Extract <style> tags
        style_tags = soup.find_all('style')
        for style in style_tags:
            if style.string:
                # Parse CSS and associate with components
                pass  # Enhanced CSS parsing would go here
    
    def _check_accessibility(self):
        """Check accessibility for all components."""
        for component_type, components in self.components.items():
            for component in components:
                # Enhanced accessibility checking
                if component.type == 'button':
                    if not component.accessibility.get('has_text'):
                        component.accessibility['issues'] = component.accessibility.get('issues', [])
                        component.accessibility['issues'].append('Button has no accessible text')
    
    def _detect_frameworks(self, soup: BeautifulSoup):
        """Detect frameworks used in the page."""
        # Check for framework-specific attributes
        if soup.find(True, {'v-bind': True}) or soup.find(True, {'v-if': True}):
            logger.info("Vue.js detected")
        
        if soup.find(True, {'ng-app': True}) or soup.find(True, {'*ngIf': True}):
            logger.info("Angular detected")
        
        if soup.find(True, {'data-reactroot': True}):
            logger.info("React detected")
    
    def get_components_by_type(self, component_type: str) -> List[Component]:
        """Get all components of a specific type."""
        return self.components.get(component_type, [])
    
    def get_all_components(self) -> List[Component]:
        """Get all extracted components."""
        all_components = []
        for components in self.components.values():
            all_components.extend(components)
        return all_components
    
    def export_components(self, output_dir: str) -> Dict[str, str]:
        """Export components to individual files."""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        exported_files = {}
        
        for component_type, components in self.components.items():
            type_dir = output_path / component_type
            type_dir.mkdir(parents=True, exist_ok=True)
            
            for component in components:
                filename = f"{component.name}.html"
                filepath = type_dir / filename
                
                with open(filepath, 'w') as f:
                    f.write(component.html)
                
                component.file_path = str(filepath)
                exported_files[component.name] = str(filepath)
        
        return exported_files
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert all components to dictionary format."""
        return {
            component_type: [asdict(c) for c in components]
            for component_type, components in self.components.items()
        }
