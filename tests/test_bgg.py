import json
from typing import Generator

import pytest

from bgg import BGGSession, GameCollection


@pytest.fixture(scope="session")
def game_collection() -> Generator[GameCollection, None, None]:
    with open("tests/collection.json", "r") as file:
        data = json.load(file)
    yield data


@pytest.fixture(autouse=True)
def test_given_sample_collection_when_calling_by_co_then_all_entries_are_mapped(
    game_collection,
):
    original_count = len(game_collection)
    by_co = BGGSession.collection_by_co(game_collection)
    new_count = len(by_co)
    assert new_count == original_count
