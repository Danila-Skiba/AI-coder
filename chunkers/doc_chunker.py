import re

class DocChunker:
    header_pattern = re.compile(r"^(#{1,6})\s+(.*)")

    def __init__(self, content, filename):
        self.content = content.splitlines()
        self.filename = filename

    def chunk(self):
        chunks = []
        current_section = None
        current_content = []
        start_line = 1

        for i, line in enumerate(self.content, start=1):
            header_match = self.header_pattern.match(line)
            if header_match:
                # Если сейчас есть накопленный чанк — сохраняем
                if current_section is not None:
                    chunks.append({
                        "id": f"{self.filename}_chunk_{start_line}",
                        "type": "doc",
                        "file": self.filename,
                        "section": current_section.strip(),
                        "content": "\n".join(current_content).rstrip(),
                        "start_line": start_line,
                        "end_line": i - 1,
                        "source": "doc",
                        "chunk_type": "documentation",
                        "linked_chunks": []
                    })
                current_section = header_match.group(2)
                current_content = [line]
                start_line = i
            else:
                if current_section is not None:
                    current_content.append(line)

        # Добавляем последний накопленный чанк
        if current_section is not None and current_content:
            chunks.append({
                "id": f"{self.filename}_chunk_{start_line}",
                "type": "doc",
                "file": self.filename,
                "section": current_section.strip(),
                "content": "\n".join(current_content).rstrip(),
                "start_line": start_line,
                "end_line": len(self.content),
                "source": "doc",
                "chunk_type": "documentation",
                "linked_chunks": []
            })

        return chunks
