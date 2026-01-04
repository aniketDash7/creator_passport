import os
import shutil
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from trust_engine.services.c2pa_service import C2PAService
from trust_engine.services.crypto import CryptoService # To get root path
from trust_engine.config import settings

router = APIRouter()
c2pa_service = C2PAService()
# We need access to root cert path logic
crypto_service = CryptoService(storage_dir=settings.CREDS_DIR) 

@router.post("/sign")
async def sign_content(
    file: UploadFile = File(...),
    username: str = Form(...)
):
    """
    Signs an uploaded image with the user's credentials.
    """
    # 1. Save uploaded file temporarily
    temp_input = os.path.join(settings.UPLOADS_DIR, f"temp_{file.filename}")
    temp_output = os.path.join(settings.UPLOADS_DIR, f"signed_{file.filename}")
    
    with open(temp_input, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    # 2. Resolve User Credentials
    # Assumption: User already registered via /identity/register
    safe_name = "".join(x for x in username if x.isalnum())
    key_path = os.path.join(settings.CREDS_DIR, f"{safe_name}_key.pem")
    cert_path = os.path.join(settings.CREDS_DIR, f"{safe_name}_cert.pem")
    
    root_key_path, root_cert_path = crypto_service.ensure_root_ca() # Ensure root exists/path known

    if not os.path.exists(key_path) or not os.path.exists(cert_path):
        raise HTTPException(status_code=404, detail="User identity not found. Please register first.")

    # 3. Sign
    try:
        # Chain: [Leaf, Root]
        chain_paths = [cert_path, root_cert_path]
        
        signed_path = c2pa_service.sign_content(
            input_path=temp_input,
            output_path=temp_output,
            key_path=key_path,
            cert_chain_paths=chain_paths,
            author_name=username
        )
        
        in_size = os.path.getsize(temp_input)
        out_size = os.path.getsize(signed_path)
        print(f"[DEBUG] Signed: In={in_size}b, Out={out_size}b (Added {out_size-in_size}b)")
        
        return FileResponse(
            signed_path, 
            media_type=file.content_type, 
            filename=f"signed_{file.filename}"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # Cleanup input (keep output for return)
        if os.path.exists(temp_input):
            os.remove(temp_input)

@router.post("/verify")
async def verify_content(file: UploadFile = File(...)):
    """
    Verifies the uploaded image and returns the C2PA manifest.
    """
    temp_input = os.path.join(settings.UPLOADS_DIR, f"verify_{file.filename}")
    
    try:
        with open(temp_input, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        # DEBUG: Check magic bytes
        with open(temp_input, "rb") as f:
            header = f.read(8)
            print(f"[DEBUG] Header Bytes: {header.hex()} ({header})")

        print(f"[DEBUG] Verify Request: File={file.filename}, Type={file.content_type}, Size={os.path.getsize(temp_input)} bytes")
        manifest = c2pa_service.verify_content(temp_input)
        print(f"[DEBUG] Verify Result: {manifest}")
        return JSONResponse(content=manifest)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if os.path.exists(temp_input):
            os.remove(temp_input)
