"""
Report generation agent for creating professional research reports.

This agent takes structured JSON analysis data and generates polished,
human-readable markdown reports with proper formatting and source citations.

UPDATED VERSION WITH PDF SUPPORT:
- Generates markdown reports
- Automatically generates PDF versions using WeasyPrint
- Returns both markdown and PDF paths
- Professional styling and formatting
"""

import os
from datetime import datetime
from pathlib import Path
from typing import Optional
import markdown

from src.agents.base import Agent, AgentResult
from src.pdf.pdf_generator import PDFGenerator


class ReportAgent(Agent):
    """
    Agent that generates professional markdown and PDF research reports.

    Takes structured JSON from AnalysisAgent and generates polished,
    human-readable reports in both markdown and PDF formats.

    Key features:
    - Handles overview and compare JSON schemas
    - Professional markdown formatting
    - Automatic PDF generation with styled templates
    - Source citations with links
    - Graceful handling of missing fields
    - Automatic reports directory creation
    - Timestamped filenames

    Attributes:
        name: The name/identifier of the agent ("report")
        reports_dir: Directory path for saving reports
        pdf_generator: PDFGenerator instance for PDF creation

    Example:
        >>> reporter = ReportAgent()
        >>> analysis = {
        ...     "summary": "Machine learning overview...",
        ...     "key_points": ["Point 1", "Point 2"],
        ...     "pros": ["Pro 1"],
        ...     "cons": ["Con 1"],
        ...     "sources": [{"title": "Source 1", "url": "https://..."}]
        ... }
        >>> result = reporter.run(mode="overview", analysis_output=analysis)
        >>> print(result.data['report_path'])  # Markdown path
        >>> print(result.data['pdf_path'])     # PDF path
    """

    def __init__(self, reports_dir: str = "reports") -> None:
        """
        Initialize the ReportAgent.

        Args:
            reports_dir: Directory path for saving reports (default: "reports")

        Example:
            >>> reporter = ReportAgent()
            >>> # or custom directory
            >>> reporter = ReportAgent(reports_dir="output/reports")
        """
        super().__init__("report")
        self.reports_dir = reports_dir
        self.pdf_generator = PDFGenerator()

        # Ensure reports directory exists
        Path(self.reports_dir).mkdir(parents=True, exist_ok=True)

    def _convert_markdown_to_html(self, markdown_content: str, title: str = "Report") -> str:
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

    def run(
        self,
        mode: str,
        analysis_output: dict,
        topic: Optional[str] = None,
        item_a: Optional[str] = None,
        item_b: Optional[str] = None,
        **kwargs
    ) -> AgentResult:
        """
        Generate professional markdown and PDF reports from analysis output.

        Creates polished reports in both markdown and PDF formats based on
        the analysis results and saves them to the reports directory.

        Args:
            mode: Report mode ("overview" or "compare")
            analysis_output: Structured JSON from AnalysisAgent
                           For overview: {summary, key_points, pros, cons, sources}
                           For compare: {overview, comparison, key_differences,
                                       use_case_recommendations, sources}
            topic: Topic name for overview reports (optional)
            item_a: First item name for comparison reports (optional)
            item_b: Second item name for comparison reports (optional)
            **kwargs: Additional parameters for future use

        Returns:
            AgentResult: Contains success status and report metadata.
                        On success, data includes:
                        - "report_path": Full path to markdown report
                        - "pdf_path": Full path to PDF report

        Example:
            >>> reporter = ReportAgent()
            >>> result = reporter.run(
            ...     mode="overview",
            ...     analysis_output=analysis_data,
            ...     topic="Machine Learning"
            ... )
            >>> if result.success:
            ...     print(f"Markdown: {result.data['report_path']}")
            ...     print(f"PDF: {result.data['pdf_path']}")
        """
        try:
            # Generate markdown based on mode
            if mode == "overview":
                markdown_text = self._generate_overview_report(analysis_output, topic)
                title = f"Overview Report: {topic or 'Research'}"
            elif mode == "compare":
                markdown_text = self._generate_compare_report(analysis_output, item_a, item_b)
                title = f"Comparison: {item_a or 'Item A'} vs {item_b or 'Item B'}"
            else:
                return AgentResult(
                    success=False,
                    error=f"Invalid mode '{mode}' for ReportAgent. Use 'overview' or 'compare'."
                )

            # Create filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            base_filename = f"{timestamp}_{mode}"

            markdown_path = os.path.join(self.reports_dir, f"{base_filename}.md")
            pdf_path = os.path.join(self.reports_dir, f"{base_filename}.pdf")

            # Save markdown report
            with open(markdown_path, 'w', encoding='utf-8') as f:
                f.write(markdown_text)

            # Generate HTML from markdown
            try:
                report_html = self._convert_markdown_to_html(markdown_text, title=title)
                html_generated = True
            except Exception as html_error:
                # Log HTML error but don't fail the entire operation
                print(f"Warning: HTML generation failed: {str(html_error)}")
                html_generated = False
                report_html = None

            # Generate PDF report
            try:
                self.pdf_generator.generate_pdf(markdown_text, pdf_path)
                pdf_generated = True
            except Exception as pdf_error:
                # Log PDF error but don't fail the entire operation
                print(f"Warning: PDF generation failed: {str(pdf_error)}")
                pdf_generated = False
                pdf_path = None

            # Prepare result data
            result_data = {
                "report_path": markdown_path
            }

            if html_generated and report_html:
                result_data["report_html"] = report_html

            if pdf_generated and pdf_path:
                result_data["pdf_path"] = pdf_path

            return AgentResult(
                success=True,
                data=result_data
            )

        except Exception as e:
            return AgentResult(
                success=False,
                error=f"Failed to generate report: {str(e)}"
            )

    def _generate_overview_report(
        self,
        analysis_output: dict,
        topic: Optional[str] = None
    ) -> str:
        """
        Generate a professional overview report in markdown format.

        Args:
            analysis_output: Analysis data with overview JSON schema
            topic: Topic name (optional, extracted from sources if not provided)

        Returns:
            str: Professional markdown formatted report

        Example:
            >>> reporter = ReportAgent()
            >>> markdown = reporter._generate_overview_report(analysis_data, "AI")
        """
        # Extract data with safe defaults
        summary = analysis_output.get("summary", "No summary available.")
        key_points = analysis_output.get("key_points", [])
        pros = analysis_output.get("pros", [])
        cons = analysis_output.get("cons", [])
        sources = analysis_output.get("sources", [])

        # Infer topic from sources if not provided
        if not topic:
            topic = self._infer_topic_from_sources(sources)

        # Build markdown report
        lines = []

        # Title
        lines.append(f"# Overview Report: {topic}")
        lines.append("")
        lines.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("")
        lines.append("---")
        lines.append("")

        # Summary Section
        lines.append("## Summary")
        lines.append("")
        lines.append(summary)
        lines.append("")
        lines.append("---")
        lines.append("")

        # Key Points Section
        lines.append("## Key Points")
        lines.append("")
        if key_points:
            for point in key_points:
                lines.append(f"- {point}")
        else:
            lines.append("*No key points available.*")
        lines.append("")
        lines.append("---")
        lines.append("")

        # Pros Section
        lines.append("## Pros")
        lines.append("")
        if pros:
            for pro in pros:
                lines.append(f"- {pro}")
        else:
            lines.append("*No advantages identified.*")
        lines.append("")
        lines.append("---")
        lines.append("")

        # Cons Section
        lines.append("## Cons")
        lines.append("")
        if cons:
            for con in cons:
                lines.append(f"- {con}")
        else:
            lines.append("*No limitations identified.*")
        lines.append("")
        lines.append("---")
        lines.append("")

        # Sources Section
        if sources:
            lines.append("## Sources")
            lines.append("")
            for i, source in enumerate(sources, 1):
                title = source.get("title", "Untitled")
                url = source.get("url", "")
                if url:
                    lines.append(f"{i}. [{title}]({url})")
                else:
                    lines.append(f"{i}. {title}")
            lines.append("")
            lines.append("---")
            lines.append("")

        # Footer
        lines.append("*Report generated by AI Research Automation Agent*")
        lines.append("")

        return "\n".join(lines)

    def _generate_compare_report(
        self,
        analysis_output: dict,
        item_a: Optional[str] = None,
        item_b: Optional[str] = None
    ) -> str:
        """
        Generate a professional comparison report in markdown format.

        Args:
            analysis_output: Analysis data with compare JSON schema
            item_a: First item name (optional, extracted from sources if not provided)
            item_b: Second item name (optional, extracted from sources if not provided)

        Returns:
            str: Professional markdown formatted comparison report

        Example:
            >>> reporter = ReportAgent()
            >>> markdown = reporter._generate_compare_report(
            ...     comparison_data, "Python", "JavaScript"
            ... )
        """
        # Extract top-level data
        overview = analysis_output.get("overview", "No overview available.")
        comparison = analysis_output.get("comparison", {})
        key_differences = analysis_output.get("key_differences", [])
        use_case_recommendations = analysis_output.get("use_case_recommendations", [])
        sources = analysis_output.get("sources", [])

        # Extract item-specific data
        item_a_data = comparison.get("item_a", {})
        item_b_data = comparison.get("item_b", {})

        item_a_summary = item_a_data.get("summary", "No summary available.")
        item_a_strengths = item_a_data.get("strengths", [])
        item_a_weaknesses = item_a_data.get("weaknesses", [])

        item_b_summary = item_b_data.get("summary", "No summary available.")
        item_b_strengths = item_b_data.get("strengths", [])
        item_b_weaknesses = item_b_data.get("weaknesses", [])

        # Infer item names from sources if not provided
        if not item_a:
            item_a = "Item A"
        if not item_b:
            item_b = "Item B"

        # Build markdown report
        lines = []

        # Title
        lines.append(f"# Comparison Report: {item_a} vs {item_b}")
        lines.append("")
        lines.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("")
        lines.append("---")
        lines.append("")

        # Overview Section
        lines.append("## Overview")
        lines.append("")
        lines.append(overview)
        lines.append("")
        lines.append("---")
        lines.append("")

        # Side-by-Side Comparison Section
        lines.append("## Side-by-Side Comparison")
        lines.append("")

        # Item A
        lines.append(f"### {item_a}")
        lines.append("")
        lines.append(f"**Summary:** {item_a_summary}")
        lines.append("")

        lines.append("**Strengths:**")
        if item_a_strengths:
            for strength in item_a_strengths:
                lines.append(f"- {strength}")
        else:
            lines.append("- *No strengths identified.*")
        lines.append("")

        lines.append("**Weaknesses:**")
        if item_a_weaknesses:
            for weakness in item_a_weaknesses:
                lines.append(f"- {weakness}")
        else:
            lines.append("- *No weaknesses identified.*")
        lines.append("")

        # Item B
        lines.append(f"### {item_b}")
        lines.append("")
        lines.append(f"**Summary:** {item_b_summary}")
        lines.append("")

        lines.append("**Strengths:**")
        if item_b_strengths:
            for strength in item_b_strengths:
                lines.append(f"- {strength}")
        else:
            lines.append("- *No strengths identified.*")
        lines.append("")

        lines.append("**Weaknesses:**")
        if item_b_weaknesses:
            for weakness in item_b_weaknesses:
                lines.append(f"- {weakness}")
        else:
            lines.append("- *No weaknesses identified.*")
        lines.append("")
        lines.append("---")
        lines.append("")

        # Key Differences Section
        lines.append("## Key Differences")
        lines.append("")
        if key_differences:
            for difference in key_differences:
                lines.append(f"- {difference}")
        else:
            lines.append("*No key differences identified.*")
        lines.append("")
        lines.append("---")
        lines.append("")

        # Use Case Recommendations Section
        lines.append("## Use Case Recommendations")
        lines.append("")
        if use_case_recommendations:
            for recommendation in use_case_recommendations:
                lines.append(f"- {recommendation}")
        else:
            lines.append("*No recommendations available.*")
        lines.append("")
        lines.append("---")
        lines.append("")

        # Sources Section
        if sources:
            lines.append("## Sources")
            lines.append("")
            for i, source in enumerate(sources, 1):
                title = source.get("title", "Untitled")
                url = source.get("url", "")
                if url:
                    lines.append(f"{i}. [{title}]({url})")
                else:
                    lines.append(f"{i}. {title}")
            lines.append("")
            lines.append("---")
            lines.append("")

        # Footer
        lines.append("*Report generated by AI Research Automation Agent*")
        lines.append("")

        return "\n".join(lines)

    def _infer_topic_from_sources(self, sources: list) -> str:
        """
        Infer topic name from sources.

        Args:
            sources: List of source dictionaries

        Returns:
            str: Inferred topic name or default
        """
        if not sources or len(sources) == 0:
            return "Research Topic"

        first_source = sources[0]
        title = first_source.get("title", "Research Topic")

        # Clean up title to extract topic
        title = title.replace("Introduction to", "").strip()
        title = title.replace("What is", "").strip()
        title = title.replace("?", "").strip()

        if ":" in title:
            title = title.split(":")[0].strip()

        # Limit length for title
        if len(title) > 60:
            title = title[:60] + "..."

        return title if title else "Research Topic"
