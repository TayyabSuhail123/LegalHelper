"""
Base agent class for all legal document analysis agents.
"""

import os
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from datetime import datetime, timezone

import openai

from app.core.graph_state import DocumentAnalysisState, ProcessingStatus
from app.services.file_processing import FileProcessingService
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
    
    def _get_openai_client(self):
        """Get OpenAI client.""" 
        if not hasattr(self, 'openai_client'):
            self.openai_client = openai.AsyncOpenAI(api_key=settings.openai_api_key)
            self.config = settings
        return self.openai_client
    
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
    
    def _truncate_text_for_llm(self, text: str, max_chars: int = 8000) -> str:
        """Truncate text to fit within token limits."""
        if len(text) <= max_chars:
            return text
        
        # Try to truncate at sentence boundaries
        truncated = text[:max_chars]
        last_period = truncated.rfind('.')
        last_newline = truncated.rfind('\n')
        
        # Use the last sentence or paragraph boundary
        if last_period > max_chars * 0.8:
            return truncated[:last_period + 1]
        elif last_newline > max_chars * 0.8:
            return truncated[:last_newline]
        else:
            return truncated + "..."

    async def _call_llm(self, prompt: str, document_text: str) -> str:
        """Call OpenAI LLM with error handling.""" 
        try:
            # Initialize OpenAI client if needed
            self._get_openai_client()
            
            # For now, use first 2000 characters to avoid token limits
            truncated_text = document_text[:2000] + "..." if len(document_text) > 2000 else document_text
            
            messages = [
                {
                    "role": "user", 
                    "content": f"{prompt}\n\nDocument content:\n{truncated_text}"
                }
            ]
            
            logger.debug(f"Calling OpenAI with model: {self.config.openai_model}")
            response = await self.openai_client.chat.completions.create(
                model=self.config.openai_model,
                messages=messages,
                max_tokens=self.config.openai_max_tokens,
                temperature=self.config.openai_temperature
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"{self.__class__.__name__}: LLM call failed: {e}")
            raise
    
    def _update_state_with_error(self, state: DocumentAnalysisState, error_msg: str, step_name: str) -> DocumentAnalysisState:
        """Update state with error information."""
        state["error_message"] = f"{self.agent_name}: {error_msg}"
        state["failed_step"] = step_name
        logger.error(f"{self.agent_name} failed: {error_msg}")
        return state
    
    def _validate_document_text(self, state: DocumentAnalysisState) -> bool:
        """Validate that document text is available."""
        if not state.get("extracted_text"):
            return False
        return True
    

