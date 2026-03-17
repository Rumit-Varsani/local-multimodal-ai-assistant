from fastapi import APIRouter, UploadFile, File, Form
from backend.agents.vision_agent import VisionAgent

router = APIRouter()

vision_agent = VisionAgent()


@router.post("/analyze")
async def analyze_image(
    prompt: str = Form(...),
    image: UploadFile = File(...)
):

    image_bytes = await image.read()

    result = vision_agent.run(prompt, image_bytes)

    return {"response": result}