import json
import logging
import os
import time
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

    def _execute_with_retry(self, func: Callable, max_retries: int = 3, base_delay: float = 1.0, backoff_factor: float = 2.0) -> Any:
        """Executes a function with an exponential backoff retry sequence."""
        delay = base_delay
        for attempt in range(max_retries + 1):
            try:
                return func()
            except Exception as exc:
                if attempt == max_retries:
                    logger.error("Max retries (%d) reached. Final failure: %s", max_retries, exc)
                    raise
                logger.warning(
                    "Attempt %d failed: %s. Retrying in %.2f seconds...",
                    attempt + 1, exc, delay
                )
                time.sleep(delay)
                delay *= backoff_factor

    def generate_json(self, system_instruction: str, user_prompt: str) -> str:
        """
        Generate a JSON response from Gemini (MIME type forced to application/json).

        Returns:
            The raw response text, which should be valid JSON.
        """
        def _call_api():
            return self.client.models.generate_content(
                model=self.model_name,
                contents=user_prompt,
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    response_mime_type="application/json"
                )
            ).text
        return self._execute_with_retry(_call_api)

    def generate_json_with_search(self, system_instruction: str, user_prompt: str) -> str:
        """
        Generate a JSON response enriched by Google Search grounding via a two-step approach.

        Step 1: Call Gemini with Google Search enabled to obtain a grounded textual analysis.
        Step 2: Call Gemini without search tools but with JSON MIME type, instructing it to
                reformat the grounded text into the required JSON schema.

        This two-step pattern is required because gemini-2.5-flash does not support combining
        google_search tool use with response_mime_type='application/json' in a single call.

        Returns:
            The raw response text from step 2, which should be valid JSON.
        """
        # ── Step 1: grounded plain-text analysis ──────────────────────────────
        def _search_call():
            return self.client.models.generate_content(
                model=self.model_name,
                contents=user_prompt,
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    tools=[types.Tool(google_search=types.GoogleSearch())],
                )
            ).text
        grounded_text = self._execute_with_retry(_search_call)

        # ── Step 2: reformat grounded text into the required JSON schema ──────
        reformat_prompt = (
            f"The following is a grounded analysis produced for a KPI report section.\n"
            f"Your task is to reformat it into valid JSON matching the schema described in the "
            f"original request below, preserving all information and language separation rules.\n\n"
            f"GROUNDED ANALYSIS:\n{grounded_text}\n\n"
            f"ORIGINAL REQUEST (schema and instructions):\n{user_prompt}"
        )

        def _json_format_call():
            return self.client.models.generate_content(
                model=self.model_name,
                contents=reformat_prompt,
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    response_mime_type="application/json",
                )
            ).text
        return self._execute_with_retry(_json_format_call)


    def generate_text(self, system_instruction: str, user_prompt: str) -> str:
        """Generate a standard text response from Gemini."""
        def _call_api():
            return self.client.models.generate_content(
                model=self.model_name,
                contents=user_prompt,
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction
                )
            ).text
        return self._execute_with_retry(_call_api)

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
        use_search: bool = False,
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
            use_search:      If True, Google Search grounding is enabled for this section,
                             allowing the model to draw on broader real-world context.

        Returns:
            Parsed dict from the Gemini response on success, or `fallback` on any failure.
        """
        try:
            system_instruction, user_prompt = prompt_fn(kpi_metadata, kpi_data_points)
            if use_search:
                raw = self.generate_json_with_search(system_instruction, user_prompt)
            else:
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
