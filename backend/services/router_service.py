import re


class RouterService:

    def route(self, message: str, image: bool = False):

        message_lower = message.lower()

        # If image attached
        if image:
            if any(word in message_lower for word in [
                "edit", "change", "remove", "replace", "style", "generate"
            ]):
                return "image_edit"

            return "vision"

        # Chat requests
        if any(word in message_lower for word in [
            "hello", "hi", "explain", "what", "why", "how", "tell"
        ]):
            return "chat"

        # Memory related
        if any(word in message_lower for word in [
            "remember", "recall", "memory", "previous"
        ]):
            return "memory"

        return "chat"