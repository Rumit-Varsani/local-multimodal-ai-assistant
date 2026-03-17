import base64
import requests
from PIL import Image
import io


class VisionService:

    def __init__(self):

        self.url = "http://localhost:11434/api/generate"
        self.model = "llava"

    def convert_to_png(self, image_bytes):

        image = Image.open(io.BytesIO(image_bytes))

        buffer = io.BytesIO()

        image.save(buffer, format="PNG")

        return buffer.getvalue()

    def analyze_image(self, prompt, image_bytes):

        png_image = self.convert_to_png(image_bytes)

        base64_image = base64.b64encode(png_image).decode("utf-8")

        payload = {
            "model": self.model,
            "prompt": prompt,
            "images": [base64_image],
            "stream": False
        }

        response = requests.post(self.url, json=payload)

        data = response.json()

        return data.get("response", "")