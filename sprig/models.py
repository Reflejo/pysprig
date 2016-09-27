import dateutil.parser

from collections import namedtuple


class Model(object):

    def __unicode_(self):
        return u"<%s>" % self.__class__.__name__

    def __str__(self):
        return self.__unicode__().decode("utf-8")

    def __repr__(self):
        return r"<%s [%s]>" % (self.__class__.__name__, self)


class User(Model):
    """
    Logged in user representation.
    """

    def __init__(self, json):
        self.app_state = json.get("app_state")
        self.phone_number = json.get("phone_number")
        self.first_name = json.get("first_name")
        self.last_name = json.get("last_name")
        self.name = json.get("name")
        self.token = json.get("authentication_token")
        self.credit_card_last4 = json.get("credit_card_last4")
        self.credit_cards = map(CreditCard, json.get("credit_cards", []))
        self.credit_card_brand = json.get("credit_card_brand")
        self.delivery_addresses = map(Address, json["delivery_addresses"])
        self.email = json.get("email")
        self.subscription_ends_at = json.get("subscription_ends_at")
        self.subscription_status = json.get("subscription_status")
        self.referral = Referral(json.get("referral", {}))
        self.balance = json.get("balance", 0)
        self.full_balance = json.get("full_balance", "$0.00 credit")
        self.id = json.get("id")

    @property
    def default_address(self):
        return self.delivery_addresses[0] if self.delivery_addresses else None

    @property
    def payment_description(self):
        return u"%s *%s" % (self.credit_card_brand, self.credit_card_last4)

    def __unicode__(self):
        return u"%s <%d>" % (self.name, self.id)


class Referral(Model):
    """
    User's referral code and share details.
    """

    def __init__(self, json):
        self.code = json.get("code")
        self.referral_amount = json.get("referral_amount")
        self.view_type = json.get("view_type")
        self.header = json.get("header")
        self.amount = json.get("amount")
        self.details = json.get("details")
        self.share_link = json.get("share_link")


class CreditCard(Model):
    """
    Credit card information including Spring internal's id.
    """

    def __init__(self, json):
        self.exp_month = json.get("exp_month")
        self.exp_year = json.get("exp_year")
        self.last4 = json.get("last4")
        self.id = json.get("id")
        self.default = json.get("defailt", False)
        self.brand = json.get("brand")

    def __unicode__(self):
        return u"%s %s" % (self.brand, self.last4)


class Address(Model):
    """
    User's delivery address information.
    """

    def __init__(self, json):
        self.parking_instructions = json.get("parking_instructions")
        self.city = json.get("city")
        self.address_city = json.get("address_city")
        self.contact_preference = json.get("contact_preference")
        self.name = json.get("name")
        self.zip = json.get("zip")
        self.apt_number = json.get("apt_number")
        self.floor_number = json.get("floor_number")
        self.state = json.get("state")
        self.buzzer_code = json.get("buzzer_code")
        self.confirmed = json.get("confirmed", False)
        self.id = json.get("id")
        self.street_address = json.get("street_address")
        self.instructions = json.get("instructions")
        self.latitude = json.get("latitude")
        self.longitude = json.get("longitude")

    def __unicode__(self):
        return self.name


class CurrentMenu(Model):
    """
    Currently available menu with all meal items.
    """

    def __init__(self, json):
        self.items = map(MenuItem, json.get("menu_items", []))
        self.inventories = json.get("inventories", [])
        self.id = json.get("menu_id")
        self.meal_name = json.get("meal_name")
        self.meal_id = json.get("meal_id")
        self.open_now = json.get("open_now", False)
        self.order_status = json.get("app_screen_status")
        self.unavailable_title = json.get("unavailable_title", "Open")
        self.tracker_id = json.get("menu_tracker_id")
        self.tracker_hash = json.get("menu_tracker_hash")

    @property
    def status(self):
        if self.open_now:
            return u"%s - %s" % (self.meal_name, self.unavailable_title)

        return u"Closed - Come back tomorrow!"

    def __unicode__(self):
        return self.status


