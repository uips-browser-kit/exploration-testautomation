import pytest

from exploration_ta.url_builder import build_detail_url


def test_build_detail_url_substitutes_id() -> None:
    assert (
        build_detail_url("/lightning/r/Account/{id}/view", "001")
        == "/lightning/r/Account/001/view"
    )


def test_build_detail_url_substitutes_non_id_placeholder() -> None:
    assert build_detail_url("/browse/{issue_key}", "ABC-3") == "/browse/ABC-3"


def test_build_detail_url_raises_on_no_placeholder() -> None:
    with pytest.raises(ValueError, match="no placeholder"):
        build_detail_url("/browse/fixed", "ABC-3")


def test_build_detail_url_raises_on_multiple_placeholders() -> None:
    with pytest.raises(ValueError, match="multiple placeholders"):
        build_detail_url("/wiki/spaces/{space_key}/pages/{page_id}", "98765")
