# coding=utf-8
import logging
from argparse import ArgumentParser, ArgumentTypeError
from typing import Set

from ikeawatcher.api import IkeaApi
from ikeawatcher.model import ShoppingCart, ArticleCode, ArticleQuantity, CollectLocation

LOCALE = "fr_BE"
LEVEL = logging.INFO

LOGGER = logging.getLogger(__name__)
logging.basicConfig(level=LEVEL)


def _code_and_quantity(s: str) -> (ArticleCode, ArticleQuantity):
    try:
        [code, quantity] = s.split(":")
        return ArticleCode(code.replace(".", "")), ArticleQuantity(quantity)
    except Exception as e:
        raise ArgumentTypeError(f"Invalid article code & quantity: {s} ({e})")


def _parse_args():
    parser = ArgumentParser()
    parser.add_argument(u"--country",
                        help=u"Country code (ex: be)",
                        dest="country",
                        type=str,
                        required=True)
    parser.add_argument(u"--delivery",
                        help=u"Zip code for delivery",
                        dest="delivery_zip_codes",
                        type=str,
                        action='append',
                        required=False)
    parser.add_argument(u"--collect",
                        help=u"Partial collect location name",
                        dest="collect_locations",
                        type=str,
                        action='append',
                        required=False)
    parser.add_argument('--try-all',
                        action="store_true",
                        help='Do not stop on first match',
                        required=False)
    parser.add_argument(u"articles",
                        metavar="code:quantity",
                        help=u"code:quantity of the article to purchase",
                        nargs='+',
                        type=_code_and_quantity)
    args = parser.parse_args()
    if not args.delivery_zip_codes and not args.collect_locations:
        raise ArgumentTypeError("At least 1 collect location or 1 delivery zip code is required")
    return args


def main():
    try:
        args = _parse_args()
        try_all = args.try_all
        ikea_api = IkeaApi(args.country, LOCALE)
        shopping_cart = ShoppingCart(args.articles)
        LOGGER.info(f"Shopping cart = {shopping_cart}")

        success = False

        selected_locations: Set[CollectLocation] = set()
        if args.collect_locations:
            LOGGER.info("Searching for collect locations ...")
            collect_locations = ikea_api.get_collect_locations()
            for searched_location in args.collect_locations:
                found = {loc for loc in collect_locations if searched_location.strip().upper() in loc.name.upper()}
                if not found:
                    raise Exception(f"Collect location '{searched_location}' not found."
                                    f" Available locations are {found}")
                elif len(found) > 1:
                    raise Exception(f"Multiple locations found for '{searched_location}': {found}")
                else:
                    LOGGER.debug(f"location {found} found for input {searched_location}")
                    selected_locations.update(found)

        if not success or try_all:
            for zip_code in set(args.delivery_zip_codes or []):
                result, details = ikea_api.check_express_delivery(shopping_cart, zip_code)
                LOGGER.info(f"Deliverable to {zip_code} ? {result}")
                success = success or result
                if success and not try_all:
                    break

        if not success or try_all:
            for location in selected_locations:
                if not success or try_all:
                    result, details = ikea_api.check_click_and_collect(shopping_cart, location)
                    LOGGER.info(f"Collectable at location {location.name}? {result}")
                    success = success or result
                    if success and not try_all:
                        break

        if success:
            LOGGER.info("Articles are available :)")
            exit(0)
        else:
            LOGGER.error("Articles are not available :(")
            exit(1)

    except Exception as e:
        LOGGER.exception(f"Error checking items availability: {e}")
        exit(2)


if __name__ == '__main__':
    main()
