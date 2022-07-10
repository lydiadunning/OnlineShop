import string

from flask import Flask, render_template, redirect, request, url_for, session, abort
from flask_sqlalchemy import SQLAlchemy
from urllib.parse import quote_plus, unquote_plus
import os
from dotenv import load_dotenv
import stripe

load_dotenv()
# This is a public sample test API key.
# Don’t submit any personally identifiable information in requests made with this key.
# Sign in to see your own test API key embedded in code samples.
stripe.api_key = os.getenv('STRIPE_SECRET_KEY')

# I don't fully understand why this web app requires a login.
# I guess I can mimic other sites


app = Flask(__name__)
app.secret_key = "secret key"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///items.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)



class Item(db.Model):
    # A single item for sale
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), unique=True, nullable=False)
    image = db.Column(db.String(20), nullable=False)
    price = db.Column(db.String(10), nullable=False)
    description = db.Column(db.String(200))
    available = db.Column(db.Integer)
    in_a_cart = db.Column(db.Integer)
    product_id = db.Column(db.String(20), unique=True, nullable=True)

db.create_all()


def remove_from_cart(item_id, canceled_or_purchased, quantity=1):
    item_to_remove = Item.query.get(item_id)
    if item_to_remove:
        if item_id in session['cart_dict'].keys():
            if session['cart_dict'][item_id] > quantity:
                session['cart_dict'][item_id] -= quantity
                if canceled_or_purchased == 'canceled':
                    item_to_remove.available += quantity
                    item_to_remove.in_a_cart -= quantity
                elif canceled_or_purchased == 'purchased':
                    item_to_remove.in_a_cart -= quantity
            elif session['cart_dict'][item_id] == quantity:
                del session['cart_dict'][item_id]
                if canceled_or_purchased == 'canceled':
                    item_to_remove.available += quantity
                    item_to_remove.in_a_cart -= quantity
                elif canceled_or_purchased == 'purchased':
                    item_to_remove.in_a_cart -= quantity
            db.session.commit()
            session.modified = True
        # returns the name of the item to avoid unnecessary database calls.
        return quote_plus(item_to_remove.name)
    else:
        return


def clear_cart(cancelled_or_purchased):
    for item_id, item_quantity in session['cart_dict'].items():
         remove_from_cart(item_id, cancelled_or_purchased, item_quantity)

def return_cart_total():
    if session['cart_dict']:
        total = 0
        for item_id, item_quantity in session['cart_dict'].items():
            cart_item = Item.query.get(item_id)
            price = float(cart_item.price)
            total += (price * item_quantity)
        return '{:#.2f}'.format(total)
    else:
        return '0.00'



@app.route('/')
def home():
    if 'cart_dict' not in session:
        session['cart_dict'] = {}
    items = Item.query.all()
    for item in items:
        item.url = quote_plus(item.name)
    print('home: ' + str(session['cart_dict']))
    return render_template('item_list.html', items=items, cart_dict=session['cart_dict'], cart_total=return_cart_total())


@app.route('/<name_url>', methods=['GET', 'POST'])
def item(name_url):
    name = unquote_plus(name_url)
    item_to_show = Item.query.filter_by(name=name).first()
    if item_to_show:
        if 'cart_dict' not in session:
            session['cart_dict'] = {}
            session.modified = True
        if str(item_to_show.id) in session['cart_dict']:
            amount_in_cart = session['cart_dict'][str(item_to_show.id)]
        else:
            amount_in_cart = 0
        return render_template('item.html',
                               item=item_to_show,
                               available=item_to_show and item_to_show.available,
                               amount_in_cart=amount_in_cart,
                               cart_total=return_cart_total())
    else:
        abort(404)


@app.route('/add/<source>/<item_id>', methods=['GET', 'POST'])
def add(source, item_id):
    new_item = Item.query.get(item_id)
    if source and new_item:
        new_item_url = quote_plus(new_item.name)
        if new_item.available:
            if item_id in session['cart_dict']:
                session['cart_dict'][item_id] += + 1
                session.modified = True
                new_item.available -= 1
                new_item.in_a_cart += 1
                db.session.commit()
            else:
                session['cart_dict'][item_id] = 1
                session.modified = True
                new_item.available -= 1
                new_item.in_a_cart += 1
                db.session.commit()
        else:
            # replace this print statement
            print("Out of stock")
        return redirect(url_for(source, name_url=new_item_url))
    else:
        abort(404)

@app.route('/remove/<source>/<item_id>', methods=['GET', 'POST'])
def remove(source, item_id):
    item_to_remove_url = remove_from_cart(item_id, 'canceled', 1)
    if source and item_to_remove_url:
        print('source: ' + source )
        print('session before redirect: ' + str(session['cart_dict']))
        return redirect(url_for(source, name_url=item_to_remove_url))
    abort(404)

@app.route('/cart')
def cart():
    item_list = []
    for item_id in session['cart_dict']:
        item = Item.query.get(item_id)
        # item_dict[quote_plus(item.name)] = item
        item.url = quote_plus(item.name)
        item_list.append(item)
        # item_list.append(Item.query.get(item_id))
        print(session['cart_dict'])
        print(item.id)
        print(type(item.id))

    return render_template('cart.html', cart_dict=session['cart_dict'], items=item_list, cart_total=return_cart_total())

def price_fix(price: string) -> int:
    return int(price.replace('.', ''))


# Lifted from stripe documentation: https://stripe.com/docs/checkout/quickstart
@app.route('/checkout', methods=['POST'])
def create_checkout_session():
    try:
        checkout_session = stripe.checkout.Session.create(
            line_items=[
                {'price': stripe.Product.retrieve(Item.query.get(item_id).product_id).default_price,
                 'quantity': session['cart_dict'][item_id]
                 } for item_id in session['cart_dict']
            ],
            mode='payment',
            success_url=f'{request.base_url}/success',
            cancel_url=f'{request.base_url}/cancel'
        )
    except Exception as e:
        print(str(e))
        return str(e)

    return redirect(checkout_session.url, code=303)

@app.route('/success')
def success():
    return render_template('success.html', cart_total=return_cart_total())

@app.route('/checkout/cancel')
def cancel():
    return redirect(url_for('cart'))

if __name__ == '__main__':
    app.run(debug=True)