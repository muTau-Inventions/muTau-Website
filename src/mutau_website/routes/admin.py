import json
import logging
import os


from datetime import datetime
from werkzeug.utils import secure_filename
from flask import (
    Blueprint, render_template, redirect, url_for,
    flash, request, current_app, abort,
)
from flask_login import login_required, current_user


from ..extensions import db, admin_required
from ..models import User, Product, Paper, Offer, ContactMessage


logger = logging.getLogger(__name__)
admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


ALLOWED_EXTENSIONS = {"pdf"}



def _research_dir() -> str:
    return os.path.join(current_app.root_path, "..", "..", "research")



def _allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS



def _lines_to_json(text: str) -> str:
    """Convert newline-separated text to a JSON array string."""
    items = [line.strip() for line in text.splitlines() if line.strip()]
    return json.dumps(items, ensure_ascii=False)



def _json_to_lines(json_str: str) -> str:
    """Convert a JSON array string to newline-separated text."""
    try:
        return "\n".join(json.loads(json_str or "[]"))
    except Exception:
        return ""



# ── Dashboard ──────────────────────────────────────────────────────────────


@admin_bp.route("/")
@login_required
@admin_required
def dashboard():
    stats = {
        "users":          User.query.count(),
        "verified_users": User.query.filter_by(is_verified=True).count(),
        "newsletter":     User.query.filter_by(newsletter=True).count(),
        "products":       Product.query.filter_by(is_active=True).count(),
        "papers":         Paper.query.count(),
        "offers":         Offer.query.count(),
        "new_offers":     Offer.query.filter_by(status="new").count(),
        "papers_pending": Paper.query.filter_by(notified=False).count(),
        "unread_contact": ContactMessage.query.filter_by(read=False).count(),
    }
    recent_offers = (
        Offer.query
        .order_by(Offer.created_at.desc())
        .limit(5)
        .all()
    )
    recent_contacts = (
        ContactMessage.query
        .order_by(ContactMessage.created_at.desc())
        .limit(5)
        .all()
    )
    return render_template(
        "admin/dashboard.html",
        stats=stats,
        recent_offers=recent_offers,
        recent_contacts=recent_contacts,
    )



# ── Products ───────────────────────────────────────────────────────────────


@admin_bp.route("/products")
@login_required
@admin_required
def products():
    all_products = Product.query.order_by(Product.name).all()
    return render_template("admin/products.html", products=all_products)



@admin_bp.route("/products/<int:product_id>/toggle", methods=["POST"])
@login_required
@admin_required
def toggle_product(product_id):
    product = Product.query.get_or_404(product_id)
    product.is_active = not product.is_active
    db.session.commit()
    state = "aktiviert" if product.is_active else "deaktiviert"
    flash(f"Produkt „{product.name}“ wurde {state}.", "success")
    return redirect(url_for("admin.products"))



@admin_bp.route("/products/<int:product_id>/edit", methods=["GET", "POST"])
@login_required
@admin_required
def edit_product(product_id):
    product = Product.query.get_or_404(product_id)


    if request.method == "POST":
        product.name        = request.form.get("name", "").strip()
        product.description = request.form.get("description", "").strip()
        product.icon        = request.form.get("icon", "").strip()
        product.features    = _lines_to_json(request.form.get("features", ""))
        product.specs       = _lines_to_json(request.form.get("specs", ""))
        product.support     = _lines_to_json(request.form.get("support", ""))


        if not product.name:
            flash("Name darf nicht leer sein.", "danger")
            return render_template("admin/product_form.html", product=product,
                                   features_text=request.form.get("features", ""),
                                   specs_text=request.form.get("specs", ""),
                                   support_text=request.form.get("support", ""))


        db.session.commit()
        logger.info("Admin %s updated product %d (%s)", current_user.email, product.id, product.slug)
        flash(f"Produkt „{product.name}“ gespeichert.", "success")
        return redirect(url_for("admin.products"))


    return render_template(
        "admin/product_form.html",
        product=product,
        features_text=_json_to_lines(product.features),
        specs_text=_json_to_lines(product.specs),
        support_text=_json_to_lines(product.support),
    )



# ── Papers ─────────────────────────────────────────────────────────────────


@admin_bp.route("/papers")
@login_required
@admin_required
def papers():
    all_papers = Paper.query.order_by(Paper.date.desc()).all()
    return render_template("admin/papers.html", papers=all_papers)



