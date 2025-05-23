import re
from typing import List, Dict

class DocChunker:
    header_pattern = re.compile(r"^(#{1,6})\s+(.*)")

    def chunk_doc(self, text: str, filename: str, max_chunk_size: int = 1000) -> List[Dict]:
        lines = text.splitlines()
        chunks = []
        current_chunk_lines = []
        current_header = "No Header"
        chunk_id = 0

        def save_chunk():
            nonlocal chunk_id
            if current_chunk_lines:
                chunk_id += 1
                chunk_text = "\n".join(current_chunk_lines).strip()
                chunk = {
                    "id": f"{filename}_chunk_{chunk_id}",
                    "type": "doc",
                    "file": filename,
                    "section": current_header,
                    "content": chunk_text,
                    "source": "doc",
                    "chunk_type": "documentation",
                    "linked_chunks": []  # сюда будем добавлять связанные чанки кода
                }
                chunks.append(chunk)

        for line in lines:
            match = self.header_pattern.match(line)
            if match:
                save_chunk()
                current_chunk_lines = []
                current_header = match.group(2)
            current_chunk_lines.append(line)
            if len("\n".join(current_chunk_lines)) > max_chunk_size:
                save_chunk()
                current_chunk_lines = []

        save_chunk()
        return chunks
