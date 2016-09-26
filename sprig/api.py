import json
import random
import urllib
import urllib2

from functools import wraps
from models import User, Menu, CurrentMenu, Confirmation, Order

URL = {
    "menu": "https://prod.eatsprig.com/api/customer/menus/current",
    "upcoming": "https://prod.eatsprig.com/api/customer/menus/upcoming",
    "login": "https://prod.eatsprig.com/api/customer/login",
    "settings": "https://prod.eatsprig.com/api/customer/settings",
    "carts": "https://prod.eatsprig.com/api/customer/carts",
    "order": "https://prod.eatsprig.com/api/customer/order",
    "ratings": "https://prod.eatsprig.com/api/customer/ratings",
}


class ConnectionError(Exception):
    """
    Unhandled error produced when trying to make a request to Spring's API.
    """


class MenuNotAvailable(Exception):
    """
    This error is thrown when the requested items are no longer available.
    """


class NotLoggedInError(Exception):
    """
    This error is thrown when trying to request an authenticated endpoint
    without authentication (e.g. before loging in).
    """


def _ensure_login(f):
    # Decorator to ensure user is logged in before making the API call.
    @wraps(f)
    def wrapper(self, *args, **kwargs):
        if not self.user:
            raise NotLoggedInError("Please log in first.")

        return f(self, *args, **kwargs)

    return wrapper


