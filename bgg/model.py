from enum import StrEnum, auto
from typing import Any, Callable, Dict, List, Mapping, Tuple

type GameEntry = Dict[str, Any]

type GameCollection = List[GameEntry]

type GameId = Tuple[str, str]

type MappedGameCollection = Dict[GameId, GameEntry]


class Attribute(StrEnum):
    collid = auto()
    objectid = auto()
    title = auto()

    version_yearpublished = auto()
    version_publishers = auto()

    pricepaid = auto()
    currvalue = auto()
    quantity = auto()
    acquisitiondate = auto()
    acquiredfrom = auto()
    invlocation = auto()
    pp_currency = auto()
    privatecomment = auto()


def _path_extract(path: str) -> Callable[[GameEntry], str]:
    def doit(item: GameEntry) -> str:

        path_entries = path.split("/")
        cur = item
        for i in range(len(path_entries) - 1):
            cur = cur.get(path_entries[i], {})
        return cur.get(path_entries[len(path_entries) - 1], "")

    return doit


def _publishers_extract(game_entry: GameEntry) -> str:
    version = game_entry.get("version", {})
    item = version.get("item", {})
    links = item.get("link", [])
    publishers = [
        link.get("@value")
        for link in links
        if link.get("@type") == "boardgamepublisher"
    ]
    return ", ".join(publishers)


_attribute_paths: Mapping[Attribute, Callable[[GameEntry], str]] = {
    Attribute.collid: _path_extract("@collid"),
    Attribute.objectid: _path_extract("@objectid"),
    Attribute.title: _path_extract("name/#text"),
    Attribute.version_yearpublished: _path_extract("version/item/yearpublished/@value"),
    Attribute.version_publishers: _publishers_extract,
    Attribute.pricepaid: _path_extract("privateinfo/@pricepaid"),
    Attribute.currvalue: _path_extract("privateinfo/@currvalue"),
    Attribute.quantity:  _path_extract("privateinfo/@quantity"),
    Attribute.acquisitiondate: _path_extract("privateinfo/@acquisitiondate"),
    Attribute.acquiredfrom: _path_extract("privateinfo/@acquiredfrom"),
    Attribute.invlocation: _path_extract("privateinfo/@inventorylocation"),
    Attribute.pp_currency: _path_extract("privateinfo/@pp_currency"),
    Attribute.privatecomment: _path_extract("privateinfo/privatecomment"),
}


def extract(attribute: Attribute, game_entry: GameEntry) -> str:
    return _attribute_paths[attribute](game_entry)


def extract_id(game_entry) -> GameId:
    return (
        extract(Attribute.collid, game_entry),
        extract(Attribute.objectid, game_entry),
    )


def map_collection(collection: GameCollection) -> MappedGameCollection:
    return {extract_id(item): item for item in collection}
