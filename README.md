# Sprig Unofficial Python API

An unofficial Python API that let you check upcoming menus, order food
and track your order.

## Disclaimer

**This is not an official API. I am not afiliated with Sprig in any
way, and am not responsible of any damage that could be done with it.
Use it at your own risk.**

## Usage

### Login

Most calls are authenticated and therefore the `Spring` object needs to be
authenticated before use.

```python
>>> from sprig import Sprig
>>> sprig = Sprig()
>>> sprig.login("Reflejo@gmail.com", "s3cr3t")
>>> sprig.user
<User [Martin Conte Mac Donell <1337>]>

```

### Retrieve current menu

To retreive the current menu when Sprig delivery is open you can use the
`menu` method.

```python
>>> sprig.login("Reflejo@gmail.com", "s3cr3t")
>>> sprig.menu()
<CurrentMenu [Dinner - WE'RE BUSY - BUT WE'RE ON IT!]>

```

### Retrieve upcoming menus

To retrieve the upcoming menus for the week you can use the `upcoming_menus`
method.

```python
>>> sprig.upcoming_menus()
[<Menu [Brunch - 2016-09-24 08:00:00-07:00]>, ...]

```

### Retrieve upcoming menus

To retreive the ongoing order containing driver's information, order status
and ETAs you can use the `track` method.

```python
>>> order = sprig.track()
>>> order
<Order [address=home status=started]>
>>> order.driver_location
{u'latitude': 37.173097520694, u'longitude': -122.290945646912}

```

### Finish order

To finish the order you can call `finish` method. In the future this method
will allow driver's rating.

```python
>>> order = sprig.track()
>>> sprig.finish(order.id)

```

## License

This project is released under the MIT license.
