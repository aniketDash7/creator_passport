from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from trust_engine.services.crypto import CryptoService
from trust_engine.config import settings

router = APIRouter()
crypto_service = CryptoService(storage_dir=settings.CREDS_DIR)

class IdentityRegisterRequest(BaseModel):
    username: str
    email: str = "user@example.com"

@router.post("/register")
async def register_identity(request: IdentityRegisterRequest):
    """
    Registers a new creator identity and issues a digital certificate.
    In a real app, this would verify ID. Here, it generates keys.
    """
    try:
        # Issue Cert
        # Note: This is a synchronous operation (crypto gen), might block event loop 
        # but fine for prototype.
        key_path, cert_path = crypto_service.issue_user_cert(request.username, request.email)
        
        return {
            "status": "success",
            "message": f"Identity created for {request.username}",
            "credentials": {
                "key_path": key_path,
                "cert_path": cert_path
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
