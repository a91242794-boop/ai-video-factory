"""Contract for quality assurance modules."""

from typing import Protocol

from avf.qa_models import QAReport
from avf.registry import Registry
from avf.storyboard_models import Storyboard


class QAContract(Protocol):
    """Evaluate AVF output without prescribing a concrete QA engine."""

    def evaluate(
        self,
        storyboard: Storyboard,
        prompt: str,
        registry: Registry,
    ) -> QAReport:
        """Return a structured QA report for a compiled storyboard."""
        ...
