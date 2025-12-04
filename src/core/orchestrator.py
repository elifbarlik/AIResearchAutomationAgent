"""
Orchestrator for coordinating multi-agent workflows.

This module manages the execution flow between different agents
in the research automation system. The orchestrator is responsible
for calling the appropriate agents in the correct sequence and
passing data between them.
"""

from typing import Any, Optional

from src.agents.planner import PlannerAgent
from src.agents.web_search import WebSearchAgent
from src.agents.analysis import AnalysisAgent
from src.agents.report import ReportAgent
from src.core.llm_client import GeminiClient


class Orchestrator:
    """
    Orchestrates the workflow between multiple agents.

    The Orchestrator coordinates the full multi-agent research pipeline:
    1. Planning - Generate research plan based on mode
    2. Search - Gather information from web searches
    3. Analysis - Analyze and structure findings
    4. Report - Generate formatted markdown report

    Each step feeds data into the next, creating a complete
    research automation workflow. If any step fails, the pipeline
    stops and returns an error indicating which stage failed.

    Attributes:
        planner: PlannerAgent instance for generating research plans
        search_agent: WebSearchAgent instance for web searches
        analysis_agent: AnalysisAgent instance for analyzing results
        report_agent: ReportAgent instance for generating reports

    Example:
        >>> orchestrator = Orchestrator()
        >>> result = orchestrator.run(mode="overview", topic="AI")
        >>> if result["status"] == "completed":
        ...     print(f"Report saved: {result['report_path']}")
    """

    def __init__(self) -> None:
        """
        Initialize the orchestrator with all required agents.

        Creates instances of all agents in the pipeline:
        - PlannerAgent: Generates structured research plans
        - WebSearchAgent: Performs web searches (mock for now)
        - AnalysisAgent: Analyzes search results using Gemini LLM
        - ReportAgent: Generates final markdown reports
        """
        # Initialize LLM client
        self.llm_client = GeminiClient()

        # Initialize agents
        self.planner = PlannerAgent()
        self.search_agent = WebSearchAgent()
        self.analysis_agent = AnalysisAgent(llm_client=self.llm_client)
        self.report_agent = ReportAgent()

    def run(
        self,
        mode: str,
        topic: Optional[str] = None,
        item_a: Optional[str] = None,
        item_b: Optional[str] = None,
        depth: str = "short"
    ) -> dict[str, Any]:
        """
        Execute the full multi-agent research pipeline.

        Orchestrates all agents in sequence to complete a research task:
        1. Planning: Generate research plan based on mode
        2. Search: Gather information via web search
        3. Analysis: Analyze and structure findings
        4. Report: Generate formatted markdown report

        Each step passes its output to the next step. If any step fails,
        the pipeline stops immediately and returns an error with the
        failure stage indicated.

        Args:
            mode: Research mode ("overview" or "compare")
                 - "overview": Single-topic research
                 - "compare": Comparative analysis of two items
            topic: Main research topic (used in overview mode)
            item_a: First item to research (used in compare mode)
            item_b: Second item to research (used in compare mode)
            depth: Analysis depth ("short", "medium", "deep")
                  Controls level of detail in analysis

        Returns:
            dict: Pipeline result containing:

                  On success:
                  {
                      "status": "completed",
                      "mode": str,
                      "topic": str | None,
                      "item_a": str | None,
                      "item_b": str | None,
                      "depth": str,
                      "steps": list,  # Plan steps from PlannerAgent
                      "report_path": str  # Path to generated report
                  }

                  On failure:
                  {
                      "error": str,  # Error message
                      "stage": str   # Which stage failed (planning/search/analysis/report)
                  }

        Example:
            >>> orchestrator = Orchestrator()
            >>>
            >>> # Overview research
            >>> result = orchestrator.run(
            ...     mode="overview",
            ...     topic="Machine Learning",
            ...     depth="medium"
            ... )
            >>> print(result["status"])  # "completed"
            >>> print(result["report_path"])  # "reports/20251203_123456_overview.md"
            >>>
            >>> # Comparative research
            >>> result = orchestrator.run(
            ...     mode="compare",
            ...     item_a="Python",
            ...     item_b="JavaScript",
            ...     depth="short"
            ... )
            >>> print(result["steps"])  # Plan steps
            >>> print(result["report_path"])  # Report location
        """
        # STEP 1: PLANNING
        # Generate research plan based on mode
        planner_result = self.planner.run(mode=mode)
        if not planner_result.success:
            return {
                "error": planner_result.error,
                "stage": "planning"
            }
        steps = planner_result.data["steps"]

        # STEP 2: SEARCH
        # Perform web search based on mode and parameters
        search_result = self.search_agent.run(
            mode=mode,
            topic=topic,
            item_a=item_a,
            item_b=item_b
        )
        if not search_result.success:
            return {
                "error": search_result.error,
                "stage": "search"
            }
        search_results = search_result.data

        # STEP 3: ANALYSIS
        # Analyze search results to extract insights
        analysis_result = self.analysis_agent.run(
            mode=mode,
            search_results=search_results,
            topic=topic,
            item_a=item_a,
            item_b=item_b,
            depth=depth
        )
        if not analysis_result.success:
            return {
                "error": analysis_result.error,
                "stage": "analysis"
            }
        analysis_output = analysis_result.data

        # STEP 4: REPORT
        # Generate formatted markdown report
        report_result = self.report_agent.run(
            mode=mode,
            analysis_output=analysis_output,
            topic=topic,
            item_a=item_a,
            item_b=item_b
        )
        if not report_result.success:
            return {
                "error": report_result.error,
                "stage": "report"
            }
        report_path = report_result.data["report_path"]

        # STEP 5: RETURN FINAL RESPONSE
        # Return comprehensive result with all metadata
        result = {
            "status": "completed",
            "mode": mode,
            "topic": topic,
            "item_a": item_a,
            "item_b": item_b,
            "depth": depth,
            "steps": steps,
            "report_path": report_path
        }

        # Add PDF path if it was generated
        if "pdf_path" in report_result.data:
            result["pdf_path"] = report_result.data["pdf_path"]

        return result
