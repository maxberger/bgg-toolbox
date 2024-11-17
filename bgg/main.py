import asyncio
import json
from configparser import ConfigParser
from http.cookies import SimpleCookie
from typing import Any, Dict, List, Tuple

import aiohttp
import xmltodict
from openpyxl import Workbook


async def load_credentials() -> Tuple[str, str]:
    parser = ConfigParser()
    with open("credentials.ini", mode="r") as f:
        parser.read_file(f)
        return parser.get("bgg", "username"), parser.get("bgg", "password")


async def login(
    session: aiohttp.ClientSession, username: str, password: str
) -> aiohttp.ClientSession:
    login_payload = {"credentials": {"username": username, "password": password}}
    headers = {"content-type": "application/json"}
    async with session.post(
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
            session.cookie_jar.update_cookies(cookie)
        return session


async def loadcollection(session: aiohttp.ClientSession) -> List[Dict[str, Any]]:
    status = 202
    while status == 202:
        async with session.get(
            "https://boardgamegeek.com/xmlapi2/collection?username=SpielwiesnSpiele&showprivate=1&version=1"
        ) as resp:
            status = resp.status
            if status == 200:
                dict = xmltodict.parse(await resp.text())
                return dict.get("items", {}).get("item", [])
            if status == 202:
                await asyncio.sleep(1)
    raise Exception("Error loading collection")


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


def collection_by_co(
    collection: List[Dict[str, Any]]
) -> Dict[Tuple[str, str], Dict[str, Any]]:
    return {
        (item.get("@collid", ""), item.get("@objectid", "")): item
        for item in collection
    }


async def update_quantity(
    session: aiohttp.ClientSession,
    collection: List[Dict[str, Any]],
    collid: str,
    objectid: str,
    quantity: str,
) -> None:
    by_co = collection_by_co(collection)
    item = by_co.get((collid, objectid), None)
    if not item:
        raise Exception(f"Object not in collection: {collid, objectid}")
    private = item.get("privateinfo", {})
    payload = {
        "fieldname": "ownership",
        "collid": collid,
        "objecttype": "thing",
        "objectid": objectid,
        "pricepaid": private.get("@pricepaid", ""),
        "currvalue": private.get("@currvalue", ""),
        "quantity": quantity,
        "acquisitiondate": private.get("@acquisitiondate", ""),
        "dateinput": "",
        "acquiredfrom": private.get("@acquiredfrom", ""),
        "invdate": "",
        "dateinput": "",
        "invlocation": private.get("@inventorylocation", ""),
        "B1": "Cancel",
        "pp_currency": private.get("@pp_currency", ""),
        "cv_currency": "",
        "privatecomment": private.get("privatecomment", ""),
        "ajax": 1,
        "action": "savedata",
    }
    async with session.post(
        "https://boardgamegeek.com/geekcollection.php",
        data=payload,
    ) as resp:
        print(f"headers: {resp.request_info.headers}")
        print(f"rq: {resp.request_info.url}")
        print(resp.status)
        print(await resp.text())


async def main():
    async with aiohttp.ClientSession(cookie_jar=aiohttp.CookieJar(unsafe=True)) as ses:
        user, pw = await load_credentials()
        session = await login(ses, user, pw)

        collection = await loadcollection(session)
        # print(json.dumps(collection))
        await export_quantities(collection)

        # await update_quantity(session, collection, "125497554", "203828", "9")


if __name__ == "__main__":
    asyncio.run(main())
