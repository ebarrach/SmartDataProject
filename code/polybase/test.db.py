from app.database import SessionLocal
from sqlalchemy import text

def test_connection():
    try:
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        print("✅ Connexion réussie à la base de données")
    except Exception as e:
        print("❌ Erreur de connexion :", e)
    finally:
        db.close()

if __name__ == "__main__":
    test_connection()
