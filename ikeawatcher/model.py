# coding=utf-8
from collections import namedtuple
from typing import Dict

ArticleCode = str

ArticleQuantity = int

CollectLocation = namedtuple("CollectLocation", "id, name")


class ShoppingCart(Dict[ArticleCode, ArticleQuantity]):
    def to_json(self):
        return [{"articleNo": a, "count": q} for a, q in self.items()]
