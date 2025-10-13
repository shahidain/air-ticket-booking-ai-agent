"""
OpenAI API Client wrapper for LLM interactions.

This client provides:
1. Structured output generation
2. Chat completions with retry logic
3. Token management
"""

from openai import OpenAI, OpenAIError
from typing import Optional, Type, TypeVar, List, Dict, Any
from pydantic import BaseModel
from config import settings
from utils.logger import setup_logger

logger = setup_logger(__name__)

T = TypeVar('T', bound=BaseModel)


class OpenAIClient:
    """Wrapper for OpenAI API with helper methods."""

    def __init__(self):
        """Initialize OpenAI client with API key from config."""
        try:
            self.client = OpenAI(api_key=settings.openai_api_key)
            self.model = settings.openai_model
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI client: {e}")
            raise

    def generate_structured_output(
        self,
        messages: List[Dict[str, str]],
        response_model: Type[T],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> T:
        """
        Generate structured output using OpenAI with Pydantic model validation.

        Args:
            messages: List of message dictionaries with 'role' and 'content'
            response_model: Pydantic model class for structured output
            temperature: Sampling temperature (0.0 to 2.0)
            max_tokens: Maximum tokens to generate

        Returns:
            Instance of response_model with parsed data

        Raises:
            OpenAIError: If API call fails
        """
        try:
            logger.debug(f"Generating structured output with model: {response_model.__name__}")

            # Use structured outputs (JSON mode)
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                response_format={"type": "json_object"}
            )

            # Parse the JSON response into the Pydantic model
            content = response.choices[0].message.content
            result = response_model.model_validate_json(content)

            logger.debug(f"Successfully generated structured output")
            return result

        except OpenAIError as error:
            logger.error(f"OpenAI API error: {error}")
            raise
        except Exception as e:
            logger.error(f"Error generating structured output: {e}")
            raise

    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        system_prompt: Optional[str] = None
    ) -> str:
        """
        Generate a chat completion.

        Args:
            messages: List of message dictionaries
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            system_prompt: Optional system prompt to prepend

        Returns:
            Generated text response
        """
        try:
            # Prepend system prompt if provided
            if system_prompt:
                messages = [
                    {"role": "system", "content": system_prompt},
                    *messages
                ]

            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )

            content = response.choices[0].message.content
            logger.debug(f"Generated completion: {len(content)} characters")

            return content

        except OpenAIError as error:
            logger.error(f"OpenAI API error: {error}")
            raise
        except Exception as e:
            logger.error(f"Error in chat completion: {e}")
            raise

    def extract_information(
        self,
        text: str,
        extraction_prompt: str,
        response_model: Type[T]
    ) -> T:
        """
        Extract structured information from text using LLM.

        Args:
            text: Input text to extract from
            extraction_prompt: Instructions for extraction
            response_model: Pydantic model for structured output

        Returns:
            Extracted information as response_model instance
        """
        messages = [
            {
                "role": "system",
                "content": extraction_prompt
            },
            {
                "role": "user",
                "content": text
            }
        ]

        return self.generate_structured_output(
            messages=messages,
            response_model=response_model,
            temperature=0.3  # Lower temperature for extraction
        )

    def format_response(
        self,
        data: Any,
        format_instruction: str,
        temperature: float = 0.7
    ) -> str:
        """
        Format data into human-readable text using LLM.

        Args:
            data: Data to format (will be converted to string)
            format_instruction: Instructions for formatting
            temperature: Sampling temperature

        Returns:
            Formatted text
        """
        messages = [
            {
                "role": "system",
                "content": format_instruction
            },
            {
                "role": "user",
                "content": str(data)
            }
        ]

        return self.chat_completion(
            messages=messages,
            temperature=temperature
        )
