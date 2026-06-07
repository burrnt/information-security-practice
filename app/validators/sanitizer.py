import bleach
import re

def sanitize_text(text: str) -> str:
    """Видаляє ВСІ HTML-теги з тексту для захисту від XSS атак."""
    if not text:
        return ""
    # Суворе правило: tags=[] видаляє будь-який HTML/JS код
    cleaned = bleach.clean(text, tags=[], strip=True)
    return cleaned.strip()

def contains_sql_patterns(text: str) -> bool:
    """Перевіряє наявність небезпечних SQL-патернів у тексті."""
    if not text:
        return False
    
    sql_patterns = [
        r"(\b(UNION|SELECT|INSERT|DELETE|DROP|ALTER|UPDATE)\b)",
        r"(--|;\/\*|\*\/)",
        r"(\bOR\b\s+\b1\s*=\s*1\b)",
        r"('" + r"|" + r'")'  # Спроба виходу за межі рядка в SQL
    ]
    for pattern in sql_patterns:
        if re.search(pattern, text, re.IGNORECASE):
            return True
    return False
