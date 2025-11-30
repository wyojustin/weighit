#!/usr/bin/env python3
"""
Generate a printable PDF from the volunteer cheatsheet markdown file.
"""
import sys
from pathlib import Path

try:
    import markdown
except ImportError:
    print("Installing markdown...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "markdown"])
    import markdown

try:
    from weasyprint import HTML, CSS
except ImportError:
    print("Installing weasyprint...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "weasyprint"])
    from weasyprint import HTML, CSS


def generate_pdf():
    # Read the markdown file
    md_path = Path(__file__).parent / "docs" / "volunteer_cheatsheet.md"
    with open(md_path, "r") as f:
        md_content = f.read()

    # Convert markdown to HTML
    html_content = markdown.markdown(md_content, extensions=['tables', 'fenced_code'])

    # Add CSS styling for better print layout
    css_style = """
    @page {
        size: Letter;
        margin: 0.75in;
    }

    body {
        font-family: Arial, Helvetica, sans-serif;
        font-size: 11pt;
        line-height: 1.4;
        color: #000;
    }

    h1 {
        font-size: 20pt;
        margin-top: 0;
        margin-bottom: 0.5em;
        border-bottom: 3px solid #333;
        padding-bottom: 0.3em;
    }

    h2 {
        font-size: 14pt;
        margin-top: 1.2em;
        margin-bottom: 0.5em;
        background-color: #f0f0f0;
        padding: 0.3em 0.5em;
        border-left: 4px solid #333;
    }

    h3 {
        font-size: 12pt;
        margin-top: 1em;
        margin-bottom: 0.4em;
    }

    ul, ol {
        margin-top: 0.5em;
        margin-bottom: 0.5em;
    }

    li {
        margin-bottom: 0.3em;
    }

    code {
        background-color: #f5f5f5;
        padding: 0.1em 0.3em;
        border-radius: 3px;
        font-family: monospace;
    }

    strong {
        font-weight: bold;
    }

    table {
        width: 100%;
        border-collapse: collapse;
        margin: 1em 0;
    }

    th, td {
        border: 1px solid #ccc;
        padding: 0.5em;
        text-align: left;
    }

    th {
        background-color: #f0f0f0;
        font-weight: bold;
    }

    hr {
        border: none;
        border-top: 2px solid #ccc;
        margin: 1.5em 0;
    }

    /* Print-specific styles */
    @media print {
        body {
            font-size: 10pt;
        }

        h1 {
            page-break-after: avoid;
        }

        h2, h3 {
            page-break-after: avoid;
        }

        ul, ol, table {
            page-break-inside: avoid;
        }
    }
    """

    # Create full HTML document
    full_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>WeighIt Volunteer Cheat Sheet</title>
    </head>
    <body>
        {html_content}
    </body>
    </html>
    """

    # Generate PDF
    output_path = Path(__file__).parent / "docs" / "volunteer_cheatsheet.pdf"
    HTML(string=full_html).write_pdf(
        output_path,
        stylesheets=[CSS(string=css_style)]
    )

    print(f"✓ PDF generated successfully: {output_path}")
    return output_path


if __name__ == "__main__":
    generate_pdf()
