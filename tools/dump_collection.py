import asyncio
import json

import bgg


async def main():
    async with bgg.BGGSession() as bgg_session:
        collection = await bgg_session.load_collection()
        print(json.dumps(collection))


if __name__ == "__main__":
    asyncio.run(main())
