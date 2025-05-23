import re

class CodeChunker:
    # Регулярки обновлены для учёта отступов и многострочного объявления функций и классов
    func_pattern = re.compile(r"^\s*def\s+(\w+)\s*\(")
    class_pattern = re.compile(r"^\s*class\s+(\w+)\s*[:\(]")

    def __init__(self, content, filename):
        self.content = content.splitlines()
        self.filename = filename

    def chunk(self):
        chunks = []
        current_section = None
        current_content = []
        start_line = 1

        for i, line in enumerate(self.content, start=1):
            func_match = self.func_pattern.match(line)
            class_match = self.class_pattern.match(line)

            if func_match or class_match:
                if current_section is not None:
                    chunks.append({
                        "id": f"{self.filename}_{current_section}_{start_line}",
                        "type": "code",
                        "file": self.filename,
                        "section": current_section,
                        "content": "\n".join(current_content).rstrip(),
                        "start_line": start_line,
                        "end_line": i - 1,
                        "source": "code",
                        "chunk_type": "code",
                        "linked_chunks": []
                    })
                current_section = func_match.group(1) if func_match else class_match.group(1)
                current_content = [line]
                start_line = i
            else:
                if current_section is not None:
                    current_content.append(line)

        if current_section is not None and current_content:
            chunks.append({
                "id": f"{self.filename}_{current_section}_{start_line}",
                "type": "code",
                "file": self.filename,
                "section": current_section,
                "content": "\n".join(current_content).rstrip(),
                "start_line": start_line,
                "end_line": len(self.content),
                "source": "code",
                "chunk_type": "code",
                "linked_chunks": []
            })

        return chunks
