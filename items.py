import string
from urllib.parse import quote_plus

import stripe
from flask import request

from main import Item, db
from random import choices, randrange

# Use this as a tool to populate a placeholder database of items for sale

def make_placeholder_data(quantity):
    chars = f"{string.digits} {string.ascii_letters}"

    for i in range(quantity):
        name = "".join(choices(chars, k=randrange(3, 12)))
        price = "".join(choices(string.digits, k=randrange(1, 3))) + "." + "".join(choices(string.digits, k=2))
        description = " ".join(["".join(choices(chars, k=randrange(2, 9))) for x in range(randrange(12, 50))])
        new_item = Item(name=name,
                        image="static/placeholder.png",
                        price=price,
                        description=description,
                        available=randrange(0, 5),
                        in_a_cart=0,
                        product_id=None
                        )
        db.session.add(new_item)
        db.session.commit()
        print(f"name: {name}")
        print(f"image: static/placeholder.png")
        print(f"price: ${price}")
        print(f"description: {description}")
        print(f"available: {randrange(0, 5)}")


def fill_inventory(amount = 10):
    for item in Item.query.all():
        item.available += randrange(0, 20)
        db.session.commit()


def show_availability():
    for item in Item.query.all():
        print(f"{item.name}: {item.available}")



# stripe stores price data as an integer value for the price in cents
# attempting to use type hints
# this function takes a string, modifies it, and returns an integer.
def price_fix(price: string) -> int:
    return int(price.replace('.', ''))

def add_products_to_stripe():
    for item in Item.query.all():
        new_product = stripe.Product.create(
          name=item.name,
          default_price_data={"unit_amount": price_fix(item.price), "currency": "usd"},
          expand=["default_price"],
          images=['http://127.0.0.1:5000//static/placeholder.png']
        )
        item.product_id = new_product.id
        db.session.commit()

# I'm assuming here that I'll be able to access the price from a product_id
def add_prices_to_stripe_products():
    for product in stripe.Product.list():
        # stripe.Price.create(
        #     product='product.id',
        #     unit_amount=product.default_price_data,
        #     currency="usd",
        # )
        print(product.default_price)
        # print(f"product={product.id}, unit_amount={product.default_price_data.unit_amount}")

def add_images_to_stripe_products():
    for product in stripe.Product.list():
        product.images = ['http://127.0.0.1:5000//static/placeholder.png']

def print_stripe_list():
    list = stripe.Product.list()
    print(list)
    print(len(list))


make_placeholder_data(10)
fill_inventory()
add_products_to_stripe()
# show_availability()
# print_stripe_list()
add_prices_to_stripe_products()
add_images_to_stripe_products()
# print('http://127.0.0.1:5000//static/placeholder.png')

