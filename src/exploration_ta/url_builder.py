from __future__ import annotations

import re


def build_detail_url(detail_template: str, candidate_id: str) -> str:
    placeholders = re.findall(r"\{([^}]+)\}", detail_template)
    if not placeholders:
        raise ValueError("detail_template contains no placeholder")
    if len(placeholders) > 1:
        raise ValueError(f"detail_template contains multiple placeholders: {placeholders}")
    if not candidate_id:
        raise ValueError("candidate_id must be non-empty")
    return detail_template.replace(f"{{{placeholders[0]}}}", candidate_id)
