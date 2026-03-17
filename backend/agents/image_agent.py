from backend.services.comfyui_service import ComfyUIService


class ImageAgent:

    def __init__(self):

        self.comfy = ComfyUIService()

    def generate(self, prompt: str):

        result = self.comfy.generate_image(prompt)

        return result