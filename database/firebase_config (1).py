import firebase_admin
from firebase_admin import credentials, auth, firestore
import os

def initialize_firebase():
    if not firebase_admin._apps:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        cert_path = os.path.join(base_dir, "config", "serviceAccountKey.json")
        if not os.path.exists(cert_path):
            raise FileNotFoundError(f"serviceAccountKey.json not found at {cert_path}")
        cred = credentials.Certificate(cert_path)
        firebase_admin.initialize_app(cred)
    return firestore.client()

def create_user_in_firebase(email, password):
    try:
        user = auth.create_user(email=email, password=password)
        return {"success": True, "user": user}
    except Exception as e:
        return {"success": False, "error": str(e)}

def save_scrape_to_history(email, url, title, count):
    try:
        db = firestore.client()
        db.collection("history").add({
            "user_email": email,
            "url":        url,
            "title":      title,
            "rows_count": count,
            "timestamp":  firestore.SERVER_TIMESTAMP
        })
        return True
    except Exception:
        return False
