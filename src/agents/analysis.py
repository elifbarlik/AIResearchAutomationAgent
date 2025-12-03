"""
Analysis agent for processing and analyzing search results using LLM.

This agent takes raw search results from web searches and uses
Google Gemini LLM to produce structured analysis including summaries,
key points, pros/cons evaluations, and comparison tables.
"""

import json
from typing import Any

from src.agents.base import Agent, AgentResult


class AnalysisAgent(Agent):
    """
    Agent that analyzes search results using Google Gemini LLM.

    The AnalysisAgent processes raw search results from the WebSearchAgent
    and uses a Large Language Model (Gemini) to generate intelligent,
    structured analysis including summaries, key points, pros/cons analysis,
    and comparison tables.

    Unlike the mock version, this implementation:
    - Uses real Gemini API for analysis
    - Generates contextual, relevant insights
    - Produces dynamic analysis based on actual search content
    - Returns structured JSON output

    Attributes:
        name: The name/identifier of the agent ("analysis")
        llm: GeminiClient instance for LLM calls

    Example:
        >>> from src.core.llm_client import GeminiClient
        >>> from src.agents.analysis import AnalysisAgent
        >>>
        >>> llm_client = GeminiClient()
        >>> analyzer = AnalysisAgent(llm_client=llm_client)
        >>> search_data = {"results": [...]}
        >>> result = analyzer.run(
        ...     mode="overview",
        ...     search_results=search_data,
        ...     depth="short"
        ... )
        >>> print(result.data["summary"])
    """

    def __init__(self, llm_client: Any) -> None:
        """
        Initialize the AnalysisAgent with an LLM client.

        Args:
            llm_client: GeminiClient instance for making LLM API calls.
                       Must have a generate(prompt: str) -> str method.

        Example:
            >>> from src.core.llm_client import GeminiClient
            >>> llm = GeminiClient()
            >>> analyzer = AnalysisAgent(llm_client=llm)
        """
        super().__init__("analysis")
        self.llm = llm_client

    def run(
        self,
        mode: str,
        search_results: dict,
        depth: str = "short",
        **kwargs
    ) -> AgentResult:
        """
        Analyze search results using Gemini LLM to produce structured insights.

        Processes search results from WebSearchAgent and generates
        comprehensive analysis using Google Gemini. The output structure
        varies based on the mode (overview vs compare).

        Args:
            mode: Analysis mode ("overview" or "compare")
            search_results: Raw search results from WebSearchAgent.
                           For overview: {"results": [{"title": ..., "snippet": ...}, ...]}
                           For compare: {"item_a": [...], "item_b": [...]}
            depth: Analysis depth ("short", "medium", "deep")
                  Controls level of detail requested from LLM
            **kwargs: Additional parameters for future use

        Returns:
            AgentResult: Contains success status and analysis data.

                        For overview mode:
                        {
                            "summary": str,
                            "key_points": [str, ...],
                            "pros": [str, ...],
                            "cons": [str, ...]
                        }

                        For compare mode:
                        {
                            "item_a_summary": str,
                            "item_b_summary": str,
                            "comparison_points": [
                                {"aspect": str, "item_a": str, "item_b": str},
                                ...
                            ],
                            "pros_cons_table": [
                                {"aspect": str, "pros": str, "cons": str},
                                ...
                            ]
                        }

        Example:
            >>> analyzer = AnalysisAgent(llm_client=gemini_client)
            >>> search_data = {"results": [{"title": "AI Guide", "snippet": "..."}]}
            >>> result = analyzer.run(mode="overview", search_results=search_data, depth="medium")
            >>> if result.success:
            ...     print(result.data["summary"])
        """
        if mode == "overview":
            # Overview analysis for single topic
            return self._analyze_overview(search_results, depth)
        elif mode == "compare":
            # Comparative analysis for two items
            return self._analyze_compare(search_results, depth)
        else:
            # Invalid mode
            return AgentResult(
                success=False,
                error="Invalid mode for AnalysisAgent"
            )

    def _analyze_overview(self, search_results: dict, depth: str) -> AgentResult:
        """
        Perform overview analysis using Gemini LLM.

        Extracts topic from search results, constructs a prompt for Gemini,
        and generates structured analysis.

        Args:
            search_results: Search results with "results" key
            depth: Analysis depth

        Returns:
            AgentResult: Success result with analysis data or error
        """
        try:
            # Extract topic from search results
            topic = "the topic"
            results = search_results.get("results", [])

            if results and len(results) > 0:
                first_result = results[0]
                title = first_result.get("title", "")
                # Try to infer topic from title
                if "Introduction to" in title:
                    topic = title.replace("Introduction to", "").strip()
                elif ":" in title:
                    topic = title.split(":")[0].strip()
                else:
                    topic = title

            # Format sources for prompt
            sources_text = ""
            for i, result in enumerate(results, 1):
                title = result.get("title", "N/A")
                snippet = result.get("snippet", "N/A")
                sources_text += f"{i}. {title}\n   {snippet}\n\n"

            # Build prompt for Gemini
            prompt = f"""You are an expert AI technical researcher.
Your task is to produce an extremely clear, structured research analysis.

Topic: {topic}

Depth: {depth}

Sources:
{sources_text}

Provide output strictly in JSON format with the following structure:
{{
  "summary": "A comprehensive summary of the topic based on the sources",
  "key_points": ["Key insight 1", "Key insight 2", "Key insight 3"],
  "pros": ["Advantage 1", "Advantage 2"],
  "cons": ["Limitation 1", "Limitation 2"]
}}

IMPORTANT: Return ONLY the JSON object, no additional text before or after."""

            # Call Gemini LLM
            response = self.llm.generate(prompt)

            # Parse JSON response
            # Clean response (remove markdown code blocks if present)
            response = response.strip()
            if response.startswith("```json"):
                response = response[7:]
            if response.startswith("```"):
                response = response[3:]
            if response.endswith("```"):
                response = response[:-3]
            response = response.strip()

            # Parse JSON
            analysis_data = json.loads(response)

            return AgentResult(success=True, data=analysis_data)

        except json.JSONDecodeError as e:
            return AgentResult(
                success=False,
                error=f"LLM JSON parsing failed: {str(e)}"
            )
        except Exception as e:
            return AgentResult(
                success=False,
                error=f"Analysis failed: {str(e)}"
            )

    def _analyze_compare(self, search_results: dict, depth: str) -> AgentResult:
        """
        Perform comparative analysis using Gemini LLM.

        Extracts item names from search results, constructs comparison prompt,
        and generates structured comparison.

        Args:
            search_results: Search results with "item_a" and "item_b" keys
            depth: Analysis depth

        Returns:
            AgentResult: Success result with comparison data or error
        """
        try:
            # Extract item_a name and results
            item_a = "Item A"
            item_a_results = search_results.get("item_a", [])

            if item_a_results and len(item_a_results) > 0:
                first_result = item_a_results[0]
                title = first_result.get("title", "")
                if "What is" in title:
                    item_a = title.replace("What is", "").replace("?", "").strip()
                elif ":" in title:
                    item_a = title.split(":")[0].strip()
                else:
                    item_a = title

            # Extract item_b name and results
            item_b = "Item B"
            item_b_results = search_results.get("item_b", [])

            if item_b_results and len(item_b_results) > 0:
                first_result = item_b_results[0]
                title = first_result.get("title", "")
                if "What is" in title:
                    item_b = title.replace("What is", "").replace("?", "").strip()
                elif ":" in title:
                    item_b = title.split(":")[0].strip()
                else:
                    item_b = title

            # Format sources for item_a
            sources_a_text = f"Item A ({item_a}) sources:\n"
            for i, result in enumerate(item_a_results, 1):
                title = result.get("title", "N/A")
                snippet = result.get("snippet", "N/A")
                sources_a_text += f"{i}. {title}\n   {snippet}\n\n"

            # Format sources for item_b
            sources_b_text = f"Item B ({item_b}) sources:\n"
            for i, result in enumerate(item_b_results, 1):
                title = result.get("title", "N/A")
                snippet = result.get("snippet", "N/A")
                sources_b_text += f"{i}. {title}\n   {snippet}\n\n"

            # Build comparison prompt
            prompt = f"""You are an expert AI technical analyst.
Compare the following two technologies in a structured and objective way.

Item A: {item_a}
Item B: {item_b}

Depth: {depth}

Sources:
{sources_a_text}

{sources_b_text}

Provide output strictly in JSON format with the following structure:
{{
  "item_a_summary": "Comprehensive summary of Item A",
  "item_b_summary": "Comprehensive summary of Item B",
  "comparison_points": [
      {{"aspect": "Performance", "item_a": "Item A's performance characteristics", "item_b": "Item B's performance characteristics"}},
      {{"aspect": "Scalability", "item_a": "Item A's scalability", "item_b": "Item B's scalability"}},
      {{"aspect": "Community", "item_a": "Item A's community", "item_b": "Item B's community"}}
  ],
  "pros_cons_table": [
      {{"aspect": "Ease of use", "pros": "Advantages of Item A", "cons": "Advantages of Item B"}},
      {{"aspect": "Performance", "pros": "Performance benefits", "cons": "Performance trade-offs"}}
  ]
}}

IMPORTANT: Return ONLY the JSON object, no additional text before or after."""

            # Call Gemini LLM
            response = self.llm.generate(prompt)

            # Parse JSON response
            # Clean response (remove markdown code blocks if present)
            response = response.strip()
            if response.startswith("```json"):
                response = response[7:]
            if response.startswith("```"):
                response = response[3:]
            if response.endswith("```"):
                response = response[:-3]
            response = response.strip()

            # Parse JSON
            comparison_data = json.loads(response)

            return AgentResult(success=True, data=comparison_data)

        except json.JSONDecodeError as e:
            return AgentResult(
                success=False,
                error=f"LLM JSON parsing failed: {str(e)}"
            )
        except Exception as e:
            return AgentResult(
                success=False,
                error=f"Comparison analysis failed: {str(e)}"
            )
