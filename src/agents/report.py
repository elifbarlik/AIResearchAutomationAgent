"""
Report generation agent for creating research reports.

This agent takes analyzed data and generates formatted reports
in markdown format, saved to the reports directory.
"""

import os
from datetime import datetime
from pathlib import Path

from src.agents.base import Agent, AgentResult


class ReportAgent(Agent):
    """
    Agent that generates formatted research reports.

    The ReportAgent takes structured analysis output from the AnalysisAgent
    and generates well-formatted markdown reports. Reports are automatically
    saved to the reports directory with timestamps for easy organization.

    Currently generates simple markdown reports. Future versions will support:
    - PDF export with styling
    - HTML with interactive elements
    - Rich tables and charts
    - Custom templates
    - Multiple output formats (DOCX, LaTeX, etc.)

    Attributes:
        name: The name/identifier of the agent ("report")

    Example:
        >>> reporter = ReportAgent()
        >>> analysis_data = {"summary": "...", "key_points": [...]}
        >>> result = reporter.run(mode="overview", analysis_output=analysis_data)
        >>> print(f"Report saved: {result.data['report_path']}")
    """

    def __init__(self) -> None:
        """
        Initialize the ReportAgent.

        Sets the agent name to "report" for identification
        in the multi-agent system. Also ensures the reports
        directory exists.
        """
        super().__init__("report")

        # Ensure reports directory exists
        Path("reports").mkdir(parents=True, exist_ok=True)

    def run(
        self,
        mode: str,
        analysis_output: dict,
        **kwargs
    ) -> AgentResult:
        """
        Generate a formatted report from analysis output.

        Creates a markdown report based on the analysis results and saves
        it to the reports directory with a timestamp. The report format
        adapts to the mode (overview vs comparative analysis).

        Args:
            mode: Report mode ("overview" or "compare")
            analysis_output: Structured analysis data from AnalysisAgent.
                           For overview: {summary, key_points, pros, cons}
                           For compare: {item_a_summary, item_b_summary,
                                       comparison_points, pros_cons_table}
            **kwargs: Additional parameters for future use
                     (e.g., output_format, template, styling_options)

        Returns:
            AgentResult: Contains success status and report metadata.
                        On success, data includes:
                        - "report_path": Full path to the saved report file

        Note:
            Future enhancements planned:
            - Support for PDF, HTML, DOCX output formats
            - Rich markdown with tables, charts, embedded images
            - Custom templates and corporate branding
            - Export to cloud storage (Google Drive, Dropbox)
            - Integration with collaboration platforms (Notion, Confluence)
            - Version control and report history tracking

        Example:
            >>> reporter = ReportAgent()
            >>> analysis = {
            ...     "summary": "Key findings...",
            ...     "key_points": ["Point 1", "Point 2"],
            ...     "pros": ["Pro 1"],
            ...     "cons": ["Con 1"]
            ... }
            >>> result = reporter.run(mode="overview", analysis_output=analysis)
            >>> if result.success:
            ...     with open(result.data['report_path']) as f:
            ...         print(f.read())
        """
        if mode == "overview":
            # Generate overview report
            markdown = self._generate_overview_report(analysis_output)
        elif mode == "compare":
            # Generate comparison report
            markdown = self._generate_compare_report(analysis_output)
        else:
            # Invalid mode
            return AgentResult(
                success=False,
                error="Invalid mode for ReportAgent"
            )

        try:
            # Create filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"reports/{timestamp}_{mode}.md"

            # Save report to file with UTF-8 encoding
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(markdown)

            return AgentResult(
                success=True,
                data={
                    "report_path": filename
                }
            )
        except Exception as e:
            return AgentResult(
                success=False,
                error=f"Failed to save report: {str(e)}"
            )

    def _generate_overview_report(self, analysis_output: dict) -> str:
        """
        Generate an overview report in markdown format.

        Creates a structured markdown document with sections for
        summary, key points, advantages, and limitations.

        Args:
            analysis_output: Analysis data containing:
                           - summary: Executive summary text
                           - key_points: List of main insights
                           - pros: List of advantages
                           - cons: List of limitations

        Returns:
            str: Markdown formatted report content

        Note:
            Future versions will support:
            - Rich formatting with colors and emphasis
            - Embedded charts and visualizations
            - Citation and source management
            - Automatic table of contents generation
            - Custom section ordering and templates
        """
        summary = analysis_output.get("summary", "No summary available.")
        key_points = analysis_output.get("key_points", [])
        pros = analysis_output.get("pros", [])
        cons = analysis_output.get("cons", [])

        # Build markdown report
        markdown_lines = [
            "# Overview Report",
            "",
            f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "---",
            "",
            "## Summary",
            "",
            summary,
            "",
            "---",
            "",
            "## Key Points",
            ""
        ]

        if key_points:
            for point in key_points:
                markdown_lines.append(f"- {point}")
        else:
            markdown_lines.append("*No key points available.*")

        markdown_lines.extend([
            "",
            "---",
            "",
            "## Pros",
            ""
        ])

        if pros:
            for pro in pros:
                markdown_lines.append(f"- {pro}")
        else:
            markdown_lines.append("*No pros identified.*")

        markdown_lines.extend([
            "",
            "---",
            "",
            "## Cons",
            ""
        ])

        if cons:
            for con in cons:
                markdown_lines.append(f"- {con}")
        else:
            markdown_lines.append("*No cons identified.*")

        markdown_lines.extend([
            "",
            "---",
            "",
            "*Report generated by AI Research Automation Agent*"
        ])

        return "\n".join(markdown_lines)

    def _generate_compare_report(self, analysis_output: dict) -> str:
        """
        Generate a comparative report in markdown format.

        Creates a structured markdown document comparing two items
        with individual summaries, comparison points, and a detailed
        pros/cons analysis.

        Args:
            analysis_output: Analysis data containing:
                           - item_a_summary: Summary of first item
                           - item_b_summary: Summary of second item
                           - comparison_points: List of comparison aspects
                           - pros_cons_table: Structured pros/cons data

        Returns:
            str: Markdown formatted comparison report

        Note:
            Future versions will support:
            - Side-by-side comparison tables
            - Visual comparison charts and graphs
            - Score cards and rating systems
            - Interactive elements for web export
            - Weighted comparison matrices
        """
        item_a_summary = analysis_output.get("item_a_summary", "No summary available.")
        item_b_summary = analysis_output.get("item_b_summary", "No summary available.")
        comparison_points = analysis_output.get("comparison_points", [])
        pros_cons_table = analysis_output.get("pros_cons_table", [])

        # Build markdown report
        markdown_lines = [
            "# Comparison Report",
            "",
            f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "---",
            "",
            "## Item A Summary",
            "",
            item_a_summary,
            "",
            "---",
            "",
            "## Item B Summary",
            "",
            item_b_summary,
            "",
            "---",
            "",
            "## Comparison Points",
            ""
        ]

        if comparison_points:
            for point in comparison_points:
                aspect = point.get("aspect", "Unknown")
                item_a_info = point.get("item_a", "N/A")
                item_b_info = point.get("item_b", "N/A")
                markdown_lines.append(f"- **{aspect}:**")
                markdown_lines.append(f"  - Item A: {item_a_info}")
                markdown_lines.append(f"  - Item B: {item_b_info}")
        else:
            markdown_lines.append("*No comparison points available.*")

        markdown_lines.extend([
            "",
            "---",
            "",
            "## Pros & Cons Table",
            ""
        ])

        if pros_cons_table:
            for row in pros_cons_table:
                aspect = row.get("aspect", "Unknown")
                pros = row.get("pros", "N/A")
                cons = row.get("cons", "N/A")
                markdown_lines.append(f"### {aspect}")
                markdown_lines.append(f"- **Pros:** {pros}")
                markdown_lines.append(f"- **Cons:** {cons}")
                markdown_lines.append("")
        else:
            markdown_lines.append("*No pros/cons table available.*")

        markdown_lines.extend([
            "---",
            "",
            "*Report generated by AI Research Automation Agent*"
        ])

        return "\n".join(markdown_lines)
