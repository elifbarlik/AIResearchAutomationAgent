"""
Base agent class and result types for the multi-agent system.

This module defines the abstract base class that all agents in the system
will inherit from, as well as common data structures for agent results.
All concrete agent implementations (e.g., PlannerAgent, WebSearchAgent,
AnalysisAgent, ReportAgent) must inherit from the Agent class and implement
the required abstract methods.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any


@dataclass
class AgentResult:
    """
    Standard result object returned by all agents.

    This dataclass provides a consistent interface for agent results,
    making it easy to handle success/failure cases and access result data.

    Attributes:
        success: Whether the agent operation completed successfully
        data: Optional dictionary containing result data (e.g., extracted info, analysis results)
        error: Optional error message if the operation failed

    Examples:
        >>> result = AgentResult(success=True, data={"answer": "42"})
        >>> result = AgentResult(success=False, error="API key not found")
    """

    success: bool
    data: dict[str, Any] | None = None
    error: str | None = None


class Agent(ABC):
    """
    Abstract base class for all agents in the multi-agent system.

    All concrete agent implementations must inherit from this class
    and implement the required abstract methods. This ensures a consistent
    interface across all agents in the system.

    Attributes:
        name: The name/identifier of the agent (e.g., "planner", "web_search")

    Example:
        >>> class MyAgent(Agent):
        ...     def run(self, **kwargs) -> AgentResult:
        ...         # Implementation here
        ...         return AgentResult(success=True, data={"result": "done"})
        >>> agent = MyAgent(name="my_agent")
        >>> result = agent.run(query="test")
    """

    def __init__(self, name: str) -> None:
        """
        Initialize the agent with a name.

        Args:
            name: The name/identifier for this agent
        """
        self.name = name

    @abstractmethod
    def run(self, **kwargs) -> AgentResult:
        """
        Execute the agent's main logic.

        This method must be implemented by all concrete agent classes.
        Each agent should define its own specific keyword arguments as needed.

        Args:
            **kwargs: Arbitrary keyword arguments specific to each agent type
                     (e.g., query, context, parameters)

        Returns:
            AgentResult: The result of the agent's execution, containing
                        success status, data, and any error messages

        Raises:
            NotImplementedError: If a subclass does not implement this method
        """
        pass