@admin_bp.route("/papers/new", methods=["GET", "POST"])
@login_required
@admin_required
def new_paper():
    if request.method == "POST":
        title       = request.form.get("title", "").strip()
        authors     = request.form.get("authors", "").strip()
        date_str    = request.form.get("date", "").strip()
        description = request.form.get("description", "").strip()
        pdf_file    = request.files.get("pdf_file")


        if not title:
            flash("Titel darf nicht leer sein.", "danger")
            return render_template("admin/paper_form.html", paper=None)


        if not pdf_file or not pdf_file.filename:
            flash("Bitte eine PDF-Datei hochladen.", "danger")
            return render_template("admin/paper_form.html", paper=None)


        if not _allowed_file(pdf_file.filename):
            flash("Nur PDF-Dateien sind erlaubt.", "danger")
            return render_template("admin/paper_form.html", paper=None)


        filename = secure_filename(pdf_file.filename)
        research_dir = _research_dir()
        os.makedirs(research_dir, exist_ok=True)
        pdf_file.save(os.path.join(research_dir, filename))


        date = None
        if date_str:
            try:
                date = datetime.strptime(date_str, "%Y-%m-%d").date()
            except ValueError:
                pass


        paper = Paper(
            pdf_path=filename,
            title=title,
            authors=authors,
            date=date,
            description=description,
        )
        db.session.add(paper)
        db.session.commit()


        logger.info("Admin %s created paper %d ('%s')", current_user.email, paper.id, paper.title)
        flash(f"Publikation „{paper.title}“ wurde hinzugefügt.", "success")
        return redirect(url_for("admin.papers"))


    return render_template("admin/paper_form.html", paper=None)



@admin_bp.route("/papers/<int:paper_id>/edit", methods=["GET", "POST"])
@login_required
@admin_required
def edit_paper(paper_id):
    paper = Paper.query.get_or_404(paper_id)


    if request.method == "POST":
        paper.title       = request.form.get("title", "").strip()
        paper.authors     = request.form.get("authors", "").strip()
        paper.description = request.form.get("description", "").strip()


        date_str = request.form.get("date", "").strip()
        if date_str:
            try:
                paper.date = datetime.strptime(date_str, "%Y-%m-%d").date()
            except ValueError:
                pass


        # Optional PDF replacement
        pdf_file = request.files.get("pdf_file")
        if pdf_file and pdf_file.filename:
            if not _allowed_file(pdf_file.filename):
                flash("Nur PDF-Dateien sind erlaubt.", "danger")
                return render_template("admin/paper_form.html", paper=paper)


            # Remove old file
            old_path = os.path.join(_research_dir(), paper.pdf_path)
            if os.path.isfile(old_path):
                try:
                    os.remove(old_path)
                except OSError:
                    logger.warning("Could not delete old PDF: %s", old_path)


            filename = secure_filename(pdf_file.filename)
            research_dir = _research_dir()
            os.makedirs(research_dir, exist_ok=True)
            pdf_file.save(os.path.join(research_dir, filename))
            paper.pdf_path = filename


        if not paper.title:
            flash("Titel darf nicht leer sein.", "danger")
            return render_template("admin/paper_form.html", paper=paper)


        db.session.commit()
        logger.info("Admin %s updated paper %d ('%s')", current_user.email, paper.id, paper.title)
        flash(f"Publikation „{paper.title}“ gespeichert.", "success")
        return redirect(url_for("admin.papers"))


    return render_template("admin/paper_form.html", paper=paper)



@admin_bp.route("/papers/<int:paper_id>/delete", methods=["POST"])
@login_required
@admin_required
def delete_paper(paper_id):
    paper = Paper.query.get_or_404(paper_id)
    title = paper.title


    # Remove PDF file
    pdf_path = os.path.join(_research_dir(), paper.pdf_path)
    if os.path.isfile(pdf_path):
        try:
            os.remove(pdf_path)
        except OSError:
            logger.warning("Could not delete PDF file: %s", pdf_path)


    db.session.delete(paper)
    db.session.commit()
    logger.info("Admin %s deleted paper %d ('%s')", current_user.email, paper_id, title)
    flash(f"Publikation „{title}“ wurde gelöscht.", "success")
    return redirect(url_for("admin.papers"))



@admin_bp.route("/papers/<int:paper_id>/send-newsletter", methods=["POST"])
@login_required
@admin_required
def send_newsletter(paper_id):
    from ..mail import send_newsletter as _send_newsletter


    paper = Paper.query.get_or_404(paper_id)


    if paper.notified:
        flash("Newsletter für diese Publikation wurde bereits gesendet.", "warning")
        return redirect(url_for("admin.papers"))


    subscribers = User.query.filter_by(newsletter=True, is_verified=True).all()
    if not subscribers:
        flash("Keine Newsletter-Abonnenten vorhanden.", "warning")
        return redirect(url_for("admin.papers"))


    pdf_url      = url_for("content.research_pdf", filename=paper.pdf_path, _external=True)
    research_url = url_for("content.research", _external=True)


    _send_newsletter(subscribers, paper, pdf_url=pdf_url, research_url=research_url)


    paper.notified = True
    db.session.commit()


    logger.info("Newsletter sent for paper %d ('%s') by admin %s", paper_id, paper.title, current_user.email)
    flash(f"Newsletter an {len(subscribers)} Abonnenten gesendet.", "success")
    return redirect(url_for("admin.papers"))



