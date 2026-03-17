from fastapi import FastAPI

# routes
from backend.routes.chat import router as chat_router
from backend.routes.image import router as image_router
from backend.routes.vision import router as vision_router


app = FastAPI(
    title="Local Multimodal AI Assistant",
    version="0.1.0"
)


@app.get("/")
def root():
    return "AI Assistant Backend Running"


# register routes
app.include_router(chat_router, prefix="/chat", tags=["chat"])

app.include_router(image_router, prefix="/image", tags=["image"])

app.include_router(vision_router, prefix="/vision", tags=["vision"])