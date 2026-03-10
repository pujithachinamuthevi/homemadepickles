from flask import Flask, render_template, request, redirect, url_for, session, flash
import hashlib
from datetime import datetime
from functools import wraps
import random

app = Flask(__name__)
app.secret_key = 'homemade_pickles_secret_key_2024'

# ═══════════════════════════════════════════════════════
#   IN-MEMORY DATA STORE  (no database file needed)
# ═══════════════════════════════════════════════════════

def _hash(pw):
    return hashlib.sha256(pw.encode()).hexdigest()

# ── Users  { id -> dict } ───────────────────────────────
users = {
    1: {'id':1,'name':'Admin','email':'admin@pickles.com',
        'password':_hash('admin123'),'is_admin':True,
        'created_at':'2024-01-01 00:00:00'}
}
_next_user_id = [2]          # mutable so inner functions can modify

# ── Products  { id -> dict } ───────────────────────────
products = {
    1: {'id':1,'name':'Mango Pickle',  'category':'Pickles','price':149.00,'stock':100,
        'image':'mango_pickle.jpg',
        'description':'Sun-dried raw mangoes blended with mustard seeds, red chilli, and sesame oil. A classic South Indian recipe passed down through generations.'},
    2: {'id':2,'name':'Lemon Pickle',  'category':'Pickles','price':129.00,'stock':100,
        'image':'lemon_pickle.jpg',
        'description':'Tangy lemon pieces marinated in salt, turmeric, and a medley of aromatic spices. Perfect with rice or roti.'},
    3: {'id':3,'name':'Garlic Pickle', 'category':'Pickles','price':159.00,'stock':100,
        'image':'garlic_pickle.jpg',
        'description':'Whole garlic cloves slow-pickled in mustard oil with fenugreek and red chilli for a bold, pungent flavor.'},
    4: {'id':4,'name':'Gongura Pickle','category':'Pickles','price':169.00,'stock':100,
        'image':'gongura_pickle.jpg',
        'description':'Made from fresh sorrel leaves (gongura) sauteed with green chillies and tempered spices. An Andhra specialty.'},
    5: {'id':5,'name':'Murukku',       'category':'Snacks', 'price':89.00, 'stock':100,
        'image':'murukku.jpg',
        'description':'Crispy spiral snacks made from rice flour and urad dal, seasoned with cumin and sesame seeds. Crunchy perfection!'},
    6: {'id':6,'name':'Banana Chips',  'category':'Snacks', 'price':79.00, 'stock':100,
        'image':'banana_chips.jpg',
        'description':'Thin-sliced raw bananas fried to golden crisp in coconut oil with a hint of salt and turmeric.'},
    7: {'id':7,'name':'Mixture',       'category':'Snacks', 'price':99.00, 'stock':100,
        'image':'mixture.jpg',
        'description':'A festive blend of fried lentils, peanuts, curry leaves, and spiced sev. The ultimate tea-time companion.'},
    8: {'id':8,'name':'Chekkalu',      'category':'Snacks', 'price':85.00, 'stock':100,
        'image':'chekkalu.jpg',
        'description':'Traditional rice crackers flavored with sesame, peanuts and curry leaves. Light, crispy and addictive!'},
    9: {'id':9,'name':'Boondi Laddu',  'category':'Snacks', 'price':199.00,'stock':100,
        'image':'boondi_laddu.jpg',
        'description':'Round, golden sweets made from gram flour pearls bound with jaggery syrup, cardamom and cashews. Festive favorite.'},
}
_next_product_id = [10]

# ── Orders  { id -> dict } ─────────────────────────────
orders = {}
_next_order_id = [1]

# ── Contacts  [ dict ] ─────────────────────────────────
contacts = []


# ═══════════════════════════════════════════════════════
#   HELPER FUNCTIONS
# ═══════════════════════════════════════════════════════

def cart_count():
    return sum(v['qty'] for v in session.get('cart', {}).values())

def cart_total():
    return sum(v['qty'] * v['price'] for v in session.get('cart', {}).values())

def find_user(email):
    for u in users.values():
        if u['email'] == email:
            return u
    return None

def get_product(pid):
    return products.get(int(pid))

def get_all_products(category='All'):
    lst = list(products.values())
    if category and category != 'All':
        lst = [p for p in lst if p['category'] == category]
    return sorted(lst, key=lambda p: (p['category'], p['name']))

def user_orders(uid):
    return sorted([o for o in orders.values() if o['user_id'] == uid],
                  key=lambda o: o['order_date'], reverse=True)