# ── Offers ─────────────────────────────────────────────────────────────────


@admin_bp.route("/offers")
@login_required
@admin_required
def offers():
    status_filter = request.args.get("status", "")
    q = Offer.query.order_by(Offer.created_at.desc())
    if status_filter in ("new", "read", "answered"):
        q = q.filter_by(status=status_filter)
    all_offers = q.all()
    return render_template("admin/offers.html", offers=all_offers, status_filter=status_filter)



@admin_bp.route("/offers/<int:offer_id>")
@login_required
@admin_required
def offer_detail(offer_id):
    offer = Offer.query.get_or_404(offer_id)
    if offer.status == "new":
        offer.status = "read"
        db.session.commit()
    return render_template("admin/offer_detail.html", offer=offer)



@admin_bp.route("/offers/<int:offer_id>/mark-answered", methods=["POST"])
@login_required
@admin_required
def mark_offer_answered(offer_id):
    offer = Offer.query.get_or_404(offer_id)
    offer.status = "answered"
    db.session.commit()
    return redirect(request.referrer or url_for("admin.offers"))



@admin_bp.route("/offers/<int:offer_id>/delete", methods=["POST"])
@login_required
@admin_required
def delete_offer(offer_id):
    offer = Offer.query.get_or_404(offer_id)
    db.session.delete(offer)
    db.session.commit()
    flash("Anfrage wurde gelöscht.", "success")
    return redirect(url_for("admin.offers"))



# ── Contact messages ───────────────────────────────────────────────────────


@admin_bp.route("/contact")
@login_required
@admin_required
def contact_messages():
    show_all = request.args.get("all") == "1"
    q = ContactMessage.query.order_by(ContactMessage.created_at.desc())
    if not show_all:
        q = q.filter_by(read=False)
    messages = q.all()
    return render_template("admin/contact_messages.html", messages=messages, show_all=show_all)



@admin_bp.route("/contact/<int:msg_id>/read", methods=["POST"])
@login_required
@admin_required
def mark_contact_read(msg_id):
    msg = ContactMessage.query.get_or_404(msg_id)
    msg.read = True
    db.session.commit()
    return redirect(request.referrer or url_for("admin.contact_messages"))



@admin_bp.route("/contact/<int:msg_id>/delete", methods=["POST"])
@login_required
@admin_required
def delete_contact(msg_id):
    msg = ContactMessage.query.get_or_404(msg_id)
    db.session.delete(msg)
    db.session.commit()
    flash("Nachricht gelöscht.", "success")
    return redirect(url_for("admin.contact_messages"))



# ── Users ──────────────────────────────────────────────────────────────────


@admin_bp.route("/users")
@login_required
@admin_required
def users():
    all_users = User.query.order_by(User.created_at.desc()).all()
    return render_template("admin/users.html", users=all_users)



@admin_bp.route("/users/<int:user_id>/toggle-admin", methods=["POST"])
@login_required
@admin_required
def toggle_admin(user_id):
    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        flash("Du kannst deinen eigenen Admin-Status nicht ändern.", "warning")
        return redirect(url_for("admin.users"))
    user.is_admin = not user.is_admin
    db.session.commit()
    state = "zum Admin ernannt" if user.is_admin else "als Admin entfernt"
    flash(f"{user.name} wurde {state}.", "success")
    return redirect(url_for("admin.users"))



@admin_bp.route("/users/<int:user_id>/resend-verification", methods=["POST"])
@login_required
@admin_required
def resend_verification(user_id):
    import secrets
    from datetime import timedelta
    from ..models import EmailVerificationToken
    from ..mail import send_verification_email


    user = User.query.get_or_404(user_id)
    if user.is_verified:
        flash(f"{user.name} ist bereits verifiziert.", "info")
        return redirect(url_for("admin.users"))


    token_str = secrets.token_urlsafe(48)
    token = EmailVerificationToken(
        token=token_str,
        user_id=user.id,
        expires_at=datetime.now(user.created_at.tzinfo) + timedelta(hours=24),
    )
    db.session.add(token)
    db.session.commit()


    from datetime import timezone
    from flask import url_for as _url_for
    verify_url = _url_for("auth.verify_email", token=token_str, _external=True)
    send_verification_email(user, verify_url)


    flash(f"Bestätigungsmail an {user.email} gesendet.", "success")
    return redirect(url_for("admin.users"))



@admin_bp.route("/users/<int:user_id>/delete", methods=["POST"])
@login_required
@admin_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        flash("Du kannst deinen eigenen Account hier nicht löschen.", "warning")
        return redirect(url_for("admin.users"))
    db.session.delete(user)
    db.session.commit()
    logger.info("Admin %s deleted user %d (%s)", current_user.email, user_id, user.email)
    flash(f"Nutzer {user.name} wurde gelöscht.", "success")
    return redirect(url_for("admin.users"))
