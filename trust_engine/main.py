from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from trust_engine.routers import identity, content
from trust_engine.config import settings

app = FastAPI(title=settings.PROJECT_NAME)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static Files (for our creator passport frontend)
app.mount("/passport", StaticFiles(directory="trust_engine/static", html=True), name="static")

# Routers
app.include_router(identity.router, prefix="/api/identity", tags=["Identity"])
app.include_router(content.router, prefix="/api/content", tags=["Content"])

@app.get("/api/content/temp_hosted_signed.jpg")
async def get_demo_image():
    # Serve the locally signed sample for the demo
    return FileResponse("sample_signed.jpg", media_type="image/jpeg")

@app.get("/")
async def root():
    return {"message": "Authenticity Protocol Trust Engine is running. Visit /passport for the Creator App."}
