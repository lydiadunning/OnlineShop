from flask import Flask, render_template, redirect, request, url_for, session
from flask_sqlalchemy import SQLAlchemy
from urllib.parse import quote_plus, unquote_plus


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
    # url = db.Column(db.String(20), unique=True, nullable=False)
    image = db.Column(db.String(20), nullable=False)
    price = db.Column(db.String(10), nullable=False)
    description = db.Column(db.String(200))
    available = db.Column(db.Integer)

db.create_all()

@app.route('/')
def home():
    items = Item.query.all()
    for item in items:
        item.url = quote_plus(item.name)
    return render_template('item_list.html', items=items)


@app.route('/<name_url>', methods=['GET', 'POST'])
def item(name_url):
    name = unquote_plus(name_url)
    item_to_show = Item.query.filter_by(name=name).first()
    # print(name)
    # print(f"name: {name} + {item_to_show.name}")
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
                           amount_in_cart=amount_in_cart)


@app.route('/add/<item_id>', methods=['GET', 'POST'])
def add(item_id):
    new_item = Item.query.get(item_id)
    new_item_url = quote_plus(new_item.name)
    if new_item.available:
        if item_id in session['cart_dict']:
            session['cart_dict'][item_id] += + 1
            session.modified = True
            new_item.available -= 1
            db.session.commit()
        else:
            session['cart_dict'][item_id] = 1
            session.modified = True
            new_item.available -= 1
            db.session.commit()
    else:
        # replace this print statement
        print("Out of stock")
    return redirect(url_for("item", name_url=new_item_url))


@app.route('/remove/<item_id>', methods=['GET', 'POST'])
def remove(item_id):
    item_to_remove = Item.query.get(item_id)
    item_to_remove_url = quote_plus(item_to_remove.name)
    if item_id in session['cart_dict'].keys():
        if session['cart_dict'][item_id] > 1:
            session['cart_dict'][item_id] -= 1
            session.modified = True
            item_to_remove.available += 1
            db.session.commit()
        else:
            del session['cart_dict'][item_id]
            session.modified = True
            item_to_remove.available += 1
            db.session.commit()
    return redirect(url_for("item", name_url=item_to_remove_url))


@app.route('/cart')
def cart():
    if 'cart_dict' not in session:
        session['cart_dict'] = {}
    item_list = []
    for item_id in session['cart_dict']:
        item = Item.query.get(item_id)
        # item_dict[quote_plus(item.name)] = item
        item.url = quote_plus(item.name)
        item_list.append(item)
        # item_list.append(Item.query.get(item_id))
        print(session['cart_dict'])
    return render_template('cart.html', cart_dict=session['cart_dict'], items=item_list)


@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    if request.method == 'POST':
        pass
        # checkout process
        # checkout process goes here
        return redirect()
    return render_template('checkout.html')


@app.route('/checkout_complete')
def checkout_complete():
    return render_template('checkout_complete.html')


if __name__ == '__main__':
    app.run(debug=True)