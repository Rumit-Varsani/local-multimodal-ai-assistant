import re


class MessageParserService:
    SEGMENT_PATTERNS = [
        re.compile(r"my name is\s+[^?!.]+[?!.]?", re.IGNORECASE),
        re.compile(r"what(?:'s| is) my name\??", re.IGNORECASE),
        re.compile(r"i live(?:\s+in)?\s+[^?!.]+[?!.]?", re.IGNORECASE),
        re.compile(r"where do i live\??", re.IGNORECASE),
        re.compile(r"i like\s+[^?!.]+[?!.]?", re.IGNORECASE),
        re.compile(r"what do i like\??", re.IGNORECASE),
        re.compile(r"i prefer\s+[^?!.]+[?!.]?", re.IGNORECASE),
        re.compile(r"what do i prefer\??", re.IGNORECASE),
        re.compile(r"write\s+[^?!.]+[?!.]?", re.IGNORECASE),
        re.compile(r"explain\s+[^?!.]+[?!.]?", re.IGNORECASE),
    ]

    NOISE_PATTERNS = [
        re.compile(r"answer one by one of (?:these|this) questions[.?!]?", re.IGNORECASE),
        re.compile(r"one by one[.?!]?", re.IGNORECASE),
    ]

    def parse(self, message: str):
        normalized = " ".join(message.strip().split())
        if not normalized:
            return []

        cleaned = normalized
        for pattern in self.NOISE_PATTERNS:
            cleaned = pattern.sub(" ", cleaned)
        cleaned = " ".join(cleaned.split())

        segments = []
        occupied_ranges = []

        for pattern in self.SEGMENT_PATTERNS:
            for match in pattern.finditer(cleaned):
                start, end = match.span()
                if self._overlaps(start, end, occupied_ranges):
                    continue

                segment = match.group(0).strip().strip(" .")
                if segment:
                    segments.append((start, segment))
                    occupied_ranges.append((start, end))

        segments.sort(key=lambda item: item[0])
        parsed_segments = [segment for _, segment in segments]

        if len(parsed_segments) >= 2:
            return parsed_segments

        return [normalized]

    def _overlaps(self, start: int, end: int, occupied_ranges):
        for existing_start, existing_end in occupied_ranges:
            if start < existing_end and end > existing_start:
                return True
        return False
