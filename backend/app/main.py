import os
# Memory optimizations for low-memory environments (e.g. Render free tier 512MB limit)
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["VECLIB_MAXIMUM_THREADS"] = "1"
os.environ["NUMEXPR_NUM_THREADS"] = "1"
os.environ["TOKENIZERS_PARALLELISM"] = "false"

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.v1.api_router import api_router
from app.core.database import close_mongo_connection
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("qnexus.main")

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url="/api/v1/openapi.json",
    docs_url="/docs"
)

# CORS Configuration - Explicit origins for secure credentials handling
extra_origins = [url.strip().rstrip("/") for url in settings.FRONTEND_URL.split(",") if url.strip()]
origins = list(set(filter(None, extra_origins + [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
])))

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_origin_regex=r"https://.*\.vercel\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

import os
from fastapi.staticfiles import StaticFiles

# Include API Router
app.include_router(api_router, prefix="/api/v1")

@app.get("/", tags=["Root"])
def root():
    return {
        "status": "healthy",
        "project": settings.PROJECT_NAME,
        "docs": "/docs",
        "api": "/api/v1"
    }

# Mount Static Files for Uploads and Question Diagrams
uploads_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "uploads")
os.makedirs(uploads_dir, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=uploads_dir), name="uploads")

@app.on_event("startup")
def startup_event():
    logger.info("Initializing Qnexus backend services...")
    try:
        from app.core.database import get_mongo_db
        from app.db.indexes import ensure_indexes
        from app.core.pinecone import ensure_pinecone_index
        from app.services.embedding_service import EmbeddingService

        db = get_mongo_db()
        ensure_indexes(db)
        ensure_pinecone_index()

        # In production, defer model loading to first request to stay well under Render's 512MB RAM limit
        if settings.ENV != "production":
            logger.info("Pre-warming SentenceTransformer embedding model...")
            EmbeddingService().embed_text("jee main previous year questions")
            logger.info("Database indexes, Pinecone index, and Embedding model ready.")
        else:
            logger.info("Production mode: embedding model will load lazily on first search to conserve memory.")
    except Exception as e:
        logger.warning(f"Startup initialization notice: {e}")

@app.on_event("shutdown")
def shutdown_event():
    logger.info("Shutting down Qnexus backend server")
    close_mongo_connection()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=settings.PORT, reload=True)


