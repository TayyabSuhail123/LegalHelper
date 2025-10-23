"""
Base agent classes for legal document analysis agents.
"""

import json
import logging
import os
from abc import ABC, abstractmethod
from typing import Any

import aiofiles
import openai

from app.core.config import settings
from app.core.graph_state import DocumentAnalysisState
from app.services.file_processing import FileProcessingService

logger = logging.getLogger(__name__)


class BaseAnalysisAgent(ABC):
    """
    Abstract base class for all legal document analysis agents.

    Provides common functionality:
    - OpenAI client management
    - Prompt loading (async)
    - Error handling patterns
    - State validation and updates
    - LLM interaction with standardized error handling
    - JSON response parsing
    """

    def __init__(self, file_service: FileProcessingService | None = None):
        self.file_service = file_service
        self.agent_name = self.__class__.__name__
        self.prompt_file = self._get_prompt_file()
        self._openai_client = None

    def _get_prompt_file(self) -> str:
        """Get the prompt file path for this agent."""
        # Convert class name to snake_case and add .prompt extension
        prompt_name = self.agent_name.replace("Agent", "")
        # Convert CamelCase to snake_case
        import re

        prompt_name = re.sub("([a-z0-9])([A-Z])", r"\1_\2", prompt_name).lower()

        agents_dir = os.path.dirname(__file__)
        return os.path.join(agents_dir, "prompts", f"{prompt_name}.prompt")

    @property
    def openai_client(self):
        """Lazy-loaded OpenAI client."""
        if self._openai_client is None:
            self._openai_client = openai.AsyncOpenAI(api_key=settings.openai_api_key)
        return self._openai_client

    async def _load_prompt(self) -> str:
        """Load the prompt template from the agent's prompt file asynchronously."""
        try:
            async with aiofiles.open(self.prompt_file, encoding="utf-8") as f:
                content = await f.read()
                return content.strip()
        except FileNotFoundError:
            logger.warning(f"Prompt file not found: {self.prompt_file}, using default")
            return self._get_default_prompt()
        except Exception as e:
            logger.error(f"Error loading prompt from {self.prompt_file}: {e}")
            return self._get_default_prompt()

    @abstractmethod
    def _get_default_prompt(self) -> str:
        """Get a default prompt if the prompt file is not found."""
        pass

    @abstractmethod
    async def analyze(self, state: DocumentAnalysisState) -> DocumentAnalysisState:
        """
        Perform the agent's specific analysis on the document.

        Args:
            state: Current document analysis state

        Returns:
            Updated state with agent's analysis results
        """
        pass

    @abstractmethod
    def _update_state_with_results(
        self, state: DocumentAnalysisState, results: dict[str, Any]
    ) -> DocumentAnalysisState:
        """
        Update state with agent-specific analysis results.
        Each agent implements this to update their specific fields.

        Args:
            state: Current state
            results: Parsed JSON results from LLM

        Returns:
            Updated state
        """
        pass

    @abstractmethod
    def _get_fallback_results(self, document_text: str) -> dict[str, Any]:
        """
        Provide fallback analysis when LLM fails.
        Each agent implements basic rule-based analysis.

        Args:
            document_text: The document text to analyze

        Returns:
            Basic analysis results
        """
        pass

    def _validate_document_text(self, state: DocumentAnalysisState) -> bool:
        """Validate that document text is available."""
        return bool(state.get("extracted_text"))

    def _update_state_with_error(
        self, state: DocumentAnalysisState, error_msg: str, step_name: str
    ) -> DocumentAnalysisState:
        """Update state with error information."""
        state["error_message"] = f"{self.agent_name}: {error_msg}"
        state["failed_step"] = step_name
        logger.error(f"{self.agent_name} failed: {error_msg}")
        return state

    def _truncate_text_for_llm(self, text: str, max_chars: int = 8000) -> str:
        """Truncate text to fit within token limits."""
        if len(text) <= max_chars:
            return text

        # Try to truncate at sentence boundaries
        truncated = text[:max_chars]
        last_period = truncated.rfind(".")
        last_newline = truncated.rfind("\n")

        # Use the last sentence or paragraph boundary
        if last_period > max_chars * 0.8:
            return truncated[: last_period + 1]
        elif last_newline > max_chars * 0.8:
            return truncated[:last_newline]
        else:
            return truncated + "..."

    async def _call_llm(self, prompt: str, document_text: str) -> str:
        """Call OpenAI LLM with standardized error handling."""
        try:
            # Truncate text to avoid token limits
            truncated_text = self._truncate_text_for_llm(document_text, max_chars=6000)

            messages = [
                {"role": "user", "content": f"{prompt}\n\nDocument content:\n{truncated_text}"}
            ]

            logger.debug(f"{self.agent_name}: Calling OpenAI with model: {settings.openai_model}")
            response = await self.openai_client.chat.completions.create(
                model=settings.openai_model,
                messages=messages,
                max_tokens=settings.openai_max_tokens,
                temperature=settings.openai_temperature,
            )

            return response.choices[0].message.content

        except Exception as e:
            logger.error(f"{self.agent_name}: LLM call failed: {e}")
            raise

    async def _parse_llm_response(self, response: str) -> dict[str, Any]:
        """Parse LLM JSON response with error handling."""
        try:
            return json.loads(response)
        except json.JSONDecodeError as e:
            logger.warning(f"{self.agent_name}: Failed to parse LLM response as JSON: {e}")
            # Try to extract JSON from response if it's wrapped in text
            import re

            json_match = re.search(r"\{.*\}", response, re.DOTALL)
            if json_match:
                try:
                    return json.loads(json_match.group())
                except json.JSONDecodeError:
                    pass
            raise

    async def _analyze_with_llm(
        self, state: DocumentAnalysisState, step_name: str, progress: float
    ) -> DocumentAnalysisState:
        """
        Common analysis pattern used by all agents.
        Handles validation, LLM calling, response parsing, and fallback.
        """
        try:
            logger.info(f"{self.agent_name}: Starting analysis for file {state['file_id']}")

            state["current_step"] = f"Running {step_name}"
            state["progress_percentage"] = progress

            # Validate document text
            if not self._validate_document_text(state):
                return self._update_state_with_error(
                    state, f"No document text available for {step_name}", step_name
                )

            document_text = state["extracted_text"]

            # Load prompt and call LLM
            prompt = await self._load_prompt()
            llm_response = await self._call_llm(prompt, document_text)

            if llm_response:
                try:
                    # Parse JSON response
                    results = await self._parse_llm_response(llm_response)

                    # Update state with agent-specific results
                    state = self._update_state_with_results(state, results)

                    logger.info(
                        f"{self.agent_name}: LLM analysis completed for file {state['file_id']}"
                    )

                except (json.JSONDecodeError, KeyError, ValueError) as e:
                    logger.warning(
                        f"{self.agent_name}: Failed to parse LLM response, using fallback: {e}"
                    )
                    fallback_results = self._get_fallback_results(document_text)
                    state = self._update_state_with_results(state, fallback_results)
            else:
                logger.warning(f"{self.agent_name}: No LLM response, using fallback analysis")
                fallback_results = self._get_fallback_results(document_text)
                state = self._update_state_with_results(state, fallback_results)

            return state

        except Exception as e:
            logger.error(f"{self.agent_name}: Analysis failed: {str(e)}")
            return self._update_state_with_error(state, str(e), step_name)
