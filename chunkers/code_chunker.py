import ast
from typing import List, Dict

class CodeChunker:
    def chunk_code(self, code: str, filename: str) -> List[Dict]:
        tree = ast.parse(code)
        chunks = []

        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                start_line = node.lineno
                end_line = getattr(node, 'end_lineno', None)
                if end_line is None:
                    end_line = start_line + 10  # примерно

                code_lines = code.splitlines()
                chunk_code = "\n".join(code_lines[start_line-1:end_line])

                chunk = {
                    "id": f"{filename}_{node.name}_{start_line}",
                    "type": "code",
                    "file": filename,
                    "section": node.name,
                    "content": chunk_code,
                    "start_line": start_line,
                    "end_line": end_line,
                    "source": "code"
                }
                chunks.append(chunk)
        return chunks
