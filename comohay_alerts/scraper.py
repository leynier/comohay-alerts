from typing import List, Optional
from urllib.parse import urljoin

from bs4 import BeautifulSoup
from requests import get

from .exceptions import HTTPException
from .models import Currency, Item, Province


class Scraper:
    def __init__(
        self,
        base_url: str = "https://comohay.com",
        parser: str = "html.parser",
    ):
        self.base_url = base_url
        self.parser = parser

    def get_autocomplete(self, query: str, debug: bool = False) -> List[str]:
        url = urljoin(self.base_url, "search/autocomplete")
        response = get(url, params={"q": query})
        if debug:
            print(f"Request URL: {response.url}")
        if response.status_code != 200:
            raise HTTPException(
                status_code=response.status_code,
                detail=response.reason,
            )
        json = response.json()
        return json["results"]

    def get_items(
        self,
        query: str,
        page: int = 1,
        provinces: Optional[List[Province]] = None,
        price_from: Optional[int] = None,
        price_to: Optional[int] = None,
        price_currency: Optional[Currency] = None,
        debug: bool = False,
    ) -> List[Item]:
        url = urljoin(self.base_url, "")
        params = {"q": query, "page": page}
        if provinces:
            params["provinces"] = [province.value for province in provinces]
        if price_from is not None:
            params["price_from"] = price_from
        if price_to is not None:
            params["price_to"] = price_to
        if price_currency is not None:
            params["price_currency"] = price_currency.value
        response = get(url, params=params)
        if debug:
            print(f"Request URL: {response.url}")
        if response.status_code != 200:
            raise HTTPException(
                status_code=response.status_code,
                detail=response.reason,
            )
        soup = BeautifulSoup(response.text, self.parser)
        items = soup.find_all("div", class_="list-item-container")
        result: List[Item] = []
        for item in items:
            header = item.find("div", class_="list-item-header")  # type: ignore
            source = header.find("span", class_="list-item-badge").text.strip()
            date = header.find_all("span")[1].text.strip()
            url = item.find("div", class_="list-item-title").a["href"]  # type: ignore
            title = item.find(  # type: ignore
                "div",
                class_="list-item-title",
            ).a.text.strip()
            location = " ".join(
                filter(
                    lambda x: x,
                    item.find("div", class_="list-item-location")  # type: ignore
                    .span.text.strip()
                    .replace("\n", " ")
                    .replace("\t", " ")
                    .split(" "),
                )
            )
            price = item.find("div", class_="list-item-price")  # type: ignore
            price = price.h3.text.strip() if price else price
            description = (
                " ".join(
                    filter(
                        lambda x: x,
                        item.find("div", class_="list-item-description")  # type: ignore
                        .get_text()
                        .strip()
                        .replace("\n", " ")
                        .replace("\t", " ")
                        .split(" "),
                    )
                )
                .replace(",", ", ")
                .replace(",  ", ", ")
                .replace(";", "; ")
                .replace(";  ", "; ")
                .replace(".", ". ")
                .replace(".  ", ". ")
                .replace(":", ": ")
                .replace(":  ", ": ")
                .replace(". . .", "...")
            ).strip()
            result.append(
                Item(
                    source=source,
                    date=date,
                    url=url,
                    title=title,
                    location=location,
                    price=price,
                    description=description,
                )
            )
        return result

    def get_total(self, debug: bool = False) -> int:
        url = urljoin(self.base_url, "")
        response = get(url)
        if debug:
            print(f"Request URL: {response.url}")
        if response.status_code != 200:
            raise HTTPException(
                status_code=response.status_code,
                detail=response.reason,
            )
        soup = BeautifulSoup(response.text, self.parser)
        try:
            item = soup.select_one(
                "#search-form > div.center-content.ads-quantity > span"
            )
            total = int(item.get_text().strip().split(" ")[0])  # type: ignore
        except Exception as e:
            if debug:
                print(f"Exception: {e}")
            raise HTTPException(status_code=500, detail="Error getting total")
        return total


scraper = Scraper()


def get_scraper() -> Scraper:
    return scraper
