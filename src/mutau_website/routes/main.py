from flask import Blueprint, render_template, request, flash, redirect, url_for,jsonify
from flask_login import login_required, current_user
import requests
import os

from ..extensions import db
from ..models import Product, Offer

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def index():
    return render_template("index.html")

# ai features test
@main_bp.route("/ai/chat", methods=["POST"])
def ai_chat_api():
    try:
        data = request.get_json()
        prompt = data.get("message", "").strip()
        
        if not prompt:
            return jsonify({"error": "Keine Nachricht"}), 400
        
        # ✅ Linux Docker Gateway IP (100% funktioniert)
        ollama_url = "http://172.17.0.1:11434/api/chat"  # ← STATT host.docker.internal!
        
        payload = {
            "model": "qwen3.5:0.8b",
            "messages": [{"role": "user", "content": prompt}],
            "stream": False
        }
        
        print(f"🟢 Verbinde mit Ollama: {ollama_url}")
        response = requests.post(ollama_url, json=payload, timeout=30)
        response.raise_for_status()
        
        result = response.json()
        ai_message = result.get("message", {}).get("content", "Keine Antwort")
        
        return jsonify({"response": ai_message})
        
    except Exception as e:
        print(f"❌ AI Error: {str(e)}")
        return jsonify({"error": f"AI-Service Fehler: {str(e)}"}), 500



@main_bp.route("/about")
def about():
    return render_template("about.html")


@main_bp.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        flash("Vielen Dank! Wir melden uns schnellstmöglich.", "success")
        return redirect(url_for("main.contact"))

    prefill_email = current_user.email if current_user.is_authenticated else ""
    return render_template("contact.html", prefill_email=prefill_email)


@main_bp.route("/offer", methods=["GET", "POST"])
@login_required
def offer():
    products   = Product.query.filter_by(is_active=True).all()
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