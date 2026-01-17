"""Socratic form engine for requirements gathering.

Uses AskUserQuestion tool to interactively collect user requirements
through structured question flows.

Created: 2026-01-17
Purpose: Interactive requirements gathering for meta-workflows
"""

import logging
from typing import Any

from empathy_os.meta_workflows.models import FormQuestion, FormResponse, FormSchema

logger = logging.getLogger(__name__)


class SocraticFormEngine:
    """Engine for collecting user requirements through Socratic questioning.

    Uses the AskUserQuestion tool to present forms to users and
    collect structured responses.
    """

    def __init__(self):
        """Initialize the Socratic form engine."""
        self.responses_cache: dict[str, FormResponse] = {}

    def ask_questions(
        self, form_schema: FormSchema, template_id: str
    ) -> FormResponse:
        """Ask all questions in the form schema and collect responses.

        Args:
            form_schema: Schema defining questions to ask
            template_id: ID of template these questions are for

        Returns:
            FormResponse with user's answers

        Raises:
            ValueError: If form_schema is invalid
        """
        if not form_schema.questions:
            logger.warning(f"Form schema for {template_id} has no questions")
            return FormResponse(template_id=template_id, responses={})

        # Batch questions (AskUserQuestion supports max 4 at once)
        batches = form_schema.get_question_batches(batch_size=4)
        all_responses = {}

        logger.info(
            f"Asking {len(form_schema.questions)} questions in {len(batches)} batch(es)"
        )

        for batch_idx, batch in enumerate(batches, 1):
            logger.debug(f"Processing batch {batch_idx}/{len(batches)}")

            # Convert batch to AskUserQuestion format
            batch_questions = self._convert_batch_to_ask_user_format(batch)

            # In real usage, this would call AskUserQuestion tool
            # For now, this is a placeholder that tests can mock
            batch_responses = self._ask_batch(batch_questions, template_id)

            # Merge responses
            all_responses.update(batch_responses)

        # Create FormResponse
        response = FormResponse(template_id=template_id, responses=all_responses)

        # Cache response
        self.responses_cache[response.response_id] = response

        logger.info(
            f"Collected {len(all_responses)} responses for template {template_id}"
        )
        return response

    def _convert_batch_to_ask_user_format(
        self, batch: list[FormQuestion]
    ) -> list[dict[str, Any]]:
        """Convert a batch of FormQuestions to AskUserQuestion format.

        Args:
            batch: List of FormQuestion objects

        Returns:
            List of question dictionaries compatible with AskUserQuestion
        """
        return [q.to_ask_user_format() for q in batch]

    def _ask_batch(
        self, questions: list[dict[str, Any]], template_id: str
    ) -> dict[str, Any]:
        """Ask a batch of questions using AskUserQuestion tool.

        This is a placeholder method that should be overridden or mocked in tests.
        In real usage, this would invoke the AskUserQuestion tool.

        Args:
            questions: Questions in AskUserQuestion format
            template_id: Template ID for context

        Returns:
            Dictionary mapping question_id → user's answer

        Note:
            This method is designed to be mockable for testing.
            Real implementation would use the AskUserQuestion tool.
        """
        # Placeholder - real implementation would call AskUserQuestion
        # For testing, this gets mocked
        logger.debug(f"_ask_batch called with {len(questions)} questions")

        # In production, this would be:
        # result = self._invoke_ask_user_question(questions)
        # return result

        # For now, return empty dict (tests will mock this)
        return {}

    def get_cached_response(self, response_id: str) -> FormResponse | None:
        """Retrieve a cached response by ID.

        Args:
            response_id: ID of response to retrieve

        Returns:
            FormResponse if found, None otherwise
        """
        return self.responses_cache.get(response_id)

    def clear_cache(self) -> None:
        """Clear the response cache."""
        self.responses_cache.clear()
        logger.debug("Response cache cleared")


# =============================================================================
# Helper functions for converting between formats
# =============================================================================


def convert_ask_user_response_to_form_response(
    ask_user_result: dict[str, Any], template_id: str
) -> FormResponse:
    """Convert AskUserQuestion tool result to FormResponse.

    Args:
        ask_user_result: Result from AskUserQuestion tool
        template_id: Template ID

    Returns:
        FormResponse object

    Example:
        >>> result = {"q1": "Answer 1", "q2": ["Option A", "Option B"]}
        >>> response = convert_ask_user_response_to_form_response(result, "test")
        >>> response.get("q1")
        'Answer 1'
    """
    return FormResponse(template_id=template_id, responses=ask_user_result)


def create_header_from_question(question: FormQuestion) -> str:
    """Create a short header for a question (max 12 chars for AskUserQuestion).

    Args:
        question: FormQuestion to create header for

    Returns:
        Short header string (≤12 chars)

    Example:
        >>> q = FormQuestion(id="has_tests", text="Do you have tests?", type=QuestionType.BOOLEAN)
        >>> create_header_from_question(q)
        'Tests'
    """
    # Extract key words from question text
    text = question.text.lower()

    # Common patterns
    if "test" in text:
        return "Tests"
    elif "coverage" in text:
        return "Coverage"
    elif "version" in text:
        return "Version"
    elif "publish" in text:
        return "Publishing"
    elif "quality" in text:
        return "Quality"
    elif "security" in text:
        return "Security"
    elif "name" in text:
        return "Name"
    elif "changelog" in text:
        return "Changelog"
    elif "git" in text:
        return "Git"

    # Fallback: use question ID (truncated to 12 chars)
    return question.id[:12].title()
