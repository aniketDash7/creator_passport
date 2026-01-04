import os

class Settings:
    PROJECT_NAME = "Authenticity Protocol Trust Engine"
    API_V1_STR = "/api/v1"
    
    # Storage
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    STORAGE_DIR = os.path.join(BASE_DIR, "storage")
    CREDS_DIR = os.path.join(STORAGE_DIR, "creds")
    UPLOADS_DIR = os.path.join(STORAGE_DIR, "uploads")
    
    # Init dirs
    os.makedirs(CREDS_DIR, exist_ok=True)
    os.makedirs(UPLOADS_DIR, exist_ok=True)

settings = Settings()