class Sprig(object):
    """
    Spring's API python implementation. Supports making order and retriving
    both current menu and upcoming menus. Note that you need an user with an
    address and payment method setup before using this class.

    Usage example
    -------------

    >>> sprig = Sprig()
    >>> sprig.login("Reflejo@gmail.com", "3x4mpl3")
    >>> sprig.menu().meal_name
    u'Dinner'
    """

    def __init__(self):
        self.user = None
        self.session_id = self._generate_session()

    def setup(self):
        """
        Initial configuration parameters such as stripe key (unauthenticated).

        Example
        -------

        >>> sprig = Sprig()
        >>> sprig.setup()
        >>> sprig.stripe_key
        u'pk_live_example'
        """
        JSON = self._request("settings")
        self.stripe_key = JSON["stripe_publishable_key"]

    def login(self, email, password):
        """
        Logs the given user in.

        - parameter email:    A string representing the user's email.
        - parameter password: A string representing the user's password.

        Example
        -------

        >>> sprig = Sprig()
        >>> sprig.login("Reflejo@gmail", "3x4mpl3")
        >>> sprig.user
        <User [Martin Conte Mac Donell <1337>]>
        """
        params = {"email": email, "password": password}
        self.user = User(self._request("login", params))

    @_ensure_login
    def confirm(self, menu, items):
        """
        Starts an order on the given menu. This call should be made before
        finalizing the order, when items are not available this function will
        throw `MenuNotAvailable`.

        - parameter email:    A string representing the user's email.
        - parameter password: A string representing the user's password.

        - returns: A `Confirmation` instance that should be used to finally
                   place the order.

        Example
        -------

        >>> sprig = Sprig()
        >>> sprig.login("Reflejo@gmail", "3x4mpl3")
        >>> menu = sprig.menu()
        >>> sprig.confirm(menu, {menu.items[0]: 2})
        <Confirmation [Items: 2, Total: 27.080000]>
        """
        items = [{
            "id": item.id,
            "quantity": count,
            "menu_tracker_item_hash": item.tracker_hash
        } for item, count in items.iteritems() if count > 0]

        address = self.user.default_address
        params = {
            "items": items,
            "street": address.street_address,
            "city": address.city,
            "zip": address.zip,
            "latitude": address.latitude,
            "longitude": address.longitude,
            "menu_id": menu.id,
            "menu_tracker_id": menu.tracker_id,
            "menu_tracker_hash": menu.tracker_hash,
            "group_order": False
        }
        try:
            confirmation = self._request("carts", params)
        except urllib2.URLError, e:
            if getattr(e, 'code', 0) == 409:
                JSON = json.loads(e.read() or "{}")
                raise MenuNotAvailable(JSON.get("message"))
            raise

        return Confirmation(confirmation)

    @_ensure_login
    def place_order(self, confirmation, menu):
        """
        Places an (already confirmed) order for immediate delivery.

        - parameter confirmation: The previously confirmed items requested.
        - parameter menu:         The menu where the order was placed.

        - returns: An `Order` object that can be used to track the order.

        Example
        -------

        >>> sprig = Sprig()
        >>> sprig.login("Reflejo@gmail", "3x4mpl3")
        >>> menu = sprig.menu()
        >>> confirm = sprig.confirm(menu, {menu.items[0]: 1})
        >>> sprig.place_order(confirm, menu)
        <Order [address=home status=unstarted]>
        """
        params = {
            "meal_id": menu.meal_id,
            "cart_id": confirmation.id,
            "menu_id": menu.id,
            "menu_tracker_id": menu.tracker_id,
            "async": True,
            "city": self.user.default_address.city,
            "delivery_address_id": self.user.default_address.id,
        }
        order = self._request("order", params)
        return Order(order)

    @_ensure_login
    def menu(self):
        """
        Returns the current menu. Only when Sprig delivery is open.

        - returns: A `CurrentMenu` object with all items available.

        Example
        -------

        >>> sprig = Sprig()
        >>> sprig.login("Reflejo@gmail", "3x4mpl3")
        >>> sprig.menu()
        <CurrentMenu [Dinner - WE'RE BUSY - BUT WE'RE ON IT!]>
        """
        address = self.user.default_address
        params = {"latitude": address.latitude, "longitude": address.longitude}
        menu = self._request("menu", query=params)
        return CurrentMenu(menu)

    @_ensure_login
    def upcoming_menus(self):
        """
        Returns all week's upcoming menus.

        - returns: An array of `Menu` with all week's upcoming menus.

        Example
        -------

        >>> sprig = Sprig()
        >>> sprig.login("Reflejo@gmail", "3x4mpl3")
        >>> sprig.upcoming_menus()
        [<Menu [Brunch - 2016-09-24 08:00:00-07:00]>, ...]
        """
        address = self.user.default_address
        params = {"latitude": address.latitude, "longitude": address.longitude}
        upcoming = self._request("upcoming", query=params)
        return map(Menu, upcoming.get("menus", []))

    @_ensure_login
    def track(self, last_computed_at=None):
        """
        Returns the ongoing order which contains driver's information,
        order status and ETAs.

        - returns: An `Order` object containing driver's location and ETAs.

        Example
        -------

        >>> sprig = Sprig()
        >>> sprig.login("Reflejo@gmail", "3x4mpl3")
        >>> order = sprig.track()
        >>> order
        <Order [address=home status=started]>
        >>> order.driver_location
        {u'latitude': 37.173097520694, u'longitude': -122.290945646912}
        """
        address = self.user.default_address
        params = {"city": address.city}
        if last_computed_at:
            params["last_computed_at"] = last_computed_at

        order = self._request("track", query=params)
        return Order(order)

    @_ensure_login
    def finish(self, order_id):
        """
        Finishes the given order (skips rating).

        Example
        -------

        >>> sprig = Sprig()
        >>> sprig.login("Reflejo@gmail", "3x4mpl3")
        >>> order = sprig.track()
        >>> sprig.finish(order.id)
        """
        params = {"order_id": order_id}
        self._request("ratings", params).get("id")

    # - Private helpers

    def _request(self, key, params=None, query=None):
        is_json = isinstance(params, dict)
        params = json.dumps(params) if is_json else params
        query = urllib.urlencode(query) if query else None
        opener = urllib2.build_opener()
        headers = {
            "X-Sprig-Session-Id": self.session_id,
            "Accept": "application/vnd.eatsprig.v8+json",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_0)"
        }

        if is_json:
            headers["Content-Type"] = "application/json;charset=UTF-8"

        if self.user:
            encoded = "{email}:{token}" \
                .format(email=self.user.email, token=self.user.token) \
                .encode("base64") \
                .strip()
            headers["Authorization"] = "Basic %s" % encoded

        url = URL[key] + "?" + query if query else URL[key]
        try:
            req = urllib2.Request(url, data=params, headers=headers)
            response = opener.open(req).read()
        except urllib2.URLError, e:
            http_code = getattr(e, 'code', None)
            if http_code == 400:
                JSON = json.loads(e.read() or "{}")
                raise ConnectionError(JSON.get("message"))
            elif http_code == 401:
                JSON = json.loads(e.read() or "{}")
                raise NotLoggedInError(JSON.get("message"))
            elif http_code == 404:
                raise ConnectionError("[%s] Resource (not found)" % key)
            else:
                raise

        return json.loads(response)

    def _generate_session(self):
        digits = []

        for letter in "xxxxxxxxxxxx4xxxyxxxxxxxxxxxxxxx":
            if letter not in ["x", "y"]:
                digits.append(letter)
                continue

            x = random.randrange(0, 15)
            digit = x if letter == "x" else (3 & x | 8)
            digits.append("%x" % digit)

        return "".join(digits)
