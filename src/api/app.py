"""
FastAPI application for the AI Research Automation Agent.

This module provides REST API endpoints for interacting with
the multi-agent research system.
"""

from typing import Any

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from src.core.orchestrator import Orchestrator


app = FastAPI(
    title="AI Research Automation Agent",
    description="Multi-agent system for automated research and analysis",
    version="1.0.0"
)


# Initialize orchestrator (singleton)
orchestrator = Orchestrator()


# Request Models
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


# Health Check Endpoint
@app.get("/health")
async def health_check() -> dict[str, str]:
    """
    Health check endpoint.

    Returns a simple status message to verify the API is running.

    Returns:
        dict: Status information with "ok" value

    Example:
        GET /health
        Response: {"status": "ok"}
    """
    return {"status": "ok"}


# Research Endpoints
@app.post("/research/overview")
async def research_overview(request: OverviewRequest) -> dict[str, Any]:
    """
    Perform overview research on a single topic.

    This endpoint executes the full research pipeline for a single topic:
    1. Planning - Generate research plan
    2. Search - Gather information via Tavily API
    3. Analysis - Analyze results with Gemini LLM
    4. Report - Generate markdown report

    Args:
        request: OverviewRequest containing:
               - topic: The research topic
               - depth: Analysis depth ("short", "medium", "deep")

    Returns:
        dict: Research results containing:
            On success:
            - status: "completed"
            - mode: "overview"
            - topic: The researched topic
            - depth: Analysis depth used
            - steps: List of plan steps
            - report_path: Path to generated report

            On failure:
            - error: Error message
            - stage: Which stage failed

    Raises:
        HTTPException: 400 for validation errors, 500 for pipeline failures

    Example:
        POST /research/overview
        Body: {
            "topic": "Quantum Computing",
            "depth": "medium"
        }

        Response: {
            "status": "completed",
            "mode": "overview",
            "topic": "Quantum Computing",
            "depth": "medium",
            "steps": [...],
            "report_path": "reports/20231203_123456_overview.md"
        }
    """
    try:
        result = orchestrator.run(
            mode="overview",
            topic=request.topic,
            depth=request.depth
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Research pipeline failed: {str(e)}"
        )


@app.post("/research/compare")
async def research_compare(request: CompareRequest) -> dict[str, Any]:
    """
    Perform comparative research between two items.

    This endpoint executes the full research pipeline for comparing two items:
    1. Planning - Generate comparative research plan
    2. Search - Gather information for both items via Tavily API
    3. Analysis - Compare and analyze with Gemini LLM
    4. Report - Generate comparison markdown report

    Args:
        request: CompareRequest containing:
               - item_a: First item to compare
               - item_b: Second item to compare
               - depth: Analysis depth ("short", "medium", "deep")

    Returns:
        dict: Comparison results containing:
            On success:
            - status: "completed"
            - mode: "compare"
            - item_a: First compared item
            - item_b: Second compared item
            - depth: Analysis depth used
            - steps: List of plan steps
            - report_path: Path to generated report

            On failure:
            - error: Error message
            - stage: Which stage failed

    Raises:
        HTTPException: 400 for validation errors, 500 for pipeline failures

    Example:
        POST /research/compare
        Body: {
            "item_a": "Python",
            "item_b": "JavaScript",
            "depth": "short"
        }

        Response: {
            "status": "completed",
            "mode": "compare",
            "item_a": "Python",
            "item_b": "JavaScript",
            "depth": "short",
            "steps": [...],
            "report_path": "reports/20231203_123456_compare.md"
        }
    """
    try:
        result = orchestrator.run(
            mode="compare",
            item_a=request.item_a,
            item_b=request.item_b,
            depth=request.depth
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Comparison pipeline failed: {str(e)}"
        )


@app.post("/research/custom")
async def research_custom(request: CustomRequest) -> dict[str, Any]:
    """
    Perform custom research with automatic mode detection.

    This endpoint intelligently determines whether to perform overview
    or comparative research based on the query content:
    - If query contains " vs " → comparative research
    - Otherwise → overview research

    For comparative queries, automatically extracts the two items to compare.

    Args:
        request: CustomRequest containing:
               - query: Natural language research query
               - depth: Analysis depth ("short", "medium", "deep")

    Returns:
        dict: Research results (same structure as overview/compare endpoints)

    Raises:
        HTTPException: 400 for invalid queries, 500 for pipeline failures

    Example:
        POST /research/custom
        Body: {
            "query": "sql vs nosql",
            "depth": "medium"
        }

        Response: {
            "status": "completed",
            "mode": "compare",
            "item_a": "sql",
            "item_b": "nosql",
            "depth": "medium",
            "steps": [...],
            "report_path": "reports/20231203_123456_compare.md"
        }

        POST /research/custom
        Body: {
            "query": "machine learning applications",
            "depth": "short"
        }

        Response: {
            "status": "completed",
            "mode": "overview",
            "topic": "machine learning applications",
            "depth": "short",
            "steps": [...],
            "report_path": "reports/20231203_123456_overview.md"
        }
    """
    try:
        query = request.query.strip()
        depth = request.depth

        # Detect mode based on query content
        if " vs " in query.lower():
            # Comparative research mode
            mode = "compare"

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

            # Run comparison research
            result = orchestrator.run(
                mode="compare",
                item_a=item_a,
                item_b=item_b,
                depth=depth
            )
            return result

        else:
            # Overview research mode
            mode = "overview"
            topic = query

            # Validate topic
            if not topic:
                raise HTTPException(
                    status_code=400,
                    detail="Query cannot be empty"
                )

            # Run overview research
            result = orchestrator.run(
                mode="overview",
                topic=topic,
                depth=depth
            )
            return result

    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Custom research pipeline failed: {str(e)}"
        )
