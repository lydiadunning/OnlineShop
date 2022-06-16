from flask import Flask, render_template, redirect, request, url_for
from flask_sqlalchemy import SQLAlchemy

# I don't fully understand why this web app requires a login.

app = Flask(__name__)
app.secret_key = "secret key"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///items.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Item(db.Model):
    # A single item for sale
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), unique=True, nullable=False)
    url = db.Column(db.String(20), unique=True, nullable=False)
    image = db.Column(db.String(20), nullable=False)
    price = db.Column(db.String(10), nullable=False)
    description = db.Column(db.String(200))
    available = db.Column(db.Integer)

db.create_all()


# cart_dict is a placeholder for a session based shopping cart
cart_dict = {}


@app.route('/')
def home():
    return render_template('item_list.html', items=Item.query.all())


@app.route('/<name_url>', methods=['GET', 'POST'])
def item(name_url):
    item_to_show = Item.query.filter_by(url=name_url).first()
    if item_to_show.id in cart_dict.keys():
        amount_in_cart = cart_dict[item_to_show.id]
    else:
        amount_in_cart = 0
    return render_template('item.html',
                           item=item_to_show,
                           available=item_to_show and item_to_show.available,
                           amount_in_cart=amount_in_cart)


@app.route('/add/<item_id>', methods=['GET', 'POST'])
def add(item_id):
    new_item = Item.query.get(item_id)
    if new_item.available:
        if int(item_id) in cart_dict.keys():
            cart_dict[int(item_id)] += 1
            new_item.available -= 1
            db.session.commit()
        else:
            cart_dict[int(item_id)] = 1
            new_item.available -= 1
            db.session.commit()
    else:
        # replace this print statement
        print("Out of stock")
    return redirect(url_for("item", name_url=new_item.url))


@app.route('/remove/<item_id>', methods=['GET', 'POST'])
def remove(item_id):
    id = int(item_id)
    item_to_remove = Item.query.get(id)
    if id in cart_dict.keys():
        if cart_dict[id] > 1:
            cart_dict[id] -= 1
            item_to_remove.available += 1
            db.session.commit()
        else:
            del cart_dict[id]
            item_to_remove.available += 1
            db.session.commit()
    return redirect(url_for("item", name_url=item_to_remove.url))


@app.route('/cart')
def cart():
    item_list = []
    for item_id in cart_dict.keys():
        item_list.append(Item.query.get(item_id))
    return render_template('cart.html', cart_dict=cart_dict, items=item_list)


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