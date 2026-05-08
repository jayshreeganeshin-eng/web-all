"""
Internationalization (i18n) module for web-all v4.2.0
Provides multi-language support for worldwide users.
"""

import json
from pathlib import Path
from typing import Dict, Optional

# Default language
DEFAULT_LANG = "en"

# Supported languages
SUPPORTED_LANGUAGES = {
    "en": "English",
    "es": "Español",
    "fr": "Français",
    "de": "Deutsch",
    "zh": "中文",
    "ja": "日本語",
    "ko": "한국어",
    "ru": "Русский",
    "ar": "العربية",
    "pt": "Português",
    "it": "Italiano",
}

# Current language setting
_current_lang: str = DEFAULT_LANG
_translations: Dict[str, Dict] = {}


def get_locales_dir() -> Path:
    """Get the locales directory path."""
    return Path(__file__).parent.parent / "locales"


def load_language(lang_code: str) -> bool:
    """
    Load translations for a specific language.
    
    Args:
        lang_code: Language code (e.g., 'en', 'es', 'fr')
    
    Returns:
        True if loaded successfully, False otherwise
    """
    global _translations
    
    locales_dir = get_locales_dir()
    lang_file = locales_dir / f"{lang_code}.json"
    
    if not lang_file.exists():
        # Try to load from alternative location
        alt_file = Path(__file__).parent / f"{lang_code}.json"
        if alt_file.exists():
            lang_file = alt_file
        else:
            return False
    
    try:
        with open(lang_file, "r", encoding="utf-8") as f:
            _translations[lang_code] = json.load(f)
        return True
    except Exception:
        return False


def set_language(lang_code: str) -> bool:
    """
    Set the current language.
    
    Args:
        lang_code: Language code to set
    
    Returns:
        True if successful, False otherwise
    """
    global _current_lang
    
    if lang_code not in SUPPORTED_LANGUAGES:
        return False
    
    if lang_code != DEFAULT_LANG and lang_code not in _translations:
        if not load_language(lang_code):
            return False
    
    _current_lang = lang_code
    return True


def get_current_language() -> str:
    """Get the current language code."""
    return _current_lang


def get_available_languages() -> Dict[str, str]:
    """Get dictionary of available languages."""
    return SUPPORTED_LANGUAGES.copy()


def t(key: str, default: Optional[str] = None, **kwargs) -> str:
    """
    Translate a key to the current language.
    
    Args:
        key: Translation key (dot-separated, e.g., 'clone.starting')
        default: Default value if translation not found
        **kwargs: Format arguments for the translation string
    
    Returns:
        Translated string or default/key if not found
    """
    global _current_lang, _translations
    
    # Get translations for current language or fallback to English
    lang_data = _translations.get(_current_lang, {})
    if not lang_data and _current_lang != DEFAULT_LANG:
        lang_data = _translations.get(DEFAULT_LANG, {})
    
    # Navigate nested keys
    keys = key.split(".")
    value = lang_data
    for k in keys:
        if isinstance(value, dict) and k in value:
            value = value[k]
        else:
            value = None
            break
    
    # Fallback to default or key
    if value is None:
        value = default if default is not None else key
    
    # Format with kwargs
    if isinstance(value, str) and kwargs:
        try:
            value = value.format(**kwargs)
        except KeyError:
            pass
    
    return value


def t_all(key: str, default: Optional[str] = None) -> Dict[str, str]:
    """
    Get translation for a key in all available languages.
    
    Args:
        key: Translation key
        default: Default value if translation not found
    
    Returns:
        Dictionary of language_code -> translation
    """
    result = {}
    
    for lang_code in SUPPORTED_LANGUAGES:
        if lang_code == DEFAULT_LANG:
            lang_data = _translations.get(DEFAULT_LANG, {})
        else:
            if lang_code not in _translations:
                load_language(lang_code)
            lang_data = _translations.get(lang_code, {})
        
        keys = key.split(".")
        value = lang_data
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                value = None
                break
        
        result[lang_code] = value if value is not None else (default or key)
    
    return result


# Convenience aliases
_ = t
translate = t


# Initialize with default language
load_language(DEFAULT_LANG)
