from flask import Blueprint, render_template, flash, redirect, url_for, abort

from ..models import Product

products_bp = Blueprint("products", __name__)


@products_bp.route("/products")
def products():
    all_products = Product.query.filter_by(is_active=True).all()
    return render_template("products.html", products=all_products)


@products_bp.route("/products/<slug>")
def product_detail(slug):
    product = Product.query.filter_by(slug=slug, is_active=True).first()
    if not product:
        flash("Produkt nicht gefunden.", "danger")
        return redirect(url_for("products.products"))
    return render_template("product_detail.html", product=product)
