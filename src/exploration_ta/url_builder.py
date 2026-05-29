from __future__ import annotations


def build_detail_url(detail_template: str, candidate_id: str) -> str:
    if "{id}" not in detail_template:
        raise ValueError("detail_template must contain {id}")
    if not candidate_id:
        raise ValueError("candidate_id must be non-empty")
    return detail_template.replace("{id}", candidate_id)
