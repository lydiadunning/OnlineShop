from flask import Flask, render_template, redirect, request

# I don't fully understand why this web app requires a login.

class Item:
    # gets item info from ORM
    pass


app = Flask(__name__)
app.secret_key = "secret key"

# cart_dict is a placeholder for a session based shopping cart
cart_dict = {}

@app.route('/')
def home():
    return render_template('item_list.html', items=Item.query.filter_by(available=True).all())

@app.route('/<item_name>', methods=['GET', 'POST'])
def item(item_name):
    item = Item.query.filter_by(item_name=item_name).first()
    return render_template('item.html', item=item, available=item and item.available)

@app.route('/add/<link_back>/<item_id>', methods=['GET', 'POST'])
def add(link_back, item_id):
    new_item = Item.query.get(item_id)
    if cart_dict[item_id]:
        cart_dict[item_id] += 1
    else:
        cart_dict[item_id] = 1
    return redirect(link_back, item=new_item, available=item and item.available)

@app.route('/remove/<link_back>/<item_id>', methods=['GET', 'POST'])
def remove(link_back, item_id):
    item_to_remove = Item.query.get(item_id)
    if cart_dict[item_id] > 1:
        cart_dict[item_id] -= 1
    else:
        del cart_dict[item_id]
    return redirect(link_back, item=item_to_remove, available=item and item.available)

@app.route('/cart')
def cart():
    return render_template('cart.html', in_cart=cart_dict)

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