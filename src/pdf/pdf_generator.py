import pdfkit
import markdown2
import os

class PDFGenerator:

    def generate_pdf(self, markdown_text: str, output_path: str) -> str:
        """
        Converts markdown text → HTML → PDF
        using pdfkit + wkhtmltopdf (Windows compatible).
        """

        # Convert markdown to HTML
        html_body = markdown2.markdown(markdown_text)

        # Minimal professional template
        html = f"""
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    margin: 40px;
                    line-height: 1.6;
                }}
                h1, h2, h3 {{
                    color: #2c3e50;
                }}
                ul {{
                    margin-left: 20px;
                }}
                .source {{
                    font-size: 12px;
                    color: #555;
                }}
            </style>
        </head>
        <body>
            {html_body}
        </body>
        </html>
        """

        # Ensure directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        # Convert HTML → PDF
        pdfkit.from_string(html, output_path)

        return output_path
