from cryptography.fernet import Fernet, InvalidToken
from app.crypto.key_manager import get_encryption_key

def get_fernet() -> Fernet:
    """Створює об’єкт Fernet з поточним криптографічним ключем."""
    return Fernet(get_encryption_key())

def encrypt_field(value: str) -> str:
    """Шифрує текстове значення за допомогою AES-128-CBC."""
    if not value:
        return ""
    f = get_fernet()
    return f.encrypt(value.encode("utf-8")).decode("utf-8")

def decrypt_field(encrypted_value: str) -> str:
    """Розшифровує значення. Повертає дешифрований текст або маркер помилки."""
    if not encrypted_value:
        return ""
    try:
        f = get_fernet()
        return f.decrypt(encrypted_value.encode("utf-8")).decode("utf-8")
    except (InvalidToken, Exception):
        return "[ПОМИЛКА РОЗШИФРУВАННЯ — невірний або відсутній ключ]"
