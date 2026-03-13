import os
import markdown

from functools import lru_cache
from flask import Blueprint, render_template, send_from_directory, abort, make_response

from ..models import Paper
from ..config import get_docs_folder, get_research_folder

content_bp = Blueprint("content", __name__)


@lru_cache(maxsize=1)
def load_docs():
    docs_list   = []
    docs_folder = get_docs_folder()

    if not os.path.exists(docs_folder):
        return docs_list

    for filename in sorted(os.listdir(docs_folder)):
        if not filename.endswith(".md"):
            continue

        file_id  = filename[:-3]
        filepath = os.path.join(docs_folder, filename)

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
        except (OSError, UnicodeDecodeError) as e:
            print(f"Warning: Skipping {filepath}: {e}")
            continue

    return docs_list


@content_bp.route("/docs")
def docs():
    docs_list = load_docs()
    response  = make_response(render_template("docs.html", docs=docs_list))
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

    # Reject absolute paths and parent-directory traversal
    if os.path.isabs(safe) or safe.startswith(".."):
        abort(400)

    research_folder = get_research_folder()
    full_path = os.path.join(research_folder, safe)

    if not os.path.isfile(full_path):
        abort(404)

    response = send_from_directory(research_folder, safe, as_attachment=False)
    response.headers["Cache-Control"] = "public, max-age=31536000, immutable"
    return response