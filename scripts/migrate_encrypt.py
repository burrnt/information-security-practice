from app.database import SessionLocal
from app.crypto.encryption import encrypt_field
from sqlalchemy import text

def migrate():
    db = SessionLocal()
    try:
        # Перевіряємо структуру та витягуємо користувачів, у яких ще немає шифротексту
        result = db.execute(text("SELECT id, email FROM users WHERE encrypted_email IS NULL OR encrypted_email = ''"))
        users = result.fetchall()
        print(f"[МІГРАЦІЯ] Знайдено {len(users)} записів для криптографічного шифрування.")

        for user_id, raw_email in users:
            if raw_email:
                encrypted = encrypt_field(raw_email)
                db.execute(
                    text("UPDATE users SET encrypted_email = :enc WHERE id = :id"),
                    {"enc": encrypted, "id": user_id}
                )
                print(f" -> Користувач #{user_id}: Дані успішно зашифровано.")

        db.commit()
        print("[УСПІХ] Міграція персональних даних завершена.")
    except Exception as e:
        db.rollback()
        print(f"[ПОМИЛКА] Під час міграції виник збій: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    migrate()
