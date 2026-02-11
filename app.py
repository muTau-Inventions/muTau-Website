import os
import json
import markdown
from flask import (
    Flask, render_template, session, redirect, url_for,
    request, flash, jsonify, send_from_directory
)
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'supersecretkey_fuer_mutau_demo'  # In Produktion ändern!

DOCS_FOLDER = "docs"

# ---------- MOCK-DATENBANK ----------
mock_users = {
    'admin@mutau.com': {
        'password': generate_password_hash('admin123'),
        'name': 'Admin User'
    }
}
mock_orders = []

# ---------- LOGIN-DEKORATOR ----------
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            flash('Bitte melde dich an, um diese Seite zu sehen.', 'warning')
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

# Produktdatenbank (hartcodiert für Demo)
PRODUCTS = {
    'converter': {
        'id': 'converter',
        'name': 'muTau Converter',
        'price': 2499,
        'icon': '🔄',
        'description': 'Konvertiert KI-Modelle in optimierten HLS-Code.',
        'features': [
            'Multi-Framework Support: TensorFlow, PyTorch, ONNX, Keras',
            'Automatische Optimierung: Intelligente Layer-Fusion und Pipeline-Optimierung',
            'Quantisierung: INT8, INT16, Fixed-Point mit adaptiven Strategien',
            'Batch Processing: Konvertieren Sie mehrere Modelle parallel',
            'CLI & Python API: Flexible Integration in Ihren Workflow',
            'Custom Layer Support: Erweitern Sie mit eigenen Layer-Definitionen'
        ],
        'specs': [
            'Unterstützte FPGAs: Xilinx Zynq, UltraScale+, Versal; Intel Stratix, Arria',
            'HLS Versionen: Vivado HLS 2020.1+, Vitis HLS 2021.1+',
            'Modell-Größe: Bis zu 500M Parameter',
            'Genauigkeit: 99%+ Original-Genauigkeit nach Konvertierung',
            'Performance: 2-5x schneller als manuelle Konvertierung',
            'Lizenz: Pro-User-Lizenz, unbegrenzte Projekte'
        ],
        'support': [
            'Dokumentation: Umfassende Online-Dokumentation und Tutorials',
            'Email Support: 24/7 Email-Support mit 24h Response-Zeit',
            'Updates: Kostenlose Updates für 12 Monate',
            'Community: Zugang zu unserem Developer-Forum',
            'Training: Online-Training-Sessions verfügbar'
        ]
    },
    'soc-builder': {
        'id': 'soc-builder',
        'name': 'muTau SoC Builder',
        'price': 3999,
        'icon': '⚙️',
        'description': 'Automatische Integration in SoC-Designs.',
        'features': [
            'AXI/Avalon Interfaces: Automatische Bus-Interface-Generierung',
            'DMA Integration: High-Performance DMA-Controller',
            'Memory Management: Optimierte DDR-Anbindung',
            'Interrupt Controller: Automatische Interrupt-Verwaltung',
            'Clock Domain Crossing: Automatische Synchronisation',
            'Power Management: Optimierte Stromsparmodi'
        ],
        'specs': [
            'Platforms: Xilinx Vivado, Intel Quartus Prime',
            'Lizenz: Enterprise-Lizenz',
            'Support für Zynq, Versal, Stratix 10',
            'Inkludiert 12 Monate Updates'
        ],
        'support': [
            'Priority Email Support: 12h Antwortzeit',
            'Telefon-Support während Geschäftszeiten',
            'Persönlicher Solutions Engineer'
        ]
    },
    'profiler': {
        'id': 'profiler',
        'name': 'muTau Profiler',
        'price': 1999,
        'icon': '📊',
        'description': 'Performance-Analyse und Optimierung.',
        'features': [
            'Detaillierte Latenz- und Durchsatzanalyse',
            'Ressourcenverbrauchs-Visualisierung',
            'Engpass-Identifikation',
            'Automatische Optimierungsvorschläge',
            'Export als HTML/PDF Reports',
            'Live-Monitoring während der Simulation'
        ],
        'specs': [
            'Integration in Vivado/Vitis und Quartus',
            'Unterstützt alle gängigen Xilinx/Intel FPGAs',
            'Lizenz: Node-Locked oder Floating',
            'Datenbank-Backend für historische Analysen'
        ],
        'support': [
            'Email Support',
            'Zugang zur Profiler-Community',
            '6 Monate Updates'
        ]
    },
    'optimizer': {
        'id': 'optimizer',
        'name': 'muTau Optimizer',
        'price': 2799,
        'icon': '🎯',
        'description': 'KI-gestützte Design-Optimierung.',
        'features': [
            'Automatische Quantisierung mit minimalem Genauigkeitsverlust',
            'Pruning von überflüssigen Verbindungen',
            'Architektur-Suche (NAS) für FPGAs',
            'Trade-off-Analyse: Latenz vs. Ressourcen',
            'Compiler-optimierte Scheduling-Strategien',
            'Integration in den Converter-Workflow'
        ],
        'specs': [
            'Lernverfahren: Reinforcement Learning + genetische Algorithmen',
            'Optimierungsziele: Latenz, Durchsatz, Power, Ressourcen',
            'Export als optimiertes HLS-Modell',
            'Lizenz: Pro-User'
        ],
        'support': [
            'Email Support',
            'Zugang zu Optimizer-Modellen',
            '12 Monate Updates'
        ]
    }
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

# ---------- DOKUMENTATION ----------
@app.route("/docs")
def docs():

    docs_list = []

    for filename in sorted(os.listdir(DOCS_FOLDER)):

        if filename.endswith(".md"):

            file_id = filename.replace(".md", "")

            filepath = os.path.join(DOCS_FOLDER, filename)

            with open(filepath, "r", encoding="utf-8") as f:
                md_content = f.read()

            html_content = markdown.markdown(
                md_content,
                extensions=[
                    "extra",
                    "fenced_code",
                    "codehilite",
                    "toc"
                ]
            )

            docs_list.append({
                "id": file_id,
                "title": file_id.replace("-", " ").title(),
                "content": html_content
            })

    return render_template("docs.html", docs=docs_list)

@app.route('/docs_build/<path:filename>')
def docs_build(filename):
    return send_from_directory('docs_build', filename)

# ---------- STATISCHE SEITEN ----------
@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        # Mock: Email senden
        flash('Vielen Dank! Wir werden uns schnellstmöglich bei Ihnen melden.', 'success')
        return redirect(url_for('contact'))
    return render_template('contact.html')

# ---------- WARENKORB ----------
@app.route('/cart')
def cart():
    cart_items = session.get('cart', [])
    subtotal = sum(item['price'] * item['quantity'] for item in cart_items)
    tax = subtotal * 0.19
    total = subtotal + tax
    return render_template('cart.html', cart_items=cart_items,
                           subtotal=subtotal, tax=tax, total=total)

@app.route('/cart_count')
def cart_count():
    cart = session.get('cart', [])
    count = sum(item['quantity'] for item in cart)
    return jsonify({'count': count})

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
        cart.append({'name': name, 'price': price, 'icon': icon, 'quantity': 1})
    session['cart'] = cart
    flash(f'{name} wurde in den Warenkorb gelegt.', 'success')
    return redirect(request.referrer or url_for('products'))

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

@app.route('/remove_from_cart', methods=['POST'])
def remove_from_cart():
    name = request.form.get('name')
    cart = session.get('cart', [])
    session['cart'] = [item for item in cart if item['name'] != name]
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

    if request.method == 'POST':
        # Mock-Zahlung
        flash('Zahlung erfolgreich! Vielen Dank für Ihre Bestellung. (Mock)', 'success')
        session['cart'] = []
        return redirect(url_for('index'))
    
    return render_template('checkout.html', cart_items=cart_items,
                           subtotal=subtotal, tax=tax, total=total)

# ---------- AUTHENTIFIZIERUNG ----------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = mock_users.get(email)
        if user and check_password_hash(user['password'], password):
            session['user'] = email
            session['user_name'] = user['name']
            flash('Erfolgreich eingeloggt!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Ungültige E-Mail oder Passwort.', 'danger')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        confirm = request.form.get('confirm_password')
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        agb = request.form.get('agb')
        
        if not agb:
            flash('Bitte akzeptieren Sie die AGB.', 'danger')
        elif email in mock_users:
            flash('Diese E-Mail-Adresse ist bereits registriert.', 'danger')
        elif password != confirm:
            flash('Die Passwörter stimmen nicht überein.', 'danger')
        elif len(password) < 6:
            flash('Das Passwort muss mindestens 6 Zeichen lang sein.', 'danger')
        else:
            mock_users[email] = {
                'password': generate_password_hash(password),
                'name': f'{first_name} {last_name}'
            }
            flash('Registrierung erfolgreich! Du kannst dich jetzt einloggen.', 'success')
            return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    session.pop('user_name', None)
    session.pop('cart', None)  # Optional: Warenkorb leeren beim Logout
    flash('Du wurdest ausgeloggt.', 'info')
    return redirect(url_for('index'))

@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email')
        # Mock: E-Mail senden
        flash(f'Ein Link zum Zurücksetzen wurde an {email} gesendet (Mock).', 'info')
        return redirect(url_for('login'))
    return render_template('forgot_password.html')

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

# ---------- CLI-BEFEHL: DOKUMENTATION BAUEN ----------
@app.cli.command('build-docs')
def build_docs():
    """Führt MkDocs Build aus, um statische Dokumentation zu generieren."""
    import subprocess
    try:
        subprocess.run(['mkdocs', 'build', '-f', 'docs_source/mkdocs.yml', '-d', '../docs_build'],
                       cwd='docs_source', check=True)
        print('✅ Dokumentation erfolgreich in docs_build/ generiert.')
    except subprocess.CalledProcessError as e:
        print(f'❌ Fehler beim Generieren der Dokumentation: {e}')

if __name__ == '__main__':
    app.run(debug=True)