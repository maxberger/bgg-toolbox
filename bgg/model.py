from typing import Any, Dict, List, Tuple

type GameEntry = Dict[str, Any]

type GameCollection = List[GameEntry]

type GameId = Tuple[str, str]

type MappedGameCollection = Dict[GameId, GameEntry]
