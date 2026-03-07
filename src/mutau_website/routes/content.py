import os
import markdown

from flask import Blueprint, render_template, send_from_directory, abort, current_app

from ..extensions import db
from ..models import Paper

content_bp = Blueprint("content", __name__)

DOCS_FOLDER   = "docs"
RESEARCH_FOLDER = "research"


# ── Docs ──────────────────────────────────────────────────────────────────────

@content_bp.route("/docs")
def docs():
    docs_list = []

    if not os.path.exists(DOCS_FOLDER):
        return render_template("docs.html", docs=docs_list)

    for filename in sorted(os.listdir(DOCS_FOLDER)):
        if not filename.endswith(".md"):
            continue

        file_id  = filename[:-3]  # strip .md
        filepath = os.path.join(DOCS_FOLDER, filename)

        try:
            with open(filepath, "r", encoding="utf-8") as f:
                md_content = f.read()
            html_content = markdown.markdown(
                md_content,
                extensions=["extra", "fenced_code", "codehilite", "toc"],
            )
            docs_list.append({
                "id":      file_id,
                "title":   file_id.replace("-", " ").title(),
                "content": html_content,
            })
        except OSError:
            continue

    return render_template("docs.html", docs=docs_list)


# ── Research ──────────────────────────────────────────────────────────────────

@content_bp.route("/research")
def research():
    papers = Paper.query.order_by(Paper.date.desc()).all()
    return render_template("research.html", papers=papers)


@content_bp.route("/research/pdf/<path:filename>")
def research_pdf(filename):
    # Prevent path traversal
    safe = os.path.normpath(filename)
    if safe.startswith(".."):
        abort(400)
    return send_from_directory(RESEARCH_FOLDER, safe)
