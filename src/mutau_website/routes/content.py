import os
import markdown

from functools import lru_cache
from flask import Blueprint, render_template, send_from_directory, abort, make_response

from ..models import Paper

content_bp = Blueprint("content", __name__)

DOCS_FOLDER   = "/app/docs"
RESEARCH_FOLDER = "/app/research"


@lru_cache(maxsize=1)
def load_docs():
    docs_list = []

    if not os.path.exists(DOCS_FOLDER):
        return docs_list

    for filename in sorted(os.listdir(DOCS_FOLDER)):
        if not filename.endswith(".md"):
            continue

        file_id = filename[:-3]
        filepath = os.path.join(DOCS_FOLDER, filename)

        try:
            with open(filepath, "r", encoding="utf-8") as f:
                md_content = f.read()

            html_content = markdown.markdown(
                md_content,
                extensions=["extra", "fenced_code", "codehilite", "toc"],
            )
            docs_list.append({
                "id": file_id,
                "title": file_id.replace("-", " ").title(),
                "content": html_content,
            })
        except (OSError, UnicodeDecodeError) as e:
            print(f"Warning: Skipping {filepath}: {e}")
            continue

    return docs_list


@content_bp.route("/docs")
def docs():
    docs_list = load_docs()

    response = make_response(render_template("docs.html", docs=docs_list))
    response.headers["Cache-Control"] = "public, max-age=1800, stale-while-revalidate=900"
    response.headers["Vary"] = "Accept-Encoding"

    return response


@content_bp.route("/research")
def research():
    papers = Paper.query.order_by(Paper.date.desc()).all()
    return render_template("research.html", papers=papers)


@content_bp.route("/research/pdf/<path:filename>")
def research_pdf(filename):
    safe = os.path.normpath(filename)
    if safe.startswith(".."):
        abort(400)

    full_path = os.path.join(RESEARCH_FOLDER, safe)
    if not os.path.isfile(full_path):
        abort(404)

    response = send_from_directory(RESEARCH_FOLDER, safe, as_attachment=False)
    response.headers['Cache-Control'] = 'public, max-age=31536000, immutable'
    return response
