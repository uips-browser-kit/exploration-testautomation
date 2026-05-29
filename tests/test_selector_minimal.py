from exploration_ta.selector import Candidate, select_candidate


def test_random_selector_is_seeded_and_reproducible() -> None:
    candidates = [Candidate(id=f"{i:03d}") for i in range(1, 21)]

    r1 = select_candidate(candidates, strategy="random", seed=42)
    r2 = select_candidate(candidates, strategy="random", seed=42)

    assert r1.selected_index == r2.selected_index
    assert r1.candidate.id == r2.candidate.id
