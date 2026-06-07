import os
import sys

def get_encryption_key() -> bytes:
    """Отримує ключ шифрування зі змінної оточення з обробкою помилки."""
    key = os.getenv("ENCRYPTION_KEY")
    if not key:
        print("КРИТИЧНА ПОМИЛКА: ENCRYPTION_KEY не встановлено у docker-compose.yml!")
        sys.exit(1)
    return key.encode()
