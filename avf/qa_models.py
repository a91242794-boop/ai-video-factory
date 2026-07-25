from typing import TypedDict


QAReport = TypedDict(
    "QAReport",
    {
        "score": int,
        "pass": bool,
        "issues": list[str],
        "checks": dict[str, bool],
        "model_tokens_used": int,
    },
)
