"""
LLM client wrapper for Google Gemini API.

This module provides a simple wrapper around the Google Gemini API
for generating text completions in the research automation system.
"""

import google.generativeai as genai

from src.core.config import get_settings


class GeminiClient:
    """
    Wrapper client for Google Gemini API.

    Provides a simple interface for generating text completions using
    Google's Gemini models. Handles API authentication and model
    configuration automatically.

    The client uses the LLM_API_KEY from configuration, which should be
    set to your Google Gemini API key in the .env file.

    Attributes:
        model_name: Name of the Gemini model to use (default: "gemini-pro")

    Example:
        >>> from src.core.llm_client import GeminiClient
        >>> client = GeminiClient()
        >>> response = client.generate("Explain quantum computing in simple terms")
        >>> print(response)

        >>> # Use a different model
        >>> client = GeminiClient(model_name="gemini-2.5-flash")
        >>> response = client.generate("Write a research summary")
    """

    def __init__(self, model_name: str = "gemini-2.5-flash") -> None:
        """
        Initialize the Gemini client.

        Loads API key from configuration and configures the Gemini API.
        The API key is read from the LLM_API_KEY setting in your .env file.

        Args:
            model_name: Name of the Gemini model to use.
                       Default is "gemini-pro".
                       Other options include:
                       - "gemini-pro": Fast and efficient for text
                       - "gemini-1.5-pro": Enhanced capabilities
                       - "gemini-pro-vision": For multimodal tasks

        Raises:
            ValueError: If API key is not configured

        Note:
            Get your API key from: https://makersuite.google.com/app/apikey
            Set it in .env as: LLM_API_KEY=your_gemini_api_key_here

        Example:
            >>> client = GeminiClient()
            >>> # or with custom model
            >>> client = GeminiClient(model_name="gemini-2.5-flash")
        """
        # Load settings
        settings = get_settings()

        # Configure Gemini API with key from settings
        # LLM_API_KEY in .env should contain your Gemini API key
        genai.configure(api_key=settings.llm_api_key)

        # Store model name
        self.model_name = model_name

    def generate(self, prompt: str) -> str:
        """
        Generate text completion using Gemini model.

        Sends a prompt to the Gemini model and returns the generated
        text response. This is a synchronous call that waits for the
        model to complete generation.

        Args:
            prompt: The text prompt to send to the model.
                   Should be clear and specific for best results.

        Returns:
            str: Generated text response from the model

        Raises:
            Exception: If the API call fails (network error, rate limit, etc.)
            ValueError: If the response is empty or malformed

        Example:
            >>> client = GeminiClient()
            >>>
            >>> # Simple completion
            >>> prompt = "Summarize the key benefits of machine learning"
            >>> response = client.generate(prompt)
            >>> print(response)
            >>>
            >>> # Structured prompt
            >>> prompt = '''
            ... Analyze the following topic: Artificial Intelligence
            ...
            ... Provide:
            ... 1. A brief summary
            ... 2. Three key points
            ... 3. Pros and cons
            ... '''
            >>> response = client.generate(prompt)

        Note:
            - Uses synchronous API calls (blocking)
            - Default model: gemini-pro
            - Rate limits apply based on your API tier
            - For long prompts (>8K tokens), consider using gemini-1.5-pro
            - Temperature and other parameters use model defaults
        """
        # Create model instance
        model = genai.GenerativeModel(self.model_name)

        # Generate content from prompt
        response = model.generate_content(prompt)

        # Extract and return text from response
        return response.text
