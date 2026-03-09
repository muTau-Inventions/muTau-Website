from flask import Blueprint, render_template
from flask_login import login_required

from ..extensions import admin_required
from ..models import User, Product, Paper, Offer

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


@admin_bp.route("/")
@login_required
@admin_required
def dashboard():
    stats = {
        "users":      User.query.count(),
        "products":   Product.query.filter_by(is_active=True).count(),
        "papers":     Paper.query.count(),
        "newsletter": User.query.filter_by(newsletter=True).count(),
        "offers":     Offer.query.count(),
        "new_offers": Offer.query.filter_by(status="new").count(),
    }
    return render_template("admin/dashboard.html", stats=stats)


@admin_bp.route("/products")
@login_required
@admin_required
def products():
    all_products = Product.query.all()
    return render_template("admin/products.html", products=all_products)


@admin_bp.route("/papers")
@login_required
@admin_required
def papers():
    all_papers = Paper.query.order_by(Paper.date.desc()).all()
    return render_template("admin/papers.html", papers=all_papers)


@admin_bp.route("/offers")
@login_required
@admin_required
def offers():
    all_offers = Offer.query.order_by(Offer.created_at.desc()).all()
    return render_template("admin/offers.html", offers=all_offers)


@admin_bp.route("/offers/<int:offer_id>/mark-read", methods=["POST"])
@login_required
@admin_required
def mark_offer_read(offer_id):
    from flask import redirect, url_for
    from ..extensions import db
    o = Offer.query.get_or_404(offer_id)
    o.status = "read"
    db.session.commit()
    return redirect(url_for("admin.offers"))


@admin_bp.route("/users")
@login_required
@admin_required
def users():
    all_users = User.query.order_by(User.created_at.desc()).all()
    return render_template("admin/users.html", users=all_users)