# -*- coding: utf-8 -*-
"""Flask app for catalog server.

Written by Nikolaus Ruf
"""

from flask import Flask, redirect, url_for, flash, request


# TODO: implement actual authentication
is_logged_in = True
user_name = "Niko"


app = Flask(
    __name__, static_folder="../static", template_folder="../templates"
)  # HTML and style files are outside the Python module directory


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

    :return: HTML code for page or redirect URL
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

    :return: HTML code for page or redirect URL
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

    :param id_: integer; category ID
    :return: HTML code for page or redirect URL
    """
    if not is_logged_in:
        flash("You need to be logged in to edit content.")
        return redirect(url_for("serve_main_page"))
    if request.method == "GET":
        page = app.config["content"].render_edit_category_page(
            user_name=user_name, id_=id_
        )
        if page is not None:
            return page
        return redirect(url_for("serve_main_page"))
    app.config["content"].edit_category(
        id_=id_, name=request.form.get("name", type=str)
    )
    return redirect(url_for("serve_category_page", id_=id_))


@app.route("/category/delete/<int:id_>/", methods=["GET", "POST"])
def serve_delete_category_page(id_):
    """Serve page for deleting a category or handle POST request.

    :param id_: integer; category ID
    :return: HTML code for page or redirect URL
    """
    if not is_logged_in:
        flash("You need to be logged in to edit content.")
        return redirect(url_for("serve_main_page"))
    if request.method == "GET":
        page = app.config["content"].render_delete_category_page(
            user_name=user_name, id_=id_
        )
        if page is not None:
            return page
        return redirect(url_for("serve_main_page"))
    app.config["content"].delete_category(id_=id_)
    return redirect(url_for("serve_main_page"))


@app.route("/item/view/<int:id_>/")
def serve_item_page(id_):
    """Serve page for one item.

    :param id_: integer; item ID
    :return: HTML code for page
    """
    page = app.config["content"].render_item_page(
        is_logged_in=is_logged_in, user_name=user_name, id_=id_
    )
    if page is not None:
        return page
    return redirect(url_for("serve_main_page"))


@app.route("/item/add/", methods=["GET", "POST"])
@app.route("/item/add/<int:id_>/")
# category ID as path parameter is only used with GET requests to pre-select
# the category, a POST request must provide it as a form parameter
def serve_add_item_page(id_=-1):
    """Serve page for adding an item or handle POST request.

    :param id_: integer; category ID proposed for item or -1 to indicate no
        proposal
    :return: HTML code for page or redirect URL
    """
    if not is_logged_in:
        flash("You need to be logged in to edit content.")
        return redirect(url_for("serve_main_page"))
    if request.method == "GET":
        page = app.config["content"].render_add_item_page(
            user_name=user_name, id_=id_
        )
        if page is not None:
            return page
        return redirect(url_for("serve_main_page"))
    id_ = app.config["content"].add_item(
        request.form.get("name", type=str),
        request.form.get("description", type=str),
        int(request.form.get("category", type=str))
    )
    if id_ is None:
        return redirect(url_for("serve_main_page"))
    return redirect(url_for("serve_item_page", id_=id_))


@app.route("/item/edit/<int:id_>/", methods=["GET", "POST"])
def serve_edit_items_page(id_):
    """Serve page for editing an item or handle POST request.

    :param id_: integer; item ID
    :return: HTML code for page or redirect URL
    """
    if not is_logged_in:
        flash("You need to be logged in to edit content.")
        return redirect(url_for("serve_main_page"))
    if request.method == "GET":
        page = app.config["content"].render_edit_item_page(
            user_name=user_name, id_=id_
        )
        if page is not None:
            return page
        return redirect(url_for("serve_main_page"))
    app.config["content"].edit_item(
        id_,
        request.form.get("name", type=str),
        request.form.get("description", type=str),
        int(request.form.get("category", type=str))
    )
    return redirect(url_for("serve_item_page", id_=id_))


@app.route("/item/delete/<int:id_>/", methods=["GET", "POST"])
def serve_delete_items_page(id_):
    """Serve page for deleting an item or handle POST request.

    :param id_: integer; item ID
    :return: HTML code for page or redirect URL
    """
    if not is_logged_in:
        flash("You need to be logged in to edit content.")
        return redirect(url_for("serve_main_page"))
    if request.method == "GET":
        page = app.config["content"].render_delete_item_page(
            user_name=user_name, id_=id_
        )
        if page is not None:
            return page
        return redirect(url_for("serve_main_page"))
    app.config["content"].delete_item(id_,)
    return redirect(url_for("serve_main_page"))
