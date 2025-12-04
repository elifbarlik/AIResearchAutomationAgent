"""
FastAPI application for the AI Research Automation Agent.

This module provides REST API endpoints for interacting with
the multi-agent research system.
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from starlette.middleware.cors import CORSMiddleware

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
orc = Orchestrator()


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
