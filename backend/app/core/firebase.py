"""
    Firebase Admin SDK initialisation.

    Initialises the Firebase app once and exposes:
      - db      → Firestore client
      - bucket  → Firebase Storage bucket
      - auth    → Firebase Auth client
"""

import firebase_admin
from firebase_admin import credentials, firestore, storage, auth
from app.config import settings


def _init_firebase():
    if not firebase_admin._apps:
        cred = credentials.Certificate(settings.FIREBASE_CREDENTIALS_PATH)
        firebase_admin.initialize_app(cred, {
            "storageBucket": settings.FIREBASE_STORAGE_BUCKET,
        })


_init_firebase()

db     = firestore.client()
bucket = storage.bucket()
auth   = auth