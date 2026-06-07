from cryptography.fernet import Fernet

key = Fernet.generate_key()
print("\n=== ЗГЕНЕРОВАНИЙ КЛЮЧ FERNET ДЛЯ ПРАКТИЧНОЇ 7 ===")
print(f"ENCRYPTION_KEY={key.decode()}")
print("================================================\n")
print("Збережіть цей ключ у docker-compose.yml в секцію environment.")
