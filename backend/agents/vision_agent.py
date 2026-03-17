from backend.services.vision_service import VisionService


class VisionAgent:

    def __init__(self):

        self.vision_service = VisionService()

    def run(self, prompt, image_bytes):

        return self.vision_service.analyze_image(prompt, image_bytes)