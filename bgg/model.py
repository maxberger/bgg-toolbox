from typing import Any, Dict, List, Tuple

type GameEntry = Dict[str, Any]

type GameCollection = List[GameEntry]

type GameId = Tuple[str, str]

type MappedGameCollection = Dict[GameId, GameEntry]


def map_collection(collection: GameCollection) -> MappedGameCollection:
    return {
        (item.get("@collid", ""), item.get("@objectid", "")): item
        for item in collection
    }
