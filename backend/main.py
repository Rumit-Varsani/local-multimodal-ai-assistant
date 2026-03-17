from fastapi import FastAPI

# ROUTES
from backend.routes.chat import router as chat_router
from backend.routes.image import router as image_router
from backend.routes.vision import router as vision_router

app = FastAPI(title="Local Multimodal AI Assistant")


@app.get("/")
def root():
    return {"status": "AI system running"}


# Register routes
app.include_router(chat_router, prefix="/chat")
app.include_router(image_router, prefix="/image")
app.include_router(vision_router, prefix="/vision")