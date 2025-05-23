import os

from markdownify import markdownify as md

HTML_DIR = "html_docs"
MD_DIR = "md_docs"


def convert_all_html_to_md():
    os.makedirs(MD_DIR, exist_ok=True)

    for filename in os.listdir(HTML_DIR):
        if not filename.endswith(".html"):
            continue

        html_path = os.path.join(HTML_DIR, filename)
        md_path = os.path.join(MD_DIR, filename.replace(".html", ".md"))

        with open(html_path, "r", encoding="utf-8") as f:
            html = f.read()

        markdown = md(html, heading_style="ATX")

        with open(md_path, "w", encoding="utf-8") as f:
            f.write(markdown)

        print(f"[✓] Сконвертировано: {html_path} → {md_path}")


if __name__ == "__main__":
    convert_all_html_to_md()
