import re

class CodeChunker:
    func_pattern = re.compile(r"^\s*def\s+(\w+)\s*\(")
    class_pattern = re.compile(r"^\s*class\s+(\w+)\s*[:\(]?")

    def __init__(self, content, filename):
        self.lines = content.splitlines()
        self.filename = filename

    def get_indent_level(self, line):
        return len(line) - len(line.lstrip(' '))

    def chunk(self):
        chunks = []
        stack = []  # (id, indent, lines, section, start_line)

        for i, line in enumerate(self.lines, start=1):
            indent = self.get_indent_level(line)
            func_match = self.func_pattern.match(line)
            class_match = self.class_pattern.match(line)

            if func_match or class_match:
                while stack and indent <= stack[-1][1]:
                    chunk_id, _, current_lines, current_section, start_line = stack.pop()
                    content = "\n".join(current_lines).rstrip()
                    if content:
                        chunks.append({
                            "id": chunk_id,
                            "type": "code",
                            "file": self.filename,
                            "section": current_section,
                            "content": content,
                            "start_line": start_line,
                            "end_line": i - 1,
                            "source": "code",
                            "chunk_type": "code",
                            "linked_chunks": []
                        })

                name = func_match.group(1) if func_match else class_match.group(1)
                start_line = i
                current_section = name
                parent_id = stack[-1][0] if stack else None
                chunk_id = f"{self.filename}_{name}_{start_line}"
                if parent_id:
                    chunk_id = f"{parent_id}.{name}_{start_line}"

                stack.append((chunk_id, indent, [line], current_section, start_line))
            else:
                if stack:
                    stack[-1][2].append(line)

        last_line = len(self.lines)
        while stack:
            chunk_id, _, current_lines, current_section, start_line = stack.pop()
            content = "\n".join(current_lines).rstrip()
            if content:
                chunks.append({
                    "id": chunk_id,
                    "type": "code",
                    "file": self.filename,
                    "section": current_section,
                    "content": content,
                    "start_line": start_line,
                    "end_line": last_line,
                    "source": "code",
                    "chunk_type": "code",
                    "linked_chunks": []
                })

        return chunks
