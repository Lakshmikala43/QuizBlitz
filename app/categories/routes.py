from flask import Blueprint, render_template, abort
from app.repositories.question_repo import CategoryRepository

categories_bp = Blueprint("categories", __name__, url_prefix="/categories")
category_repo = CategoryRepository()


@categories_bp.route("/")
def list_categories():
    """Public/player view of all active quiz disciplines."""
    cats = category_repo.get_active_categories()
    return render_template("categories/list.html", categories=cats)


@categories_bp.route("/<slug>")
def view_category(slug):
    """Inspect category details and start customized quiz."""
    cat = category_repo.get_by_slug(slug)
    if not cat or not cat.is_active:
        abort(404)
    return render_template("categories/detail.html", category=cat)
