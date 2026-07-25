from typing import get_type_hints

from avf.qa import run_static_qa
from avf.qa_models import QAReport


def test_static_qa_declares_structured_report_type():
    assert get_type_hints(run_static_qa)["return"] is QAReport
