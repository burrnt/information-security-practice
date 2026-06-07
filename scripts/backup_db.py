import sys
import os
import shutil
from datetime import datetime
from cryptography.fernet import Fernet

# Додаємо кореневу директорію проекту до шляхів пошуку модулів
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.crypto.key_manager import get_encryption_key

def create_backup():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Твій реальний перевірений шлях до БД в корені контейнера
    db_path = "dekanat.db"
    backup_dir = "backups"
        
    os.makedirs(backup_dir, exist_ok=True)
    backup_path = f"{backup_dir}/dekanat_backup_{timestamp}.db"
    
    # 1. Копіювання файлу SQLite
    shutil.copy2(db_path, backup_path)
    
    # 2. Шифрування копії через Fernet
    f = Fernet(get_encryption_key())
    with open(backup_path, "rb") as file:
        file_data = file.read()
        
    encrypted_data = f.encrypt(file_data)
    encrypted_path = f"{backup_path}.enc"
    
    with open(encrypted_path, "wb") as file:
        file.write(encrypted_data)
        
    # 3. Видалення відкритої копії
    os.remove(backup_path)
    print(f"[БЕКАП] Зашифровану резервну копію створено: {encrypted_path}")
    return encrypted_path

if __name__ == "__main__":
    create_backup()
