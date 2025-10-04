from database import SessionLocal
from models_db import User

def test_connection():
    db = SessionLocal()  # Open a session
    try:
        users = db.query(User).all()  # Query the users table
        print(f"Database connection successful! Found {len(users)} users.")
    except Exception as e:
        print(f"Database connection failed: {e}")
    finally:
        db.close()  # Always close the session

if __name__ == "__main__":
    test_connection()