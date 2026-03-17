from fastapi import APIRouter, UploadFile, File
from pydantic import BaseModel

from backend.agents.image_agent import ImageAgent

router = APIRouter()

image_agent = ImageAgent()


class ImageRequest(BaseModel):
    prompt: str


# generate image
@router.post("/generate")
def generate_image(request: ImageRequest):

    result = image_agent.generate(request.prompt)

    return result


# upload image
@router.post("/upload-image")
async def upload_image(file: UploadFile = File(...)):

    contents = await file.read()

    path = f"storage/images/{file.filename}"

    with open(path, "wb") as f:
        f.write(contents)

    return {"image_path": path}