class Menu(Model):
    """
    Upcoming menu with all meal items.
    """

    def __init__(self, json):
        self.id = json.get("menu_id")
        self.meal_name = json.get("meal_name")
        self.starts_at = dateutil.parser.parse(json.get("starts_at"))
        self.meal_id = json.get("meal_id")
        self.items = map(MenuItem, json.get("menu_items", []))

    def __unicode__(self):
        return u"%s - %s" % (self.meal_name, self.starts_at)


class MenuItem(Model):
    """
    Meal item from a menu or order. Includes all nutritional information.
    """

    def __init__(self, json):
        self.fiber = json.get("fiber")
        self.sodium = json.get("sodium")
        self.protein = json.get("protein")
        self.is_meal = json.get("is_meal", False)
        self.fat = json.get("fat")
        self.id = json.get("id")
        self.carbohydrates = json.get("carbohydrates")
        self.sugar = json.get("sugar")
        self.details = json.get("details")
        self.spicy = json.get("spicy")
        self.price = json.get("price")
        self.vegan = json.get("vegan")
        self.display_order = json.get("display_order", 10)
        self.vegetarian = json.get("vegetarian")
        self.title = json.get("title")
        self.calories = json.get("calories")
        self.gluten_free = json.get("gluten_free")
        self.image_url = json.get("large_photo_with_background_url")
        self.tracker_hash = json.get("menu_tracker_item_hash")
        self.cart_quantity = json.get("cart_quantity", 0)

    def __eq__(self, other):
        return other.id == self.id

    def __hash__(self):
        return self.id or 0

    def __unicode__(self):
        return self.title


class Confirmation(Model):
    """
    Confirmation object returned after pre-ordering a meal.
    """

    def __init__(self, json):
        self.id = json.get("id")
        self.total = json.get("total")
        self.delivery_fee = json.get("delivery_fee")
        self.rush_level = json.get("rush_level")
        self.sales_tax = json.get("sales_tax")
        self.customer_id = json.get("customer_id")
        self.items_total = json.get("items_total")
        self.line_items = map(LineItem, json.get("line_items", []))

    def __unicode__(self):
        lines = filter(lambda x: x.type == LineItem.TYPE_DISH, self.line_items)
        return u"Items: %d, Total: %f" % (len(lines), self.total / 100.0)


class LineItem(Model):
    """
    Item line from an order receipt. Including price and quantity.
    """

    TYPE_SALES_TAX = "sales_tax"
    TYPE_DISH = "dish"

    def __init__(self, json):
        self.type = json.get("type")
        self.quantity = json.get("quantity", 1)
        self.title = json.get("title")
        self.price = json.get("price", 0.0)
        self.image_url = json.get("image")

    @classmethod
    def from_menu_item(klass, menu_item, count):
        item = LineItem({})
        item.type = LineItem.TYPE_DISH
        item.quantity = count
        item.title = menu_item.title
        item.price = menu_item.price
        item.image_url = menu_item.image_url
        return item


class Order(Model):
    """
    Existing order information, used to track the driver and ETAs.
    """

    STATUS_STARTED = "started"
    STATUS_UNSTARTED = "unstarted"
    STATUS_UNRATED = "unrated"

    def __init__(self, json):
        self.id = json.get("order_id")
        self.status = json.get("app_screen_status")
        self.cart_id = json.get("cart_id")
        self.customer_eta = int(json.get("customer_eta", 0))
        self.address = Address(json.get("delivery_address"))
        self.driver_id = json.get("driver_id")
        self.driver_name = json.get("driver_name")
        self.driver_location = json.get("driver_location")
        self.driver_phone_number = json.get("driver_phone_number")
        self.last_computed_at = json.get("last_computed_at")
        self.meal_id = json.get("meal_id")
        self.menu_items = map(MenuItem, json.get("menu_items", []))

    def __unicode__(self):
        return u"address=%s status=%s" % (self.address, self.status)
