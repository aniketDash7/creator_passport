from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, EmailStr, Field
from trust_engine.services.crypto import CryptoService
from trust_engine.config import settings

router = APIRouter()
crypto_service = CryptoService(storage_dir=settings.CREDS_DIR)

class IdentityRegisterRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, pattern="^[a-zA-Z0-9_\-]+$")
    email: EmailStr

@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register_identity(request: IdentityRegisterRequest):
    """
    Registers a new creator identity and issues a digital certificate.
    Validates identity uniqueness and input format.
    """
    try:
        # Check if user already exists
        if crypto_service.check_identity_exists(request.username):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Identity already exists for username: {request.username}"
            )

        # Issue Cert
        key_path, cert_path = crypto_service.issue_user_cert(request.username, request.email)
        
        return {
            "status": "success",
            "message": f"Identity created for {request.username}",
            "credentials": {
                "key_path": key_path,
                "cert_path": cert_path
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}"
        )
