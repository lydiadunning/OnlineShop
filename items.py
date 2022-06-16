import string
from urllib.parse import quote_plus
from main import Item, db
from random import choices, randrange

# Use this as a tool to populate a placeholder database of items for sale

def make_placeholder_data(quantity):
    chars = f"{string.digits} {string.ascii_letters}"

    for i in range(quantity):
        name = "".join(choices(chars, k=randrange(3, 12)))
        price = "".join(choices(string.digits, k=randrange(1, 3))) + "." + "".join(choices(string.digits, k=2))
        description = "".join(choices(chars, k=randrange(100, 200)))
        new_item = Item(name=name,
                        image="static/placeholder.png",
                        price=price,
                        description=description,
                        available=randrange(0, 5)
                        )
        db.session.add(new_item)
        db.session.commit()
        print(f"name: {name}")
        print(f"image: static/placeholder.png")
        print(f"price: ${price}")
        print(f"description: {description}")
        print(f"available: {randrange(0, 5)}")

# make_placeholder_data(10)

def fill_inventory(amount = 10):
    for item in Item.query.all():
        item.available += amount
        db.session.commit()

fill_inventory()