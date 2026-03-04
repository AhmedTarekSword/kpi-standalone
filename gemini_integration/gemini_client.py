import json
import logging
import os
from typing import Any, Callable, Dict, List, Tuple

from dotenv import load_dotenv
from google import genai
from google.genai import types

logger = logging.getLogger(__name__)


class GeminiClient:
    """A client to interact with the Google Gemini API."""

    def __init__(self, api_key: str = None, model_name: str = "gemini-2.5-flash"):
        """
        Initialises the Gemini API client.

        Args:
            api_key:    The Gemini API key. Falls back to the 'GEMINI_API_KEY'
                        environment variable if not provided.
            model_name: The Gemini model to use. Defaults to 'gemini-2.5-flash'.
        """
        load_dotenv()
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError(
                "Gemini API key is required. Set the 'GEMINI_API_KEY' environment "
                "variable or pass the key to the constructor."
            )

        self.client = genai.Client(api_key=self.api_key)
        self.model_name = model_name

    # ------------------------------------------------------------------
    # Low-level generation helpers
    # ------------------------------------------------------------------

    def generate_json(self, system_instruction: str, user_prompt: str) -> str:
        """
        Generate a JSON response from Gemini (MIME type forced to application/json).

        Returns:
            The raw response text, which should be valid JSON.
        """
        response = self.client.models.generate_content(
            model=self.model_name,
            contents=user_prompt,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                response_mime_type="application/json"
            )
        )
        return response.text

    def generate_text(self, system_instruction: str, user_prompt: str) -> str:
        """Generate a standard text response from Gemini."""
        response = self.client.models.generate_content(
            model=self.model_name,
            contents=user_prompt,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction
            )
        )
        return response.text

    # ------------------------------------------------------------------
    # Section runner
    # ------------------------------------------------------------------

    def run_section(
        self,
        section_name: str,
        prompt_fn: Callable[
            [Dict[str, Any], List[Dict[str, Any]]],
            Tuple[str, str]
        ],
        kpi_metadata: Dict[str, Any],
        kpi_data_points: List[Dict[str, Any]],
        fallback: Any,
    ) -> Any:
        """
        Build and execute a single report-section API call, with graceful fallback.

        Args:
            section_name:    Human-readable name used in log messages (e.g. "root_causes").
            prompt_fn:       One of the per-section prompt builder functions from prompts.py.
                             Must accept (kpi_metadata, kpi_data_points) and return
                             (system_instruction, user_prompt).
            kpi_metadata:    KPI context dict passed through to the prompt builder.
            kpi_data_points: List of period data points passed through to the prompt builder.
            fallback:        Value returned when the call fails (e.g. {"english": "", "arabic": ""}
                             for text sections, or {"english": [], "arabic": []} for list sections).

        Returns:
            Parsed dict from the Gemini response on success, or `fallback` on any failure.
        """
        try:
            system_instruction, user_prompt = prompt_fn(kpi_metadata, kpi_data_points)
            raw = self.generate_json(system_instruction, user_prompt)
            result = json.loads(raw)
            logger.info("Section '%s' generated successfully.", section_name)
            return result
        except Exception as exc:
            logger.error(
                "Section '%s' failed: %s. Using fallback value.",
                section_name,
                exc,
                exc_info=True,
            )
            return fallback
