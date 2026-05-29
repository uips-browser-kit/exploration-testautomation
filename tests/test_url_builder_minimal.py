from exploration_ta.url_builder import build_detail_url


def test_build_detail_url_substitutes_id() -> None:
    assert (
        build_detail_url("/lightning/r/Account/{id}/view", "001")
        == "/lightning/r/Account/001/view"
    )
