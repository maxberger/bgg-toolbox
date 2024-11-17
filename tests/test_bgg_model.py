import json
from typing import Generator

import pytest

from bgg import GameCollection, model


@pytest.fixture(scope="session")
def game_collection() -> Generator[GameCollection, None, None]:
    with open("tests/collection.json", "r") as file:
        data = json.load(file)
    yield data


def test_given_sample_collection_when_calling_map_collection_then_all_entries_are_mapped(
    game_collection,
):
    original_count = len(game_collection)
    by_co = model.map_collection(game_collection)
    new_count = len(by_co)
    assert new_count == original_count
