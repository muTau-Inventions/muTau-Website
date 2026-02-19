import os
import json
import markdown
from functools import wraps

from flask import (
    Flask, render_template, session, redirect,
    url_for, request, flash, jsonify, send_from_directory
)

from flask_sqlalchemy import SQLAlchemy
from flask_login import (
    LoginManager, UserMixin,
    login_user, login_required,
    logout_user, current_user
)

from flask_bcrypt import Bcrypt


# ---------------- APP SETUP ----------------

app = Flask(__name__)

app.secret_key = os.environ.get("SECRET_KEY", os.urandom(24))

DATABASE_URL = os.environ.get("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL not set")


app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

DOCS_FOLDER = "docs"

# ---------------- LOGIN MANAGER ----------------

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


# ---------------- USER MODEL ----------------

class User(UserMixin, db.Model):

    id = db.Column(db.Integer, primary_key=True)

    email = db.Column(db.String(120), unique=True, nullable=False)

    password_hash = db.Column(db.String(255), nullable=False)

    name = db.Column(db.String(120))

    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode("utf-8")

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# ---------------- DB CREATE ----------------
with app.app_context():
    db.create_all()



# ---------------- LOGIN REQUIRED DECORATOR ----------------

def login_required_custom(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Bitte melde dich an.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


# ---------- RESEARCH-PAPIER-LADER ----------

def get_research_papers():
    papers = []
    base_dir = 'research'
    if not os.path.exists(base_dir):
        return papers

    for folder in os.listdir(base_dir):

        folder_path = os.path.join(base_dir, folder)

        info_path = os.path.join(folder_path, 'information.json')
        pdf_path = os.path.join(folder_path, 'paper.pdf')

        if os.path.isdir(folder_path) and os.path.exists(info_path) and os.path.exists(pdf_path):

            try:

                with open(info_path, 'r', encoding='utf-8') as f:
                    info = json.load(f)

                info['folder'] = folder
                info['pdf'] = url_for('research_pdf', filename=f'{folder}/paper.pdf')

                papers.append(info)

            except:
                continue

    return sorted(papers, key=lambda x: x.get('date', ''), reverse=True)


# ---------- ROUTEN ----------

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/research')
def research():
    papers = get_research_papers()
    return render_template('research.html', papers=papers)


@app.route('/research_pdf/<path:filename>')
def research_pdf(filename):
    return send_from_directory('research', filename)

@app.route('/about')
def about():
    return render_template('about.html')



# ---------- PRODUKTE ----------

PRODUCTS = {
    'converter': {'id': 'converter','name': 'muTau Converter','price': 2499,'icon': '🔄','description': 'Konvertiert KI-Modelle.'},
    'soc-builder': {'id': 'soc-builder','name': 'muTau SoC Builder','price': 3999,'icon': '⚙️','description': 'Automatische Integration.'},
    'profiler': {'id': 'profiler','name': 'muTau Profiler','price': 1999,'icon': '📊','description': 'Performance Analyse.'},
    'optimizer': {'id': 'optimizer','name': 'muTau Optimizer','price': 2799,'icon': '🎯','description': 'KI Optimierung.'}
}


@app.route('/products')
def products():
    return render_template('products.html', products=PRODUCTS)


@app.route('/product/<product_id>')
def product_detail(product_id):

    product = PRODUCTS.get(product_id)

    if not product:
        flash('Produkt nicht gefunden.', 'danger')
        return redirect(url_for('products'))

    return render_template('product_detail.html', product=product)


# ---------- DOCS ----------

@app.route("/docs")
def docs():

    docs_list = []

    for filename in sorted(os.listdir(DOCS_FOLDER)):

        if filename.endswith(".md"):

            file_id = filename.replace(".md", "")

            filepath = os.path.join(DOCS_FOLDER, filename)

            with open(filepath, "r", encoding="utf-8") as f:
                md_content = f.read()

            html_content = markdown.markdown(md_content, extensions=["extra","fenced_code","codehilite","toc"])

            docs_list.append({
                "id": file_id,
                "title": file_id.replace("-", " ").title(),
                "content": html_content
            })

    return render_template("docs.html", docs=docs_list)


# ---------- CART ----------

@app.route('/cart')
def cart():

    cart_items = session.get('cart', [])

    subtotal = sum(item['price'] * item['quantity'] for item in cart_items)
    tax = subtotal * 0.19
    total = subtotal + tax

    return render_template('cart.html', cart_items=cart_items,
                           subtotal=subtotal, tax=tax, total=total)


@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():

    name = request.form.get('name')
    price = float(request.form.get('price'))
    icon = request.form.get('icon')

    cart = session.get('cart', [])

    found = False

    for item in cart:

        if item['name'] == name:
            item['quantity'] += 1
            found = True
            break

    if not found:
        cart.append({'name': name,'price': price,'icon': icon,'quantity': 1})

    session['cart'] = cart

    flash(f'{name} wurde in den Warenkorb gelegt.', 'success')

    return redirect(request.referrer or url_for('products'))


# ---------- AUTH ----------
@app.route('/register', methods=['GET','POST'])
def register():
    print("🔍 === REGISTER DEBUG START ===")
    
    if request.method == 'POST':
        print(f"📋 FORM DATA: {dict(request.form)}")
        
        email = request.form.get('email')
        password = request.form.get('password')
        confirm = request.form.get('confirm_password')
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        agb = request.form.get('agb') 

        print(f"AGB: '{agb}' (should be 'on')")
        print(f"Passwords match: {password == confirm}")
        print(f"Email exists: {User.query.filter_by(email=email).first()}")
        
        if not agb:
            print("AGB missing!")
            flash("Bitte akzeptiere die AGB.", "danger")
            return redirect(url_for('register'))

        if password != confirm:
            print("Passwords don't match!")
            flash("Die Passwörter stimmen nicht überein.", "danger")
            return redirect(url_for('register'))

        if User.query.filter_by(email=email).first():
            print("Email exists!")
            flash("Diese Email existiert bereits", "danger")
            return redirect(url_for('register'))

        print("Creating user...")
        try:
            user = User(email=email, name=f"{first_name} {last_name}")
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            print("User created successfully!")
            flash("Registrierung erfolgreich", "success")
            return redirect(url_for('login'))
        except Exception as e:
            print(f"DB ERROR: {e}")
            db.session.rollback()
            flash("Datenbankfehler. Bitte versuche es erneut.", "danger")
            return redirect(url_for('register'))

    print("GET request - showing form")
    return render_template('register.html')




@app.route('/login', methods=['GET','POST'])
def login():

    if request.method == 'POST':

        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):

            login_user(user)

            flash("Login erfolgreich", "success")

            return redirect(url_for('index'))

        flash("Login fehlgeschlagen", "danger")

    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():

    logout_user()

    session.pop('cart', None)

    flash("Du wurdest ausgeloggt", "info")

    return redirect(url_for('index'))

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        # Mock: Email senden
        flash('Vielen Dank! Wir werden uns schnellstmöglich bei Ihnen melden.', 'success')
        return redirect(url_for('contact'))
    return render_template('contact.html')

