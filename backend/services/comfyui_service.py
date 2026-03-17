import json
import uuid
import requests
from pathlib import Path


class ComfyUIService:

    def __init__(self):

        self.server_address = "127.0.0.1:8188"

        workflow_path = Path("models/workflows/text_to_image_api.json")

        with open(workflow_path) as f:
            self.workflow = json.load(f)

    def generate_image(self, prompt: str):

        workflow = self.workflow.copy()

        # Replace prompt text inside workflow
        for node in workflow.values():

            if "inputs" in node and "text" in node["inputs"]:
                node["inputs"]["text"] = prompt

        payload = {
            "prompt": workflow,
            "client_id": str(uuid.uuid4())
        }

        response = requests.post(
            f"http://{self.server_address}/prompt",
            json=payload
        )

        return response.json()