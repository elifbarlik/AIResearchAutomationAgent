"""
FastAPI application for the AI Research Automation Agent.

This module provides REST API endpoints for interacting with
the multi-agent research system.
"""

import os
from pathlib import Path
import markdown
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse, Response
from pydantic import BaseModel
from starlette.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from src.core.orchestrator import Orchestrator


app = FastAPI(
    title="AI Research Automation Agent",
    description="Multi-agent system for automated research and analysis",
    version="1.0.0"
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================================
# CONFIGURATION
# =========================================
REPORTS_DIR = Path("reports")

# =========================================
# INITIALIZATION
# =========================================
orc = Orchestrator()
app.mount("/static/reports", StaticFiles(directory="reports"), name="reports")

# =========================================
# HELPER FUNCTIONS
# =========================================

def convert_markdown_to_html(markdown_content: str, title: str = "Report") -> str:
    """
    Convert markdown content to a styled HTML document.

    Takes raw markdown text and converts it to a complete HTML document
    with professional styling, including support for code blocks, tables,
    and other markdown features.

    Args:
        markdown_content: Raw markdown text to convert
        title: Title for the HTML document (used in <title> tag)

    Returns:
        str: Complete HTML document with styling

    Example:
        >>> html = convert_markdown_to_html("# Hello\\nWorld", "My Report")
        >>> assert "<!DOCTYPE html>" in html
        >>> assert "<h1>Hello</h1>" in html
    """
    # Convert markdown to HTML with extensions
    html_content = markdown.markdown(
        markdown_content,
        extensions=['fenced_code', 'tables', 'toc']
    )

    # Wrap in clean HTML template with professional styling
    wrapped_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            line-height: 1.6;
            color: #333;
        }}
        h1, h2, h3, h4, h5, h6 {{
            margin-top: 1.5em;
            margin-bottom: 0.5em;
            color: #2c3e50;
        }}
        h1 {{
            border-bottom: 2px solid #3498db;
            padding-bottom: 0.3em;
        }}
        code {{
            background-color: #f4f4f4;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: 'Courier New', Courier, monospace;
        }}
        pre {{
            background-color: #f4f4f4;
            padding: 15px;
            border-radius: 5px;
            overflow-x: auto;
        }}
        pre code {{
            background-color: transparent;
            padding: 0;
        }}
        table {{
            border-collapse: collapse;
            width: 100%;
            margin: 1em 0;
        }}
        th, td {{
            border: 1px solid #ddd;
            padding: 12px;
            text-align: left;
        }}
        th {{
            background-color: #3498db;
            color: white;
        }}
        tr:nth-child(even) {{
            background-color: #f9f9f9;
        }}
        a {{
            color: #3498db;
            text-decoration: none;
        }}
        a:hover {{
            text-decoration: underline;
        }}
        blockquote {{
            border-left: 4px solid #3498db;
            padding-left: 15px;
            color: #666;
            margin: 1em 0;
        }}
    </style>
</head>
<body>
    {html_content}
