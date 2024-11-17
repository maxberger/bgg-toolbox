import json

from bgg import BGGSession


def test_given_sample_collection_when_calling_by_co_then_all_entries_are_mapped():
    with open("tests/collection.json", "r") as file:
        data = json.load(file)
    original_count = len(data)
    by_co = BGGSession.collection_by_co(data)
    new_count = len(by_co)
    assert new_count == original_count
