import asyncio
import json
from configparser import ConfigParser
from http.cookies import SimpleCookie
from typing import Optional, Tuple

import aiohttp
import xmltodict

from .model import Attribute, GameCollection, GameId, extract, map_collection


class BGGSession:

    def __init__(self):
        self.session: Optional[aiohttp.ClientSession] = None

    @staticmethod
    async def _load_credentials() -> Tuple[str, str]:
        parser = ConfigParser()
        with open("credentials.ini", mode="r") as f:
            parser.read_file(f)
            return parser.get("bgg", "username"), parser.get("bgg", "password")

    async def _login(self, username: str, password: str) -> None:
        login_payload = {"credentials": {"username": username, "password": password}}
        headers = {"content-type": "application/json"}
        async with self.session.post(
            "https://boardgamegeek.com/login/api/v1",
            data=json.dumps(login_payload),
            headers=headers,
        ) as resp:
            await resp.text()

            # BGG returns strange "deleted" cookies which break the cookie parsing.
            # Need to manually re-add the bggusername and bggpassword cookies to
            # the session object.
            valid_cookies = [
                SimpleCookie(cookie)
                for cookie in resp.headers.getall("Set-Cookie")
                if "delete" not in cookie
            ]
            for cookie in valid_cookies:
                self.session.cookie_jar.update_cookies(cookie)

    async def load_collection(self) -> GameCollection:
        status = 202
        while status == 202:
            async with self.session.get(
                "https://boardgamegeek.com/xmlapi2/collection?username=SpielwiesnSpiele&showprivate=1&version=1"
            ) as resp:
                status = resp.status
                if status == 200:
                    dict = xmltodict.parse(await resp.text())
                    return dict.get("items", {}).get("item", [])
                if status == 202:
                    await asyncio.sleep(1)
        raise Exception("Error loading collection")

    async def __aenter__(self):
        self.session = aiohttp.ClientSession(cookie_jar=aiohttp.CookieJar(unsafe=True))
        await self.session.__aenter__()
        username, password = await BGGSession._load_credentials()
        await self._login(username, password)
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.session.close()

    async def update_quantity(
        self,
        collection: GameCollection,
        id: GameId,
        quantity: str,
    ) -> None:
        by_co = map_collection(collection)
        item = by_co.get(id, None)
        if not item:
            raise Exception(f"Object not in collection: {id}")
        payload = {
            "fieldname": "ownership",
            "collid": id[0],
            "objecttype": "thing",
            "objectid": id[1],
            "pricepaid": extract(Attribute.pricepaid, item),
            "currvalue": extract(Attribute.currvalue, item),
            "quantity": quantity,
            "acquisitiondate": extract(Attribute.acquisitiondate, item),
            "dateinput": "",
            "acquiredfrom": extract(Attribute.acquiredfrom, item),
            "invdate": "",
            "dateinput": "",
            "invlocation": extract(Attribute.invlocation, item),
            "B1": "Cancel",
            "pp_currency": extract(Attribute.pp_currency, item),
            "cv_currency": "",
            "privatecomment": extract(Attribute.privatecomment, item),
            "ajax": 1,
            "action": "savedata",
        }
        async with self.session.post(
            "https://boardgamegeek.com/geekcollection.php",
            data=payload,
        ) as resp:
            print(f"headers: {resp.request_info.headers}")
            print(f"rq: {resp.request_info.url}")
            print(resp.status)
            print(await resp.text())
