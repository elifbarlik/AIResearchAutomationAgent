"""
Analysis agent for processing and analyzing search results using LLM.

This agent takes raw search results from web searches and uses
Google Gemini LLM to produce highly structured, source-grounded JSON analysis.

COMPLETELY REWRITTEN VERSION:
- Enforces strict JSON schemas for consistency
- Source-grounded analysis using Tavily search results
- Retry logic for JSON parsing errors
- Depth-aware prompt construction
- Eliminates hallucinations through structured prompts
"""

import json
from typing import Any, Optional

from src.agents.base import Agent, AgentResult


class AnalysisAgent(Agent):
    """
    Agent that analyzes search results using Google Gemini LLM with structured JSON output.

    This version enforces strict JSON schemas and uses highly structured prompts
    to ensure consistent, high-quality output with minimal hallucinations.

    Key improvements:
    - Strict JSON schemas for overview and compare modes
    - Source citations extracted from Tavily results
    - Retry logic for JSON parsing failures
    - Depth-aware prompts (short/detailed)
    - Source-grounded analysis to reduce hallucinations

    Attributes:
        name: The name/identifier of the agent ("analysis")
        llm: GeminiClient instance for LLM calls
        max_retries: Maximum retry attempts for JSON parsing (default: 1)

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
        ...     topic="machine learning",
        ...     depth="short"
        ... )
        >>> print(result.data["summary"])
    """

    def __init__(self, llm_client: Any, max_retries: int = 1) -> None:
        """
        Initialize the AnalysisAgent with an LLM client.

        Args:
            llm_client: GeminiClient instance for making LLM API calls.
                       Must have a generate(prompt: str) -> str method.
            max_retries: Maximum retry attempts for JSON parsing (default: 1)

        Example:
            >>> from src.core.llm_client import GeminiClient
            >>> llm = GeminiClient()
            >>> analyzer = AnalysisAgent(llm_client=llm)
        """
        super().__init__("analysis")
        self.llm = llm_client
        self.max_retries = max_retries

    def run(
        self,
        mode: str,
        search_results: dict,
        topic: Optional[str] = None,
        item_a: Optional[str] = None,
        item_b: Optional[str] = None,
        depth: str = "short",
        **kwargs
    ) -> AgentResult:
        """
        Analyze search results using Gemini LLM to produce structured JSON insights.

        Processes search results from WebSearchAgent and generates
        comprehensive analysis using Google Gemini with strict JSON schemas.

        Args:
            mode: Analysis mode ("overview" or "compare")
            search_results: Raw search results from WebSearchAgent.
                           For overview: {"results": [{"title": ..., "url": ..., "snippet": ...}, ...]}
                           For compare: {"item_a": [...], "item_b": [...]}
            topic: Topic name for overview mode (optional, inferred if not provided)
            item_a: First item name for compare mode (optional, inferred if not provided)
            item_b: Second item name for compare mode (optional, inferred if not provided)
            depth: Analysis depth ("short", "detailed")
                  - "short": Concise summaries and focused insights
                  - "detailed": Long-form comprehensive analysis
            **kwargs: Additional parameters for future use

        Returns:
            AgentResult: Contains success status and analysis data.

                        For overview mode:
                        {
                            "summary": str,
                            "key_points": [str, str, str],
                            "pros": [str, str],
                            "cons": [str, str],
                            "sources": [{"title": str, "url": str}, ...]
                        }

                        For compare mode:
                        {
                            "overview": str,
                            "comparison": {
                                "item_a": {
                                    "summary": str,
                                    "strengths": [str, ...],
                                    "weaknesses": [str, ...]
                                },
                                "item_b": {
                                    "summary": str,
                                    "strengths": [str, ...],
                                    "weaknesses": [str, ...]
                                }
                            },
                            "key_differences": [str, str],
                            "use_case_recommendations": [str, str],
                            "sources": [{"title": str, "url": str}, ...]
                        }

        Example:
            >>> analyzer = AnalysisAgent(llm_client=gemini_client)
            >>> search_data = {"results": [{"title": "AI Guide", "url": "...", "snippet": "..."}]}
            >>> result = analyzer.run(
            ...     mode="overview",
            ...     search_results=search_data,
            ...     topic="artificial intelligence",
            ...     depth="detailed"
            ... )
            >>> if result.success:
            ...     print(result.data["summary"])
            ...     print(result.data["sources"])
        """
        if mode == "overview":
            return self._analyze_overview(search_results, topic, depth)
        elif mode == "compare":
            return self._analyze_compare(search_results, item_a, item_b, depth)
        else:
            return AgentResult(
                success=False,
                error=f"Invalid mode '{mode}' for AnalysisAgent. Use 'overview' or 'compare'."
            )

    def _analyze_overview(
        self,
        search_results: dict,
        topic: Optional[str],
        depth: str
    ) -> AgentResult:
        """
        Perform overview analysis using Gemini LLM with strict JSON schema.

        Args:
            search_results: Search results with "results" key
            topic: Topic name (inferred if None)
            depth: Analysis depth ("short" or "detailed")

        Returns:
            AgentResult: Success result with analysis data or error
        """
        try:
            results = search_results.get("results", [])

            if not results:
                return AgentResult(
                    success=False,
                    error="No search results provided for overview analysis"
                )

            # Infer topic if not provided
            if not topic:
                topic = self._infer_topic_from_results(results)

            # Extract sources for citation
            sources = self._extract_sources(results)

            # Build structured prompt
            prompt = self._build_overview_prompt(results, topic, depth, sources)

            # Call LLM with retry logic
            analysis_data = self._call_llm_with_retry(prompt, mode="overview")

            # Add sources to output
            analysis_data["sources"] = sources

            return AgentResult(success=True, data=analysis_data)

        except json.JSONDecodeError as e:
            return AgentResult(
                success=False,
                error=f"Failed to parse LLM JSON response after retries: {str(e)}"
            )
        except Exception as e:
            return AgentResult(
                success=False,
                error=f"Overview analysis failed: {str(e)}"
            )

    def _analyze_compare(
        self,
        search_results: dict,
        item_a: Optional[str],
        item_b: Optional[str],
        depth: str
    ) -> AgentResult:
        """
        Perform comparative analysis using Gemini LLM with strict JSON schema.

        Args:
            search_results: Search results with "item_a" and "item_b" keys
            item_a: First item name (inferred if None)
            item_b: Second item name (inferred if None)
            depth: Analysis depth ("short" or "detailed")

        Returns:
            AgentResult: Success result with comparison data or error
        """
        try:
            results_a = search_results.get("item_a", [])
            results_b = search_results.get("item_b", [])

            if not results_a or not results_b:
                return AgentResult(
                    success=False,
                    error="Incomplete search results for comparison analysis"
                )

            # Infer item names if not provided
            if not item_a:
                item_a = self._infer_topic_from_results(results_a)
            if not item_b:
                item_b = self._infer_topic_from_results(results_b)

            # Extract sources for citation
            sources_a = self._extract_sources(results_a)
            sources_b = self._extract_sources(results_b)
            all_sources = sources_a + sources_b

            # Build structured comparison prompt
            prompt = self._build_compare_prompt(
                results_a, results_b, item_a, item_b, depth, all_sources
            )

            # Call LLM with retry logic
            comparison_data = self._call_llm_with_retry(prompt, mode="compare")

            # Add sources to output
            comparison_data["sources"] = all_sources

            return AgentResult(success=True, data=comparison_data)

        except json.JSONDecodeError as e:
            return AgentResult(
                success=False,
                error=f"Failed to parse LLM JSON response after retries: {str(e)}"
            )
        except Exception as e:
            return AgentResult(
                success=False,
                error=f"Comparison analysis failed: {str(e)}"
            )

    def _build_overview_prompt(
        self,
        results: list,
        topic: str,
        depth: str,
        sources: list
    ) -> str:
        """
        Build highly structured prompt for overview analysis.

        Args:
            results: List of search results
            topic: Topic name
            depth: Analysis depth
            sources: List of source citations

        Returns:
            str: Structured prompt for Gemini
        """
        # Format search results as JSON for source grounding
        results_json = json.dumps(results, indent=2, ensure_ascii=False)

        # Depth-specific instructions
        if depth == "detailed":
            detail_instruction = "Provide comprehensive, long-form analysis with extensive details."
            summary_length = "3-4 detailed paragraphs"
            points_count = "5-7 key points"
            pros_cons_count = "3-4 items each"
        else:  # short
            detail_instruction = "Provide concise, focused analysis."
            summary_length = "2-3 concise paragraphs"
            points_count = "3-4 key points"
            pros_cons_count = "2-3 items each"

        prompt = f"""You are an expert AI research analyst. Your task is to analyze search results and produce a highly structured JSON output.

CRITICAL INSTRUCTIONS:
1. Respond ONLY with valid JSON. No markdown, no prose, no explanations.
2. Do NOT include code blocks, comments, or trailing commas.
3. Base your analysis STRICTLY on the provided search results - do not hallucinate information.
4. Extract insights directly from the source material.
5. {detail_instruction}

TOPIC: {topic}

DEPTH: {depth}

SEARCH RESULTS (Source-Grounded Data):
{results_json}

OUTPUT SCHEMA (You must follow this EXACT structure):
{{
  "summary": "{summary_length} summarizing {topic} based on the search results",
  "key_points": [
    "Key insight 1 from sources",
    "Key insight 2 from sources",
    "Key insight 3 from sources"
    // {points_count} total
  ],
  "pros": [
    "Advantage 1 backed by sources",
    "Advantage 2 backed by sources"
    // {pros_cons_count}
  ],
  "cons": [
    "Limitation 1 backed by sources",
    "Limitation 2 backed by sources"
    // {pros_cons_count}
  ]
}}

VALIDATION CHECKLIST:
✓ Output is valid JSON (no trailing commas)
✓ All fields are present: summary, key_points, pros, cons
✓ key_points is an array of strings
✓ pros is an array of strings
✓ cons is an array of strings
✓ All content is grounded in the provided search results
✓ No markdown formatting or code blocks

OUTPUT (JSON only):"""

        return prompt

    def _build_compare_prompt(
        self,
        results_a: list,
        results_b: list,
        item_a: str,
        item_b: str,
        depth: str,
        all_sources: list
    ) -> str:
        """
        Build highly structured prompt for comparative analysis.

        Args:
            results_a: Search results for item A
            results_b: Search results for item B
            item_a: First item name
            item_b: Second item name
            depth: Analysis depth
            all_sources: Combined source citations

        Returns:
            str: Structured prompt for Gemini
        """
        # Format search results as JSON for source grounding
        results_a_json = json.dumps(results_a, indent=2, ensure_ascii=False)
        results_b_json = json.dumps(results_b, indent=2, ensure_ascii=False)

        # Depth-specific instructions
        if depth == "detailed":
            detail_instruction = "Provide comprehensive, detailed comparative analysis."
            summary_length = "3-4 detailed paragraphs per item"
            list_count = "4-5 items per list"
            differences_count = "5-7 key differences"
            recommendations_count = "4-5 recommendations"
        else:  # short
            detail_instruction = "Provide concise, focused comparative analysis."
            summary_length = "2-3 concise paragraphs per item"
            list_count = "2-3 items per list"
            differences_count = "3-4 key differences"
            recommendations_count = "2-3 recommendations"

        prompt = f"""You are an expert AI comparative research analyst. Your task is to compare two items based on search results and produce a highly structured JSON output.

CRITICAL INSTRUCTIONS:
1. Respond ONLY with valid JSON. No markdown, no prose, no explanations.
2. Do NOT include code blocks, comments, or trailing commas.
3. Base your analysis STRICTLY on the provided search results - do not hallucinate information.
4. Provide objective, balanced comparison grounded in sources.
5. {detail_instruction}

COMPARISON ITEMS:
- Item A: {item_a}
- Item B: {item_b}

DEPTH: {depth}

SEARCH RESULTS FOR {item_a}:
{results_a_json}

SEARCH RESULTS FOR {item_b}:
{results_b_json}

OUTPUT SCHEMA (You must follow this EXACT structure):
{{
  "overview": "2-3 paragraphs providing high-level comparison context between {item_a} and {item_b}",
  "comparison": {{
    "item_a": {{
      "summary": "{summary_length} describing {item_a}",
      "strengths": [
        "Strength 1 of {item_a} from sources",
        "Strength 2 of {item_a} from sources"
        // {list_count} total
      ],
      "weaknesses": [
        "Weakness 1 of {item_a} from sources",
        "Weakness 2 of {item_a} from sources"
        // {list_count} total
      ]
    }},
    "item_b": {{
      "summary": "{summary_length} describing {item_b}",
      "strengths": [
        "Strength 1 of {item_b} from sources",
        "Strength 2 of {item_b} from sources"
        // {list_count} total
      ],
      "weaknesses": [
        "Weakness 1 of {item_b} from sources",
        "Weakness 2 of {item_b} from sources"
        // {list_count} total
      ]
    }}
  }},
  "key_differences": [
    "Major difference 1 between {item_a} and {item_b}",
    "Major difference 2 between {item_a} and {item_b}"
    // {differences_count} total
  ],
  "use_case_recommendations": [
    "Use {item_a} when... (specific scenario)",
    "Use {item_b} when... (specific scenario)"
    // {recommendations_count} total
  ]
}}

VALIDATION CHECKLIST:
✓ Output is valid JSON (no trailing commas)
✓ All fields are present: overview, comparison, key_differences, use_case_recommendations
✓ comparison.item_a and comparison.item_b each have: summary, strengths, weaknesses
✓ All arrays contain strings
✓ All content is grounded in the provided search results
✓ Comparison is objective and balanced
✓ No markdown formatting or code blocks

OUTPUT (JSON only):"""

        return prompt

    def _call_llm_with_retry(self, prompt: str, mode: str) -> dict:
        """
        Call LLM with retry logic for JSON parsing failures.

        Args:
            prompt: The structured prompt
            mode: "overview" or "compare" (for error context)

        Returns:
            dict: Parsed JSON response

        Raises:
            json.JSONDecodeError: If all retry attempts fail
        """
        last_error = None

        for attempt in range(self.max_retries + 1):
            try:
                # Call Gemini LLM
                response = self.llm.generate(prompt)

                # Clean and parse response
                parsed_json = self._parse_json_response(response)

                # Validate schema
                self._validate_response_schema(parsed_json, mode)

                return parsed_json

            except json.JSONDecodeError as e:
                last_error = e
                if attempt < self.max_retries:
                    # Retry with correction prompt
                    correction_prompt = f"""The previous response was invalid JSON. Please fix and respond with ONLY valid JSON.

Error: {str(e)}

Previous response:
{response}

Requirements:
1. Valid JSON only (no markdown, no comments)
2. No trailing commas
3. Follow the exact schema provided earlier

OUTPUT (corrected JSON only):"""
                    prompt = correction_prompt
                else:
                    # Final attempt failed
                    raise last_error

        # Should not reach here, but just in case
        raise last_error

    def _parse_json_response(self, response: str) -> dict:
        """
        Parse and clean JSON response from LLM.

        Args:
            response: Raw LLM response

        Returns:
            dict: Parsed JSON

        Raises:
            json.JSONDecodeError: If parsing fails
        """
        # Clean response
        response = response.strip()

        # Remove markdown code blocks if present
        if response.startswith("```json"):
            response = response[7:]
        elif response.startswith("```"):
            response = response[3:]

        if response.endswith("```"):
            response = response[:-3]

        response = response.strip()

        # Remove any leading/trailing text before/after JSON
        # Find first { and last }
        start_idx = response.find('{')
        end_idx = response.rfind('}')

        if start_idx != -1 and end_idx != -1:
            response = response[start_idx:end_idx + 1]

        # Parse JSON
        return json.loads(response)

    def _validate_response_schema(self, data: dict, mode: str) -> None:
        """
        Validate that the response matches the expected schema.

        Args:
            data: Parsed JSON data
            mode: "overview" or "compare"

        Raises:
            ValueError: If schema validation fails
        """
        if mode == "overview":
            required_fields = ["summary", "key_points", "pros", "cons"]
            for field in required_fields:
                if field not in data:
                    raise ValueError(f"Missing required field: {field}")
                if field != "summary" and not isinstance(data[field], list):
                    raise ValueError(f"Field '{field}' must be a list")

        elif mode == "compare":
            required_fields = ["overview", "comparison", "key_differences", "use_case_recommendations"]
            for field in required_fields:
                if field not in data:
                    raise ValueError(f"Missing required field: {field}")

            # Validate comparison structure
            if "item_a" not in data["comparison"] or "item_b" not in data["comparison"]:
                raise ValueError("comparison must contain 'item_a' and 'item_b'")

            for item in ["item_a", "item_b"]:
                if "summary" not in data["comparison"][item]:
                    raise ValueError(f"comparison.{item} must contain 'summary'")
                if "strengths" not in data["comparison"][item]:
                    raise ValueError(f"comparison.{item} must contain 'strengths'")
                if "weaknesses" not in data["comparison"][item]:
                    raise ValueError(f"comparison.{item} must contain 'weaknesses'")

    def _extract_sources(self, results: list) -> list:
        """
        Extract source citations from search results.

        Args:
            results: List of search results with title and url

        Returns:
            list: List of source dicts with title and url
        """
        sources = []
        for result in results:
            title = result.get("title", "Untitled")
            url = result.get("url", "")
            if url:  # Only include if URL exists
                sources.append({
                    "title": title,
                    "url": url
                })
        return sources

    def _infer_topic_from_results(self, results: list) -> str:
        """
        Infer topic name from search results.

        Args:
            results: List of search results

        Returns:
            str: Inferred topic name
        """
        if not results or len(results) == 0:
            return "Unknown Topic"

        first_result = results[0]
        title = first_result.get("title", "Unknown Topic")

        # Clean up title to extract topic
        title = title.replace("Introduction to", "").strip()
        title = title.replace("What is", "").strip()
        title = title.replace("?", "").strip()

        if ":" in title:
            title = title.split(":")[0].strip()

        return title if title else "Unknown Topic"
