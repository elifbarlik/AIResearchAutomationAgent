"""
Web search agent using Tavily API for real web searches.

This agent performs actual web searches using the Tavily Search API
to gather relevant information for research tasks. Tavily provides
high-quality search results optimized for AI applications.
"""

import requests
from typing import Optional

from src.agents.base import Agent, AgentResult
from src.core.config import get_settings


class WebSearchAgent(Agent):
    """
    Agent that performs real web searches using Tavily API.

    The WebSearchAgent queries the Tavily Search API to find relevant sources
    and information. It supports different search modes including
    single-topic searches and comparative searches.

    Tavily API provides:
    - High-quality search results
    - Cleaned and structured content
    - Fast response times
    - Optimized for AI/LLM applications

    Attributes:
        name: The name/identifier of the agent ("web_search")
        api_key: Tavily API key from configuration
        endpoint: Tavily API endpoint URL

    Example:
        >>> searcher = WebSearchAgent()
        >>> result = searcher.run(mode="overview", topic="AI trends")
        >>> if result.success:
        ...     print(f"Found {len(result.data['results'])} results")
    """

    def __init__(self) -> None:
        """
        Initialize the WebSearchAgent.

        Loads Tavily API key from configuration and sets up the API endpoint.

        Note:
            Requires TAVILY_API_KEY or SEARCH_API_KEY to be set in .env file.
            Get your API key from: https://tavily.com

        Example:
            >>> searcher = WebSearchAgent()
        """
        super().__init__("web_search")
        settings = get_settings()
        self.api_key = settings.search_api_key
        self.endpoint = "https://api.tavily.com/search"

    def run(
        self,
        mode: str,
        topic: Optional[str] = None,
        item_a: Optional[str] = None,
        item_b: Optional[str] = None,
        **kwargs
    ) -> AgentResult:
        """
        Perform web search using Tavily API based on mode and parameters.

        Executes real web searches via Tavily API. For overview mode,
        searches a single topic. For compare mode, searches two items
        independently for comparative analysis.

        Args:
            mode: The search mode ("overview" or "compare")
            topic: The main topic to search (used in overview mode)
            item_a: First item to search (used in compare mode)
            item_b: Second item to search (used in compare mode)
            **kwargs: Additional parameters for future use
                     (e.g., search_depth, max_results, include_domains)

        Returns:
            AgentResult: Contains success status and search results.

                        For overview mode, data structure:
                        {
                            "results": [
                                {"title": str, "url": str, "snippet": str},
                                ...
                            ]
                        }

                        For compare mode, data structure:
                        {
                            "item_a": [
                                {"title": str, "url": str, "snippet": str},
                                ...
                            ],
                            "item_b": [
                                {"title": str, "url": str, "snippet": str},
                                ...
                            ]
                        }

        Example:
            >>> searcher = WebSearchAgent()
            >>> # Overview search
            >>> result = searcher.run(mode="overview", topic="Machine Learning")
            >>> print(result.data["results"][0]["title"])
            >>>
            >>> # Comparative search
            >>> result = searcher.run(mode="compare", item_a="Python", item_b="JavaScript")
            >>> print(len(result.data["item_a"]))
        """
        if mode == "overview":
            # Overview mode: single topic search
            return self._search_overview(topic)
        elif mode == "compare":
            # Compare mode: search for two items
            return self._search_compare(item_a, item_b)
        else:
            # Invalid mode
            return AgentResult(
                success=False,
                error="Invalid mode for WebSearchAgent"
            )

    def _search_overview(self, topic: Optional[str]) -> AgentResult:
        """
        Perform overview search for a single topic using Tavily API.

        Args:
            topic: The topic to search

        Returns:
            AgentResult: Success result with search results or error

        Note:
            Makes a single API call to Tavily with num_results=5
            to get comprehensive results for the topic.
        """
        if not topic:
            return AgentResult(
                success=False,
                error="Topic is required for overview search"
            )

        try:
            # Prepare API request payload
            payload = {
                "api_key": self.api_key,
                "query": topic,
                "num_results": 5
            }

            # Make POST request to Tavily API
            response = requests.post(self.endpoint, json=payload, timeout=30)
            response.raise_for_status()

            # Parse JSON response
            data = response.json()

            # Extract and format results
            results = []
            for item in data.get("results", []):
                results.append({
                    "title": item.get("title", ""),
                    "url": item.get("url", ""),
                    "snippet": item.get("content", item.get("snippet", ""))
                })

            return AgentResult(
                success=True,
                data={"results": results}
            )

        except requests.exceptions.Timeout:
            return AgentResult(
                success=False,
                error="Tavily API request timed out after 30 seconds"
            )
        except requests.exceptions.HTTPError as e:
            return AgentResult(
                success=False,
                error=f"Tavily API HTTP error: {e.response.status_code}"
            )
        except requests.exceptions.RequestException as e:
            return AgentResult(
                success=False,
                error=f"Tavily API request failed: {str(e)}"
            )
        except Exception as e:
            return AgentResult(
                success=False,
                error=f"Search failed: {str(e)}"
            )

    def _search_compare(
        self,
        item_a: Optional[str],
        item_b: Optional[str]
    ) -> AgentResult:
        """
        Perform comparative searches for two items using Tavily API.

        Makes two separate API calls to gather information about both items
        for comparison analysis.

        Args:
            item_a: First item to search
            item_b: Second item to search

        Returns:
            AgentResult: Success result with search results for both items or error

        Note:
            Makes two API calls (one for each item) with num_results=3
            to keep the comparison focused and balanced.
        """
        if not item_a or not item_b:
            return AgentResult(
                success=False,
                error="Both item_a and item_b are required for compare search"
            )

        try:
            # Search for item_a
            payload_a = {
                "api_key": self.api_key,
                "query": item_a,
                "num_results": 3
            }
            response_a = requests.post(self.endpoint, json=payload_a, timeout=30)
            response_a.raise_for_status()
            data_a = response_a.json()

            # Search for item_b
            payload_b = {
                "api_key": self.api_key,
                "query": item_b,
                "num_results": 3
            }
            response_b = requests.post(self.endpoint, json=payload_b, timeout=30)
            response_b.raise_for_status()
            data_b = response_b.json()

            # Format results for item_a
            results_a = []
            for item in data_a.get("results", []):
                results_a.append({
                    "title": item.get("title", ""),
                    "url": item.get("url", ""),
                    "snippet": item.get("content", item.get("snippet", ""))
                })

            # Format results for item_b
            results_b = []
            for item in data_b.get("results", []):
                results_b.append({
                    "title": item.get("title", ""),
                    "url": item.get("url", ""),
                    "snippet": item.get("content", item.get("snippet", ""))
                })

            return AgentResult(
                success=True,
                data={
                    "item_a": results_a,
                    "item_b": results_b
                }
            )

        except requests.exceptions.Timeout:
            return AgentResult(
                success=False,
                error="Tavily API request timed out after 30 seconds"
            )
        except requests.exceptions.HTTPError as e:
            return AgentResult(
                success=False,
                error=f"Tavily API HTTP error: {e.response.status_code}"
            )
        except requests.exceptions.RequestException as e:
            return AgentResult(
                success=False,
                error=f"Tavily API request failed: {str(e)}"
            )
        except Exception as e:
            return AgentResult(
                success=False,
                error=f"Comparative search failed: {str(e)}"
            )