app.jinja_env.globals.update(cart_count=cart_count, cart_total=cart_total)


# ═══════════════════════════════════════════════════════
#   ADMIN DECORATOR
# ═══════════════════════════════════════════════════════

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('is_admin'):
            flash('Admin access required.', 'danger')
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated


# ═══════════════════════════════════════════════════════
#   PUBLIC ROUTES
# ═══════════════════════════════════════════════════════

@app.route('/')
def index():
    all_p   = list(products.values())
    featured = random.sample(all_p, min(6, len(all_p)))
    pickles  = [p for p in all_p if p['category']=='Pickles'][:4]
    snacks   = [p for p in all_p if p['category']=='Snacks'][:4]
    return render_template('index.html', featured=featured, pickles=pickles, snacks=snacks)


@app.route('/products')
def products_page():
    category = request.args.get('category', 'All')
    prods = get_all_products(category)
    return render_template('products.html', products=prods, selected_category=category)


@app.route('/product/<int:pid>')
def product_detail(pid):
    product = get_product(pid)
    if not product:
        flash('Product not found.', 'danger')
        return redirect(url_for('products_page'))
    related = [p for p in products.values()
               if p['category'] == product['category'] and p['id'] != pid][:4]
    return render_template('product_detail.html', product=product, related=related)


@app.route('/cart')
def cart():
    items = [{'id':pid,'name':v['name'],'price':v['price'],'qty':v['qty'],
              'image':v.get('image',''),'subtotal':v['price']*v['qty']}
             for pid,v in session.get('cart',{}).items()]
    return render_template('cart.html', cart_items=items)


@app.route('/add-to-cart', methods=['POST'])
def add_to_cart():
    pid = str(request.form.get('product_id'))
    qty = int(request.form.get('quantity', 1))
    product = get_product(pid)
    if not product:
        flash('Product not found.', 'danger')
        return redirect(url_for('products_page'))
    cart = session.get('cart', {})
    if pid in cart:
        cart[pid]['qty'] += qty
    else:
        cart[pid] = {'name':product['name'],'price':product['price'],
                     'qty':qty,'image':product['image']}
    session['cart'] = cart
    flash(f'"{product["name"]}" added to cart!', 'success')
    return redirect(request.referrer or url_for('products_page'))


@app.route('/update-cart', methods=['POST'])
def update_cart():
    pid = str(request.form.get('product_id'))
    qty = int(request.form.get('quantity', 1))
    cart = session.get('cart', {})
    if pid in cart:
        if qty <= 0:
            del cart[pid]
        else:
            cart[pid]['qty'] = qty
    session['cart'] = cart
    return redirect(url_for('cart'))


@app.route('/remove-from-cart/<pid>')
def remove_from_cart(pid):
    cart = session.get('cart', {})
    cart.pop(str(pid), None)
    session['cart'] = cart
    flash('Item removed from cart.', 'info')
    return redirect(url_for('cart'))


@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    if 'user_id' not in session:
        flash('Please login to checkout.', 'warning')
        return redirect(url_for('login'))
    cart = session.get('cart', {})
    if not cart:
        flash('Your cart is empty.', 'warning')
        return redirect(url_for('cart'))

    if request.method == 'POST':
        oid = _next_order_id[0]
        _next_order_id[0] += 1
        items = [{'product_id':int(pid),'name':v['name'],'quantity':v['qty'],
                  'price':v['price'],'image':v.get('image','')}
                 for pid,v in cart.items()]
        orders[oid] = {
            'id': oid,
            'user_id':    session['user_id'],
            'user_name':  session['user_name'],
            'user_email': users.get(session['user_id'],{}).get('email',''),
            'total_price': cart_total(),
            'status':     'Pending',
            'order_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'items':      items,
            'item_count': len(items)
        }
        session['cart'] = {}
        flash(f'Order #{oid} placed successfully! 🎉', 'success')
        return redirect(url_for('order_success', oid=oid))

    return render_template('checkout.html', cart=cart)


@app.route('/order-success/<int:oid>')
def order_success(oid):
    return render_template('order_success.html', oid=oid)


