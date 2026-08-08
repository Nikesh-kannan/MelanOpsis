from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.config import APP_NAME, VERSION, CORS_ORIGINS, IMAGES_DIR
from app.db.database import engine, Base
from app.models.inference import inference_service
from app.api import health, analyze, cases, stats

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 1. Initialize SQLite tables
    print("[Main] Creating database tables if needed...")
    Base.metadata.create_all(bind=engine)
    
    # 2. Pre-load PyTorch model into memory once at startup
    print("[Main] Pre-loading PyTorch model into memory...")
    inference_service.load_model()
    
    yield
    print("[Main] Application shutting down...")

app = FastAPI(
    title=APP_NAME,
    version=VERSION,
    description="Backend service for DermScanI AI-assisted skin lesion triage.",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount uploaded images directory for static retrieval
app.mount("/data/images", StaticFiles(directory=str(IMAGES_DIR)), name="images")

# Register API routers
app.include_router(health.router, prefix="/api", tags=["Health"])
app.include_router(analyze.router, prefix="/api", tags=["Analyze"])
app.include_router(cases.router, prefix="/api", tags=["Cases"])
app.include_router(stats.router, prefix="/api", tags=["Stats"])

@app.get("/")
def read_root():
    return {
        "app": APP_NAME,
        "status": "online",
        "docs": "/docs",
        "version": VERSION
    }
