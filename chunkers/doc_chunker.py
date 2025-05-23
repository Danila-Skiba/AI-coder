import re

class DocChunker:
    header_pattern = re.compile(r"^(#{1,6})\s+(.*)")

    def __init__(self, content, filename):
        self.lines = content.splitlines()
        self.filename = filename

    def chunk(self):
        chunks = []
        stack = []

        for i, line in enumerate(self.lines, start=1):
            header_match = self.header_pattern.match(line)
            if header_match:
                level = len(header_match.group(1))
                title = header_match.group(2).strip()

                while stack and stack[-1][0] >= level:
                    lvl, sec, start, cont = stack.pop()
                    if cont:
                        full_section = " > ".join(s[1] for s in stack + [(lvl, sec)])
                        chunks.append({
                            "id": f"{self.filename}_chunk_{start}",
                            "type": "doc",
                            "file": self.filename,
                            "section": full_section,
                            "content": "\n".join(cont).rstrip(),
                            "start_line": start,
                            "end_line": i - 1,
                            "source": "doc",
                            "chunk_type": "documentation",
                            "linked_chunks": []
                        })

                stack.append((level, title, i, [line]))
            else:
                if stack:
                    stack[-1][3].append(line)

        last_line = len(self.lines)
        while stack:
            lvl, sec, start, cont = stack.pop()
            if cont:
                full_section = " > ".join(s[1] for s in stack + [(lvl, sec)])
                chunks.append({
                    "id": f"{self.filename}_chunk_{start}",
                    "type": "doc",
                    "file": self.filename,
                    "section": full_section,
                    "content": "\n".join(cont).rstrip(),
                    "start_line": start,
                    "end_line": last_line,
                    "source": "doc",
                    "chunk_type": "documentation",
                    "linked_chunks": []
                })

        return chunks