from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user

from ..extensions import db
from ..models import Product, Offer, ContactMessage

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def index():
    return render_template("index.html")


@main_bp.route("/about")
def about():
    return render_template("about.html")


@main_bp.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        name    = request.form.get("name", "").strip()
        email   = request.form.get("email", "").strip()
        subject = request.form.get("subject", "").strip()
        message = request.form.get("message", "").strip()

        if not name or not email or not message:
            flash("Bitte fülle alle Pflichtfelder aus.", "danger")
        else:
            try:
                msg = ContactMessage(
                    name=name,
                    email=email,
                    subject=subject or None,
                    message=message,
                )
                db.session.add(msg)
                db.session.commit()
                flash("Vielen Dank! Wir melden uns schnellstmöglich.", "success")
                return redirect(url_for("main.contact"))
            except Exception:
                db.session.rollback()
                flash("Ein Fehler ist aufgetreten. Bitte versuche es erneut.", "danger")

    prefill_name  = current_user.name  if current_user.is_authenticated else ""
    prefill_email = current_user.email if current_user.is_authenticated else ""
    return render_template("contact.html", prefill_name=prefill_name, prefill_email=prefill_email)


@main_bp.route("/offer", methods=["GET", "POST"])
@login_required
def offer():
    products    = Product.query.filter_by(is_active=True).all()
    preselected = request.args.get("product", "")

    if request.method == "POST":
        company          = request.form.get("company", "").strip()
        product_interest = request.form.get("product_interest", "").strip()
        message          = request.form.get("message", "").strip()

        if not message:
            flash("Bitte fülle alle Pflichtfelder aus.", "danger")
            return render_template("offer.html", products=products, preselected=preselected)

        try:
            o = Offer(
                user_id=current_user.id,
                name=current_user.name,
                email=current_user.email,
                company=company or None,
                product_interest=product_interest or None,
                message=message,
            )
            db.session.add(o)
            db.session.commit()
            flash("Ihre Anfrage wurde gesendet. Wir melden uns in Kürze.", "success")
            return redirect(url_for("main.offer"))
        except Exception:
            db.session.rollback()
            flash("Ein Fehler ist aufgetreten. Bitte versuche es erneut.", "danger")

    return render_template("offer.html", products=products, preselected=preselected)