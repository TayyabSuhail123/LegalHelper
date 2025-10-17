"""
Base agent class for all legal document analysis agents.
"""

import os
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from datetime import datetime, timezone

from langchain.schema import HumanMessage
from langchain_openai import ChatOpenAI

from app.core.graph_state import DocumentAnalysisState, ProcessingStatus
from app.core.file_processing import FileProcessingService
from app.core.config import settings

logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    """
    Base class for all legal document analysis agents.
    
    Each agent specializes in a specific aspect of legal document analysis
    and has its own prompt file for easy customization.
    """
    
    def __init__(self, file_service: Optional[FileProcessingService] = None):
        self.file_service = file_service
        self._llm = None
        self.agent_name = self.__class__.__name__
        self.prompt_file = self._get_prompt_file()
        
    def _get_prompt_file(self) -> str:
        """Get the prompt file path for this agent."""
        # Convert class name to snake_case and add .prompt extension
        prompt_name = self.agent_name.replace('Agent', '')
        # Convert CamelCase to snake_case
        import re
        prompt_name = re.sub('([a-z0-9])([A-Z])', r'\1_\2', prompt_name).lower()
        
        agents_dir = os.path.dirname(__file__)
        return os.path.join(agents_dir, 'prompts', f'{prompt_name}.prompt')
    
    def _get_llm(self) -> Optional[ChatOpenAI]:
        """Get or create LLM instance."""
        if self._llm is None and settings.openai_api_key:
            try:
                self._llm = ChatOpenAI(
                    api_key=settings.openai_api_key,
                    model=settings.openai_model,
                    max_tokens=3000,  # Increased for detailed analysis
                    temperature=0.1   # Low temperature for consistent analysis
                )
            except Exception as e:
                logger.warning(f"Failed to initialize OpenAI client: {e}")
                self._llm = None
        return self._llm
    
    def _load_prompt(self) -> str:
        """Load the prompt template from the agent's prompt file."""
        try:
            with open(self.prompt_file, 'r', encoding='utf-8') as f:
                return f.read().strip()
        except FileNotFoundError:
            logger.error(f"Prompt file not found: {self.prompt_file}")
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
    
    async def _call_llm(self, prompt: str, document_text: str) -> Optional[str]:
        """
        Call the LLM with the given prompt and document text.
        
        Args:
            prompt: The prompt template to use
            document_text: The document text to analyze
            
        Returns:
            LLM response or None if failed
        """
        llm = self._get_llm()
        if not llm:
            logger.warning(f"{self.agent_name}: No LLM available, skipping AI analysis")
            return None
            
        try:
            # Format the prompt with document text
            formatted_prompt = prompt.format(
                document_text=document_text,
                timestamp=datetime.now(timezone.utc).isoformat()
            )
            
            response = await llm.ainvoke([HumanMessage(content=formatted_prompt)])
            return response.content.strip()
            
        except Exception as e:
            logger.error(f"{self.agent_name}: LLM call failed: {e}")
            return None
    
    def _update_state_with_error(self, state: DocumentAnalysisState, error_msg: str, step_name: str) -> DocumentAnalysisState:
        """Update state with error information."""
        state["error_message"] = f"{self.agent_name}: {error_msg}"
        state["failed_step"] = step_name
        logger.error(f"{self.agent_name} failed: {error_msg}")
        return state
    
    def _validate_document_text(self, state: DocumentAnalysisState) -> bool:
        """Validate that document text is available for analysis."""
        if not state.get("extracted_text"):
            logger.warning(f"{self.agent_name}: No extracted text available")
            return False
        return True
