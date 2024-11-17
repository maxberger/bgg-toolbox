import asyncio
from typing import Any, Dict, List

from openpyxl import Workbook

import bgg
from bgg.model import Attribute, extract

attributes_to_extract = [
    Attribute.collid,
    Attribute.objectid,
    Attribute.title,
    Attribute.version_yearpublished,
    Attribute.version_publishers,
    Attribute.quantity,
]


async def export_quantities(collection: List[Dict[str, Any]]) -> None:
    wb = Workbook()
    ws = wb.active

    ws.append([attribute.name for attribute in attributes_to_extract])
    for item in collection:
        ws.append([extract(attribute, item) for attribute in attributes_to_extract])
    wb.save("quantities.xlsx")


async def main():
    async with bgg.BGGSession() as bgg_session:
        collection = await bgg_session.load_collection()
        await export_quantities(collection)


if __name__ == "__main__":
    asyncio.run(main())
