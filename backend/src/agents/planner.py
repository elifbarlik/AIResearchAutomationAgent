"""
Planner agent for creating research plans.

This agent is responsible for analyzing research queries and
creating structured plans for the research automation workflow.
Different planning modes provide varying levels of detail and depth.
"""

from src.agents.base import Agent, AgentResult


class PlannerAgent(Agent):
    def __init__(self):
        super().__init__("planner")
    """
    Agent that creates structured research plans.

    The PlannerAgent analyzes research requirements and generates
    a step-by-step plan for conducting the research. It supports
    different planning modes for varying levels of detail and
    complexity.

    Attributes:
        name: The name/identifier of the agent

    Example:
        >>> planner = PlannerAgent(name="planner")
        >>> result = planner.run(mode="overview")
        >>> if result.success:
        ...     print(f"Steps: {result.data['steps']}")
    """

    def run(self, mode: str = "overview", **kwargs) -> AgentResult:
        """
        Generate a research plan based on the specified mode.

        Creates a structured list of steps for conducting research,
        tailored to the specified planning mode. The plan provides
        a roadmap for the research automation workflow.

        Args:
            mode: The planning mode that determines depth and approach.
                  Supported modes:
                  - "overview": High-level research plan (5 steps)
                  - "detailed": Comprehensive step-by-step plan (8 steps)
                  - "compare": Comparative analysis plan (7 steps)
                  - "deep": In-depth research plan (8 steps)
            **kwargs: Additional parameters (e.g., query, context, constraints)

        Returns:
            AgentResult: Contains success status and plan data.
                        On success, data includes:
                        - "steps": List of plan steps
                        - "mode": The mode used
                        - "total_steps": Number of steps in the plan

        Example:
            >>> planner = PlannerAgent(name="planner")
            >>> result = planner.run(mode="detailed", query="AI trends")
            >>> print(result.data["total_steps"])
            8
        """
        try:
            # Generate plan steps based on mode
            steps = self._generate_plan_steps(mode)

            return AgentResult(
                success=True,
                data={
                    "steps": steps,
                    "mode": mode,
                    "total_steps": len(steps)
                }
            )
        except Exception as e:
            return AgentResult(
                success=False,
                error=f"Planning failed: {str(e)}"
            )

    def _generate_plan_steps(self, mode: str) -> list[str]:
        """
        Generate plan steps based on the planning mode.

        This is a template-based implementation that returns predefined
        steps for each mode. In a production system, this would integrate
        with an LLM to generate dynamic, context-aware plans based on
        the specific research query and requirements.

        Args:
            mode: The planning mode (overview, detailed, compare, deep)

        Returns:
            list[str]: Ordered list of plan steps

        Note:
            Unknown modes default to "overview" plan.
        """
        # Define plan templates for different modes
        plans = {
            "overview": [
                "Define research scope and objectives",
                "Identify key topics and keywords",
                "Search for relevant sources",
                "Extract and summarize key information",
                "Compile findings into overview report"
            ],
            "detailed": [
                "Conduct background research on topic",
                "Define specific research questions",
                "Identify primary and secondary sources",
                "Perform systematic literature review",
                "Analyze data and extract insights",
                "Cross-reference findings across sources",
                "Synthesize information into coherent narrative",
                "Generate comprehensive detailed report"
            ],
            "compare": [
                "Identify items/topics to compare",
                "Define comparison criteria and metrics",
                "Research each item independently",
                "Extract comparable data points",
                "Perform side-by-side analysis",
                "Highlight similarities and differences",
                "Generate comparative summary report"
            ],
            "deep": [
                "Define research hypothesis or key questions",
                "Conduct extensive literature review",
                "Identify all relevant sources and datasets",
                "Perform in-depth analysis of each source",
                "Extract detailed insights and patterns",
                "Validate findings across multiple sources",
                "Analyze implications and draw conclusions",
                "Generate comprehensive deep-dive report"
            ]
        }

        # Return plan for the specified mode, or default to overview
        return plans.get(mode, plans["overview"])
