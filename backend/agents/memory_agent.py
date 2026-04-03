# backend/agents/memory_agent.py

from backend.services.brain_state_service import BrainStateService
from backend.services.memory_service import MemoryService


class MemoryAgent:
    FACT_PREFIXES = {
        "name": "User name is ",
        "location": "User lives in ",
        "work": "User works as ",
        "likes": "User likes ",
        "preference": "User prefers ",
    }

    FACT_QUESTIONS = {
        "name": [
            "what is my name",
            "what's my name",
            "tell me my name",
            "do you know my name",
        ],
        "location": [
            "where do i live",
            "where am i living",
            "what city do i live in",
            "what country do i live in",
        ],
        "work": [
            "what do i do for work",
            "where do i work",
            "what is my job",
            "what do i work as",
        ],
        "likes": [
            "what do i like",
            "what things do i like",
        ],
        "preference": [
            "what do i prefer",
            "what are my preferences",
        ],
    }

    STOPWORDS = {
        "a",
        "an",
        "and",
        "are",
        "do",
        "for",
        "i",
        "in",
        "is",
        "me",
        "my",
        "of",
        "on",
        "or",
        "the",
        "to",
        "what",
        "where",
        "who",
        "why",
        "you",
    }

    def __init__(self):
        self.memory = MemoryService()
        self.brain_state = BrainStateService()

    def get_context(self, query: str):
        memories = self.memory.retrieve(query)

        if not memories:
            return ""

        # Keep only memories that share meaningful words with the query.
        relevant = []
        query_tokens = self._tokenize(query)

        for mem in memories:
            memory_tokens = self._tokenize(mem)
            if not query_tokens or query_tokens.intersection(memory_tokens):
                relevant.append(mem)

        return "\n".join(relevant)

    def should_store(self, text: str):
        keywords = [
            "my name is",
            "i live",
            "i work",
            "i like",
            "i prefer"
        ]
        return any(k in text.lower() for k in keywords)

    def clean_memory(self, text: str):
        text_lower = text.lower()

        if "my name is" in text_lower:
            value = self._value_after_phrase(text, "my name is")
            return f"User name is {value}"

        elif "i live" in text_lower:
            value = self._value_after_phrase(text, "i live")
            if value.startswith("in "):
                value = value[3:]
            return f"User lives in {value}"

        elif "i work" in text_lower:
            value = self._value_after_phrase(text, "i work")
            if value.startswith("as "):
                value = value[3:]
            return f"User works as {value}"

        elif "i like" in text_lower:
            value = self._value_after_phrase(text, "i like")
            return f"User likes {value}"

        elif "i prefer" in text_lower:
            value = self._value_after_phrase(text, "i prefer")
            return f"User prefers {value}"

        return text.strip()

    def store_interaction(self, user_input: str, response: str):
        if self.should_store(user_input):
            clean = self.clean_memory(user_input)
            print("💾 Storing memory:", clean)
            self.memory.store(clean)
            self._sync_brain_fact(clean)

    def answer_fact_update(self, message: str):
        normalized_message = message.lower().strip()
        if normalized_message.endswith("?"):
            return None
        if normalized_message.startswith(("what ", "where ", "who ", "when ", "why ", "how ")):
            return None

        clean = self.clean_memory(message)
        if clean == message.strip():
            return None

        if clean.startswith(self.FACT_PREFIXES["name"]):
            value = clean[len(self.FACT_PREFIXES["name"]):].strip()
            return f"Okay, I'll remember that your name is {value}."

        if clean.startswith(self.FACT_PREFIXES["location"]):
            value = clean[len(self.FACT_PREFIXES["location"]):].strip()
            return f"Okay, I'll remember that you live in {value}."

        if clean.startswith(self.FACT_PREFIXES["work"]):
            value = clean[len(self.FACT_PREFIXES["work"]):].strip()
            return f"Okay, I'll remember that you work as {value}."

        if clean.startswith(self.FACT_PREFIXES["likes"]):
            value = clean[len(self.FACT_PREFIXES["likes"]):].strip()
            return f"Okay, I'll remember that you like {value}."

        return None

    def answer_preference_update(self, message: str):
        preference_value = self._extract_preference_value(message)
        if not preference_value:
            return None

        return f"Okay, I'll keep that in mind and prefer {preference_value}."

    def answer_personal_question(self, query: str):
        fact_type = self._detect_fact_question(query)
        if not fact_type:
            return None

        fact_value = self._find_fact_value(fact_type)
        if not fact_value:
            return "I don't have that information."

        if fact_type == "name":
            return f"Your name is {fact_value}."
        if fact_type == "location":
            return f"You live in {fact_value}."
        if fact_type == "work":
            return f"You work as {fact_value}."
        if fact_type == "likes":
            return f"You like {fact_value}."
        if fact_type == "preference":
            return f"You prefer {fact_value}."

        return None

    def get_response_style_instruction(self):
        preferences = self.brain_state.get_preferences()
        response_style = preferences.get("response_style", "")
        response_modes = preferences.get("response_modes", [])
        preference = self.brain_state.get_fact("preference") or self._find_fact_value("preference")
        if not preference:
            return "No saved response style preference."

        if response_style == "short" or "short" in response_modes:
            return "The user prefers short, concise answers."
        if response_style == "detailed" or "detailed" in response_modes:
            return "The user prefers more detailed answers."
        if "code-first" in response_modes or "code" in preference.lower():
            return "When relevant, prioritize code before explanation."

        return f"User preference: {preference}."

    def get_brain_facts(self):
        return self.brain_state.load()["facts"]

    def _tokenize(self, text: str):
        cleaned = text.lower().replace("\n", " ")
        tokens = set()

        for raw_token in cleaned.split():
            token = raw_token.strip(".,!?;:'\"()[]{}")
            if len(token) < 3:
                continue
            if token in self.STOPWORDS:
                continue
            tokens.add(token)

        return tokens

    def _detect_fact_question(self, query: str):
        normalized_query = query.lower().strip().rstrip("?.!")

        for fact_type, patterns in self.FACT_QUESTIONS.items():
            if any(pattern in normalized_query for pattern in patterns):
                return fact_type

        return None

    def _find_fact_value(self, fact_type: str):
        prefix = self.FACT_PREFIXES[fact_type]
        brain_value = self.brain_state.get_fact(fact_type)
        if brain_value:
            return brain_value

        memories = self.memory.retrieve_all()

        for memory in reversed(memories):
            if memory.startswith(prefix):
                return memory[len(prefix):].strip()

        return ""

    def _value_after_phrase(self, text: str, phrase: str):
        text_lower = text.lower()
        start_index = text_lower.find(phrase)
        if start_index == -1:
            return text.strip()

        value = text[start_index + len(phrase):].strip()
        return value.strip(" .!?")

    def _extract_preference_value(self, text: str):
        text_lower = text.lower().strip()
        if text_lower.endswith("?"):
            return ""
        if "i prefer" not in text_lower:
            return ""

        return self._value_after_phrase(text, "i prefer")

    def _sync_brain_fact(self, clean_memory: str):
        for fact_key, prefix in self.FACT_PREFIXES.items():
            if clean_memory.startswith(prefix):
                value = clean_memory[len(prefix):].strip()
                if fact_key == "preference":
                    self.brain_state.update_preference(value)
                else:
                    self.brain_state.update_fact(fact_key, value)
                return
