from typing import List

import cloudscraper
import pytz
import requests
import datetime


class StoreResponse:
    def __init__(self, data):
        self.id = data.get("id")
        self.name = data.get("name")
        self.vendor_code = data.get("vendor_code")


class SearchProductResult:
    def __init__(self, data):
        self.name = data.get("name")
        self.brand = data.get("brand")
        self.size = data.get("size")
        self.id = data.get("id")
        self.unit = data.get("unit")


class SearchResults:
    def __init__(self, data):
        self.hits = [SearchProductResult(x) for x in data.get("hits", [])]

        self.query = data.get("query")
        self.limit = data.get("limit")
        self.offset = data.get("offset")

        self.processing_time_ms = data.get("processingTimeMs")
        self.estimated_total_hits = data.get("estimatedTotalHits")


class ProductsPriceResult:
    def __init__(self, data):
        self.store_id = data.get("store_id")
        self.store_name = data.get("store_name")
        self.vendor_code = data.get("vendor_code")
        self.original_price = data.get("original_price")
        self.sale_price = data.get("sale_price")
        self.club_price = data.get("club_price")
        self.multibuy_price = data.get("multibuy_price")
        self.multibuy_quantity = data.get("multibuy_quantity")
        self.multibuy_limit = data.get("multibuy_limit")
        self.club_multibuy_price = data.get("club_multibuy_price")
        self.club_multibuy_quantity = data.get("club_multibuy_quantity")
        self.club_multibuy_limit = data.get("club_multibuy_limit")

    @property
    def lowest(self):
        prices = [x for x in [self.original_price, self.sale_price, self.club_price] if x]
        return min(prices) if prices else None


class ProductsResult:
    def __init__(self, data):
        self.id = data.get("id")
        self.name = data.get("name")
        self.brand = data.get("brand")
        self.unit = data.get("unit")
        self.size = data.get("size")
        self.prices = [ProductsPriceResult(x) for x in data.get("prices", [])]

    @property
    def full_product_name(self):
        return f"{self.brand} {self.name}"


class Grocer:

    def __init__(self):
        self.backend_base_url = "https://backend.grocer.nz"
        self.search_base_url = "https://search.grocer.nz"

        self.scraper = cloudscraper.create_scraper()

    def updated_at(self) -> datetime.datetime:
        response = requests.get(self.backend_base_url + "/updatedAt")

        response.raise_for_status()

        unix_epoch = int(response.text)
        return datetime.datetime.fromtimestamp(unix_epoch, tz=pytz.timezone("NZ"))

    def get_stores(self) -> list[StoreResponse]:
        response = requests.get(self.backend_base_url + "/stores")

        response.raise_for_status()

        return [StoreResponse(x) for x in response.json()]

    def search(self, limit=10, offset=0, query="", filter_results=None, attributes=None) -> SearchResults:
        if not filter_results:
            filter_results = []
        if not attributes:
            attributes = ["id", "name", "brand", "unit", "size"]

        payload = {
            "filter": filter_results,
            "limit": limit,
            "offset": offset,
            "q": query,
            "attributesToRetrieve": attributes,
        }

        response = self.scraper.post(self.search_base_url + "/indexes/products/search", json=payload, headers={"Authorization": "Bearer 7f58239330307ec585c86863f985ab83cbb9ce951a9601c66e158548fb632fd1"})
        response.raise_for_status()
        return SearchResults(response.json())

    def get_products_by_id(self, product_ids, store_ids) -> List[ProductsResult]:
        product_query = "&".join(["productIds[]=" + str(x) for x in product_ids])
        store_query = "&".join(["storeIds[]=" + str(x) for x in store_ids])
        response = requests.get(self.backend_base_url + "/products", params=f"{product_query}&{store_query}")
        response.raise_for_status()
        return [ProductsResult(x) for x in response.json()]

    def get_product_by_barcode(self, barcode, store_ids) -> ProductsResult:
        store_query = "&".join(["stores[]=" + str(x) for x in store_ids])

        response = self.scraper.get(self.backend_base_url + "/product", params=f"barcode={barcode}&"+store_query)

        response.raise_for_status()
        return ProductsResult(response.json())

    def gen_product_image_url(self, product_id) -> list[str]:
        return [
            f"https://grocer-au.syd1.cdn.digitaloceanspaces.com/products/{product_id}.webp",
            f"https://grocer-au.syd1.cdn.digitaloceanspaces.com/products/{product_id}.jpg",
        ]
