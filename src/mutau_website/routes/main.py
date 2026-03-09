from flask import Blueprint, render_template, request, flash, redirect, url_for

from ..extensions import db
from ..models import Product, Offer

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
        flash("Vielen Dank! Wir melden uns schnellstmöglich.", "success")
        return redirect(url_for("main.contact"))
    return render_template("contact.html")


@main_bp.route("/offer", methods=["GET", "POST"])
def offer():
    products = Product.query.filter_by(is_active=True).all()
    preselected = request.args.get("product", "")

    if request.method == "POST":
        name             = request.form.get("name", "").strip()
        email            = request.form.get("email", "").strip()
        company          = request.form.get("company", "").strip()
        product_interest = request.form.get("product_interest", "").strip()
        message          = request.form.get("message", "").strip()

        if not name or not email or not message:
            flash("Bitte fülle alle Pflichtfelder aus.", "danger")
            return render_template("offer.html", products=products, preselected=preselected)

        try:
            o = Offer(
                name=name,
                email=email,
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