</body>
</html>"""

    return wrapped_html


# =========================================
# REQUEST MODELS
# =========================================

class OverviewRequest(BaseModel):
    """Request model for overview research."""
    topic: str
    depth: str = "short"


class CompareRequest(BaseModel):
    """Request model for comparative research."""
    item_a: str
    item_b: str
    depth: str = "short"


class CustomRequest(BaseModel):
    """Request model for custom research with automatic mode detection."""
    query: str
    depth: str = "short"


# =========================================
# ENDPOINTS
# =========================================

@app.get("/health")
async def health_check():
    """
    Health check endpoint.

    Returns a simple status message to verify the API is running.

    Returns:
        dict: {"status": "ok"}
    """
    return {"status": "ok"}


@app.post("/research/overview")
async def research_overview(req: OverviewRequest):
    """
    Perform overview research on a single topic.

    Args:
        req: OverviewRequest containing topic and depth

    Returns:
        dict: Research results with status, report_path, etc.

    Raises:
        HTTPException: 400 if validation fails, 500 if pipeline fails
    """
    try:
        # Validate topic
        if not req.topic or not req.topic.strip():
            raise HTTPException(
                status_code=400,
                detail="Topic cannot be empty"
            )

        # Call orchestrator
        result = orc.run(
            mode="overview",
            topic=req.topic,
            depth=req.depth
        )

        # Check for errors in result
        if "error" in result:
            raise HTTPException(
                status_code=400,
                detail=f"Research failed at {result.get('stage', 'unknown')} stage: {result['error']}"
            )

        return result

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Overview research failed: {str(e)}"
        )


@app.post("/research/compare")
async def research_compare(req: CompareRequest):
    """
    Perform comparative research between two items.

    Args:
        req: CompareRequest containing item_a, item_b, and depth

    Returns:
        dict: Comparison results with status, report_path, etc.

    Raises:
        HTTPException: 400 if validation fails, 500 if pipeline fails
    """
    try:
        # Validate items
        if not req.item_a or not req.item_a.strip():
            raise HTTPException(
                status_code=400,
                detail="item_a cannot be empty"
            )

        if not req.item_b or not req.item_b.strip():
            raise HTTPException(
                status_code=400,
                detail="item_b cannot be empty"
            )

        # Call orchestrator
        result = orc.run(
            mode="compare",
            item_a=req.item_a,
            item_b=req.item_b,
            depth=req.depth
        )

        # Check for errors in result
        if "error" in result:
            raise HTTPException(
                status_code=400,
                detail=f"Comparison failed at {result.get('stage', 'unknown')} stage: {result['error']}"
            )

        return result

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Comparison research failed: {str(e)}"
        )


@app.post("/research/custom")
async def research_custom(req: CustomRequest):
    """
    Perform custom research with automatic mode detection.

    Detects whether to use overview or compare mode based on query content.
    If query contains " vs ", uses compare mode. Otherwise uses overview mode.

    Args:
        req: CustomRequest containing query and depth

    Returns:
        dict: Research results (same structure as overview/compare)

    Raises:
        HTTPException: 400 if validation fails, 500 if pipeline fails
    """
    try:
        # Validate query
        if not req.query or not req.query.strip():
            raise HTTPException(
                status_code=400,
                detail="Query cannot be empty"
            )

        query = req.query.strip()
        depth = req.depth

        # Detect mode based on query content
        if " vs " in query.lower():
            # COMPARE MODE
            # Split query by " vs " (case insensitive)
            parts = query.lower().split(" vs ")

            if len(parts) != 2:
                raise HTTPException(
                    status_code=400,
                    detail="Invalid comparison query. Use format: 'item1 vs item2'"
                )

            item_a = parts[0].strip()
            item_b = parts[1].strip()

            # Validate items
            if not item_a or not item_b:
                raise HTTPException(
                    status_code=400,
                    detail="Both items must be non-empty for comparison"
                )

            # Call orchestrator in compare mode
            result = orc.run(
                mode="compare",
                item_a=item_a,
                item_b=item_b,
                depth=depth
            )

        else:
            # OVERVIEW MODE
            topic = query

            # Call orchestrator in overview mode
            result = orc.run(
                mode="overview",
                topic=topic,
                depth=depth
            )

        # Check for errors in result
        if "error" in result:
            raise HTTPException(
                status_code=400,
                detail=f"Custom research failed at {result.get('stage', 'unknown')} stage: {result['error']}"
            )

        return result

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Custom research failed: {str(e)}"
        )


@app.get("/reports/pdf/{filename}")
async def download_pdf(filename: str):
    """
    Download a PDF report file.

    Serves the PDF file with proper Content-Type and Content-Disposition headers
    for download. Validates that the file exists in the reports directory and
    prevents directory traversal attacks.

    Args:
        filename: Name of the PDF file (e.g., "20251204_123456_overview.pdf")

    Returns:
        FileResponse: PDF file with appropriate headers

    Raises:
        HTTPException: 404 if file not found

    Example:
        curl http://localhost:8000/reports/pdf/20251204_123456_overview.pdf
    """
    # Sanitize filename to prevent directory traversal
    safe_filename = os.path.basename(filename)

    # Construct full file path
    file_path = REPORTS_DIR / safe_filename

    # Check if file exists
    if not file_path.exists() or not file_path.is_file():
        raise HTTPException(
            status_code=404,
            detail="Report not found"
        )

    # Validate it's a PDF file
    if not safe_filename.endswith('.pdf'):
        raise HTTPException(
            status_code=400,
            detail="Invalid file type. Only PDF files are supported."
        )

    # Return file with proper headers
    return FileResponse(
        path=str(file_path),
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={safe_filename}"}
    )


@app.get("/reports/view/{filename}")
async def view_report(filename: str, format: str = Query("json", regex="^(html|json)$")):
    """
    View a Markdown report as HTML or JSON.

    Reads the markdown file from the reports directory, converts it to HTML
    with proper styling and extensions (code blocks, tables, TOC), and returns
    it in the requested format.

    Args:
        filename: Name of the markdown file (e.g., "20251204_123456_overview.md")
        format: Response format - "html" or "json" (default: "json")
               - "json": Returns {"html": str, "title": str}
               - "html": Returns raw HTML content with text/html media type

    Returns:
        Response | dict: HTML Response or JSON dict based on format parameter

    Raises:
        HTTPException: 404 if file not found, 400 if not a markdown file

    Examples:
        # Get JSON response (default)
        curl http://localhost:8000/reports/view/20251204_123456_overview.md

        # Get HTML response
        curl http://localhost:8000/reports/view/20251204_123456_overview.md?format=html
    """
    # Sanitize filename to prevent directory traversal
    safe_filename = os.path.basename(filename)

    # Construct full file path
    file_path = REPORTS_DIR / safe_filename

    # Check if file exists
    if not file_path.exists() or not file_path.is_file():
        raise HTTPException(
            status_code=404,
            detail="Report not found"
        )

    # Validate it's a markdown file
    if not safe_filename.endswith('.md'):
        raise HTTPException(
            status_code=400,
            detail="Invalid file type. Only Markdown files are supported."
        )

    try:
        # Read markdown content
        with open(file_path, 'r', encoding='utf-8') as f:
            markdown_content = f.read()

        # Convert markdown to HTML using helper function
        wrapped_html = convert_markdown_to_html(markdown_content, title=safe_filename)

        # Return based on requested format
        if format == "html":
            return Response(content=wrapped_html, media_type="text/html")
        else:
            # Default: JSON format
            return {
                "html": wrapped_html,
                "title": safe_filename
            }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process markdown file: {str(e)}"
        )
