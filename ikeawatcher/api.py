# coding=utf-8
import hashlib
import hmac
import json
import logging
from typing import Dict, Set

import requests

from ikeawatcher.model import CollectLocation, ShoppingCart

LOGGER = logging.getLogger(__name__)

_HMAC_ALGO = hashlib.sha1
_HMAC_KEY = "G6XxMY7n"


class IkeaApi:

    def __init__(self, country, locale):
        self._country = country.strip().lower()
        self._locale = locale

    def get_collect_locations(self) -> Set[CollectLocation]:
        url = f"https://ww8.ikea.com/clickandcollect/{self._country}/receive/listfetchlocations?version=2"
        response = requests.get(url)
        response.raise_for_status()
        locations_by_id = response.json()

        """
        Example values for Belgium
        locations_by_id = {
            '76ffc2d2-3327-4191-ae4f-83f4b2e3920a': {'name': 'IKEA Hasselt', 'isClosed': False, 'closingTimes': ''},
            '3a27b7d5-bad0-4d6a-9186-296ecd396a28': {'name': '- Pick-up Point Dockx Hasselt-West', 'isClosed': False,
                                                     'closingTimes': ''},
            '99931b05-27fc-42e2-bf56-46446b91e1b5': {'name': '- Pick Up Point BD MyShopi Geel', 'isClosed': False,
                                                     'closingTimes': ''},
            'ea21bc9c-6c6f-4f3c-b980-c63a648687f5': {'name': 'IKEA Zaventem', 'isClosed': False, 'closingTimes': ''},
            '3c0eeb5d-998b-4e32-a8b2-11c677b6c009': {'name': '- Pick-up Point Dockx Machelen', 'isClosed': False,
                                                     'closingTimes': ''},
            '68271b0b-8090-4d06-86b1-ef54c13f511a': {'name': '- Pick-up Point Dockx Herent', 'isClosed': False,
                                                     'closingTimes': ''},
            '56e815a3-b641-48a1-8ea7-82755ef936b3': {'name': 'IKEA Arlon', 'isClosed': False, 'closingTimes': ''},
            '36bc78f3-a74e-4cfe-bb54-efe13d4712d5': {'name': 'IKEA Mons', 'isClosed': False, 'closingTimes': ''},
            '7997ba73-9928-4381-a3e8-1739a01c5d4f': {'name': '- Pick-up Point Roeselare', 'isClosed': False,
                                                     'closingTimes': ''},
            '8b9ae83a-1266-4cd4-b12d-59f0ad6c9543': {'name': '- Pick-up Point Dockx Jumet', 'isClosed': False,
                                                     'closingTimes': ''},
            'c0ced698-b6fe-4418-8813-5cc5a0a841a5': {'name': '- Pick-up Point Rekkem', 'isClosed': False,
                                                     'closingTimes': ''},
            'af983201-e1ef-48e8-9781-cf530d73349d': {'name': 'IKEA Gent', 'isClosed': False, 'closingTimes': ''},
            '274ea32b-61d3-47a2-bbaa-4b4a518fa826': {'name': '- Pick-up Point Dockx Aalst', 'isClosed': False,
                                                     'closingTimes': ''},
            'f4ec9269-112d-4c92-ae31-f1d9c1ae0c86': {'name': '- Pick-up Point Dockx Oudenaarde', 'isClosed': False,
                                                     'closingTimes': ''},
            'acf5b993-acee-4d7c-b7f2-573ca4f75129': {'name': 'IKEA Wilrijk', 'isClosed': False, 'closingTimes': ''},
            '0436634a-1560-4a23-afce-4917b149f7ca': {'name': '- Pick-up Point Sint-Niklaas', 'isClosed': False,
                                                     'closingTimes': ''},
            '7bc38679-8264-44a2-a4e9-9ee5107b5bcc': {'name': '- Click and Collect Box Mechelen', 'isClosed': False,
                                                     'closingTimes': ''},
            '1e1f5b73-06a5-4bfa-bd5a-59dbc33cc8c3': {'name': 'IKEA Anderlecht (Brussels)', 'isClosed': False,
                                                     'closingTimes': ''},
            'cd4d0a31-771f-4cb9-8ced-c246a2d61104': {'name': '- Pick-up Point Dockx Nivelles', 'isClosed': False,
                                                     'closingTimes': ''},
            '9805f302-33e3-48f8-90c1-9b700953e7f4': {'name': 'IKEA Liège', 'isClosed': False, 'closingTimes': ''},
            '39ff81bc-a3cc-4b4e-a38d-e6cfad98bf3d': {'name': '- Pick-Up Point City Depot Naninne', 'isClosed': False,
                                                     'closingTimes': ''},
            'a08a2b93-6783-4626-b8d9-f520ceb05dfc': {'name': '- Pick-Up Point Dockx Verviers', 'isClosed': False,
                                                     'closingTimes': ''}}
        """
        result = {CollectLocation(id=loc_id, name=loc["name"]) for loc_id, loc in locations_by_id.items()}
        LOGGER.debug(f"Collect locations: {result}")
        return result

    def check_express_delivery(self, shopping_cart: ShoppingCart, zip_code: str, promotion_code: str = None):
        url = f"https://ww8.ikea.com/clickandcollect/{self._country}/receive/receiveexpress/"
        # url = f"https://ww8.ikea.com/clickandcollect/{self._country}/receive/"
        payload = {
            "selectedService": "express",
            "selectedServiceValue": zip_code,
            "articles": shopping_cart.to_json(),
            "locale": self._locale,
            "customerView": "desktop",
            "system": "IRW",
            "promotionCode": promotion_code or ""
        }
        result, details = self._make_delivery_request(url, payload)

        """
        example response:
        {
           "status": "OK",
           "target": "https://ww8.ikea.com/clickandcollect/be/start/JR8PpQa7eW1nuregZ4J2pTA1lVLsBKXl",
           "servicePrices": {
              "homeDelivery": {
                 "price": 39.9,
                 "deliveryHandling": "2 man"
              },
              "status": "OK"
       }
        """

        return result, details

    def check_click_and_collect(self, shopping_cart: ShoppingCart, location: CollectLocation,
                                promotion_code: str = None):
        url = f"https://ww8.ikea.com/clickandcollect/{self._country}/receive/"
        payload = {
            "selectedService": "fetchlocation",
            "selectedServiceValue": location.id,
            "articles": shopping_cart.to_json(),
            "locale": self._locale,
            "customerView": "desktop",
            "slId": "1241241241",
            "promotionCode": promotion_code or ""
        }
        result, details = self._make_delivery_request(url, payload)
        return result, details

    def _make_delivery_request(self, url: str, payload: Dict) -> (bool, Dict):
        payload_json = json.dumps(payload, separators=(',', ':'))
        data = {
            "payload": payload_json,
            "hmac": self._generate_hmac(payload_json),
            # "backUrl": "https://order.ikea.com/be/fr/checkout/delivery/"
        }
        LOGGER.debug(f"Delivery request: {json.dumps(data, indent=3)}")
        response = requests.post(url, json=data)
        response.raise_for_status()
        json_response = response.json()
        LOGGER.debug(f"Delivery response: {json.dumps(json_response, indent=3)}")

        is_success = json_response.get("status", "").upper() == "OK"
        return is_success, json_response

    @staticmethod
    def _generate_hmac(data):
        return hmac.new(_HMAC_KEY.encode("utf8"), data.encode("utf8"), _HMAC_ALGO).digest().hex()
