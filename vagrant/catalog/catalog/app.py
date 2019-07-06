# -*- coding: utf-8 -*-
"""Flask app for catalog server.

Written by Nikolaus Ruf
"""

from flask import Flask, redirect, url_for, flash, request
import logging


logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())
# log output is configured for the root logger in the startup script


# TODO: implement actual authentication
is_logged_in = True
user_name = "Niko"


app = Flask(
    __name__, static_folder="../static", template_folder="../templates"
)  # HTML and style files are outside the Python module


@app.route("/")
def serve_main_page():
    """Serve main page.

    :return: HTML code for page
    """
    return app.config["content"].render_main_page(
        is_logged_in=is_logged_in, user_name=user_name
    )


@app.route("/category/view/<int:id_>/")
def serve_category_page(id_):
    """Serve page for one category.

    :return: HTML code for page
    """
    page = app.config["content"].render_category_page(
        is_logged_in=is_logged_in, user_name=user_name, id_=id_
    )
    if page is not None:
        return page
    return redirect(url_for("serve_main_page"))


@app.route("/category/add/", methods=["GET", "POST"])
def serve_add_category_page():
    """Serve page for adding a category or handle POST request.

    :return: HTML code for page or redirect URK
    """
    if not is_logged_in:
        flash("You need to be logged in to edit content.")
        return redirect(url_for("serve_main_page"))
    if request.method == "GET":
        return app.config["content"].render_add_category_page(
            user_name=user_name
        )
    id_ = app.config["content"].add_category(
        request.form.get("name", type=str)
    )
    if id_ is None:
        return redirect(url_for("serve_main_page"))
    return redirect(url_for("serve_category_page", id_=id_))


@app.route("/category/edit/<int:id_>/", methods=["GET", "POST"])
def serve_edit_category_page(id_):
    """Serve page for editing a category or handle POST request.

    :return: HTML code for page or redirect URK
    """
    if not is_logged_in:
        flash("You need to be logged in to edit content.")
        return redirect(url_for("serve_main_page"))
    if request.method == "GET":
        return app.config["content"].render_edit_category_page(
            user_name=user_name, id_=id_
        )
    app.config["content"].edit_category(
        id_=id_, name=request.form.get("name", type=str)
    )
    return redirect(url_for("serve_category_page", id_=id_))


@app.route("/category/delete/<int:id_>/", methods=["GET", "POST"])
def serve_delete_category_page(id_):
    """Serve page for deleting a category or handle POST request.

    :return: HTML code for page or redirect URK
    """
    if not is_logged_in:
        flash("You need to be logged in to edit content.")
        return redirect(url_for("serve_main_page"))
    if request.method == "GET":
        return app.config["content"].render_delete_category_page(
            user_name=user_name, id_=id_
        )
    app.config["content"].delete_category(id_=id_)
    return redirect(url_for("serve_main_page"))


@app.route("/item/view/<int:id_>/")
def serve_item_page(id_):
    """Serve page for one item.

    :return: HTML code for page
    """
    page = app.config["content"].render_item_page(
        is_logged_in=is_logged_in, user_name=user_name, id_=id_
    )
    if page is not None:
        return page
    return redirect(url_for("serve_main_page"))
