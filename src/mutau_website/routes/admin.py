import logging
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user

from ..extensions import db, admin_required
from ..models import User, Product, Paper, Offer

logger = logging.getLogger(__name__)
admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


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
    }
    recent_offers = (
        Offer.query
        .order_by(Offer.created_at.desc())
        .limit(5)
        .all()
    )
    return render_template("admin/dashboard.html", stats=stats, recent_offers=recent_offers)


# ── Products ───────────────────────────────────────────────────────────────

@admin_bp.route("/products")
@login_required
@admin_required
def products():
    all_products = Product.query.all()
    return render_template("admin/products.html", products=all_products)


# ── Papers ─────────────────────────────────────────────────────────────────

@admin_bp.route("/papers")
@login_required
@admin_required
def papers():
    all_papers = Paper.query.order_by(Paper.date.desc()).all()
    return render_template("admin/papers.html", papers=all_papers)


@admin_bp.route("/papers/<int:paper_id>/send-newsletter", methods=["POST"])
@login_required
@admin_required
def send_newsletter(paper_id):
    from ..mail import send_newsletter as _send_newsletter

    paper = Paper.query.get_or_404(paper_id)

    if paper.notified:
        flash("Newsletter für dieses Paper wurde bereits gesendet.", "warning")
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


@admin_bp.route("/offers/<int:offer_id>/mark-read", methods=["POST"])
@login_required
@admin_required
def mark_offer_read(offer_id):
    o = Offer.query.get_or_404(offer_id)
    if o.status == "new":
        o.status = "read"
        db.session.commit()
    return redirect(url_for("admin.offers"))


@admin_bp.route("/offers/<int:offer_id>/mark-answered", methods=["POST"])
@login_required
@admin_required
def mark_offer_answered(offer_id):
    o = Offer.query.get_or_404(offer_id)
    o.status = "answered"
    db.session.commit()
    return redirect(url_for("admin.offers"))


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