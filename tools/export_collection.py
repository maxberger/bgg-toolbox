import asyncio
from typing import Any, Dict, List

from openpyxl import Workbook

import bgg


async def export_quantities(collection: List[Dict[str, Any]]) -> None:
    wb = Workbook()
    ws = wb.active

    ws.append(["collid", "objectid", "name", "quantity"])
    for item in collection:
        collid: str = item.get("@collid", "")
        objectid: str = item.get("@objectid", "")
        name: str = item.get("name", {}).get("#text", "")
        quantity: str = item.get("privateinfo", {}).get("@quantity", "")
        ws.append([collid, objectid, name, quantity])
    wb.save("quantities.xlsx")


async def main():
    async with bgg.BGGSession() as bgg_session:
        collection = await bgg_session.load_collection()
        await export_quantities(collection)


if __name__ == "__main__":
    asyncio.run(main())