@app.route('/cart_count')
def cart_count():
    cart = session.get('cart', [])
    count = sum(item['quantity'] for item in cart)
    return jsonify({'count': count})

@app.route('/update_cart', methods=['POST'])
def update_cart():
    name = request.form.get('name')
    change = int(request.form.get('change', 0))
    cart = session.get('cart', [])
    for item in cart:
        if item['name'] == name:
            item['quantity'] += change
            if item['quantity'] <= 0:
                cart.remove(item)
            break
    session['cart'] = cart
    return redirect(url_for('cart'))

# ---------- CHECKOUT (MOCK) ----------
@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    cart_items = session.get('cart', [])
    if not cart_items:
        flash('Ihr Warenkorb ist leer.', 'info')
        return redirect(url_for('cart'))
    
    subtotal = sum(item['price'] * item['quantity'] for item in cart_items)
    tax = subtotal * 0.19
    total = subtotal + tax

@app.route('/remove_from_cart', methods=['POST'])
def remove_from_cart():
    name = request.form.get('name')
    cart = session.get('cart', [])
    session['cart'] = [item for item in cart if item['name'] != name]
    return redirect(url_for('cart'))


# ---------- RECHTLICHES ----------
@app.route('/impressum')
def impressum():
    return render_template('impressum.html')

@app.route('/datenschutz')
def datenschutz():
    return render_template('datenschutz.html')

@app.route('/agb')
def agb():
    return render_template('agb.html')

@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email')
        # Mock: E-Mail senden
        flash(f'Ein Link zum Zurücksetzen wurde an {email} gesendet (Mock).', 'info')
        return redirect(url_for('login'))
    return render_template('forgot_password.html')

# ---------- START ----------

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)