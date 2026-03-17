from fastapi import APIRouter, UploadFile, File
import shutil

router = APIRouter()


@router.post("/upload-image")
def upload_image(file: UploadFile = File(...)):

    save_path = f"storage/images/{file.filename}"

    with open(save_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return {"message": "Image uploaded", "filename": file.filename}