@app.route('/my-orders')
def my_orders():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('my_orders.html', orders=user_orders(session['user_id']))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = find_user(request.form['email'])
        if user and user['password'] == _hash(request.form['password']) and not user['is_admin']:
            session['user_id']   = user['id']
            session['user_name'] = user['name']
            flash(f'Welcome back, {user["name"]}!', 'success')
            return redirect(url_for('index'))
        flash('Invalid email or password.', 'danger')
    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name     = request.form['name']
        email    = request.form['email']
        password = _hash(request.form['password'])
        if find_user(email):
            flash('Email already registered.', 'danger')
            return render_template('register.html')
        uid = _next_user_id[0]
        _next_user_id[0] += 1
        users[uid] = {'id':uid,'name':name,'email':email,'password':password,
                      'is_admin':False,
                      'created_at':datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        flash('Account created! Please login.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')


@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('user_name', None)
    flash('Logged out successfully.', 'info')
    return redirect(url_for('index'))


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        contacts.append({'name':request.form['name'],'email':request.form['email'],
                         'message':request.form['message'],
                         'created_at':datetime.now().strftime('%Y-%m-%d %H:%M:%S')})
        flash('Thank you! We will get back to you soon.', 'success')
        return redirect(url_for('contact'))
    return render_template('contact.html')


# ═══════════════════════════════════════════════════════
#   ADMIN ROUTES
# ═══════════════════════════════════════════════════════

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        user = find_user(request.form['email'])
        if user and user['password'] == _hash(request.form['password']) and user['is_admin']:
            session['is_admin']   = True
            session['admin_name'] = user['name']
            return redirect(url_for('admin_dashboard'))
        flash('Invalid admin credentials.', 'danger')
    return render_template('admin_login.html')


@app.route('/admin/logout')
def admin_logout():
    session.pop('is_admin', None)
    session.pop('admin_name', None)
    return redirect(url_for('admin_login'))


@app.route('/admin')
@admin_required
def admin_dashboard():
    regular = [u for u in users.values() if not u['is_admin']]
    revenue = sum(o['total_price'] for o in orders.values())
    recent  = sorted(orders.values(), key=lambda o: o['order_date'], reverse=True)[:5]
    stats   = {'products':len(products),'orders':len(orders),
               'users':len(regular),'revenue':revenue}
    return render_template('admin_dashboard.html', stats=stats, recent_orders=recent)


@app.route('/admin/products')
@admin_required
def admin_products():
    prods = sorted(products.values(), key=lambda p: (p['category'], p['name']))
    return render_template('admin_products.html', products=prods)


@app.route('/admin/add-product', methods=['GET', 'POST'])
@admin_required
def add_product():
    if request.method == 'POST':
        pid = _next_product_id[0]
        _next_product_id[0] += 1
        products[pid] = {
            'id':pid,'name':request.form['name'],'category':request.form['category'],
            'price':float(request.form['price']),'description':request.form['description'],
            'image':request.form['image'],'stock':100
        }
        flash('Product added successfully!', 'success')
        return redirect(url_for('admin_products'))
    return render_template('add_product.html')


@app.route('/admin/edit-product/<int:pid>', methods=['GET', 'POST'])
@admin_required
def edit_product(pid):
    product = get_product(pid)
    if not product:
        flash('Product not found.', 'danger')
        return redirect(url_for('admin_products'))
    if request.method == 'POST':
        products[pid].update({
            'name':request.form['name'],'category':request.form['category'],
            'price':float(request.form['price']),'description':request.form['description'],
            'image':request.form['image']
        })
        flash('Product updated!', 'success')
        return redirect(url_for('admin_products'))
    return render_template('edit_product.html', product=product)


@app.route('/admin/delete-product/<int:pid>')
@admin_required
def delete_product(pid):
    products.pop(pid, None)
    flash('Product deleted.', 'info')
    return redirect(url_for('admin_products'))


@app.route('/admin/orders')
@admin_required
def admin_orders():
    all_orders = sorted(orders.values(), key=lambda o: o['order_date'], reverse=True)
    return render_template('admin_orders.html', orders=all_orders)


@app.route('/admin/order/<int:oid>')
@admin_required
def admin_order_detail(oid):
    order = orders.get(oid)
    if not order:
        flash('Order not found.', 'danger')
        return redirect(url_for('admin_orders'))
    return render_template('admin_order_detail.html', order=order, items=order['items'])


@app.route('/admin/update-order-status/<int:oid>', methods=['POST'])
@admin_required
def update_order_status(oid):
    if oid in orders:
        orders[oid]['status'] = request.form['status']
        flash('Order status updated.', 'success')
    return redirect(url_for('admin_order_detail', oid=oid))


@app.route('/admin/users')
@admin_required
def admin_users():
    regular = sorted([u for u in users.values() if not u['is_admin']],
                     key=lambda u: u['created_at'], reverse=True)
    return render_template('admin_users.html', users=regular)


# ═══════════════════════════════════════════════════════
if __name__ == '__main__':
    app.run(debug=True)
