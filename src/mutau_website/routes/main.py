from flask import Blueprint, render_template, request, flash, redirect, url_for

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
        # Placeholder — wire up email via mail.py when SMTP is ready
        flash("Vielen Dank! Wir melden uns schnellstmöglich.", "success")
        return redirect(url_for("main.contact"))
    return render_template("contact.html")
