# -*- coding: utf-8 -*-
"""Flask app for catalog server.

This submodule creates a logger named like itself (catalog.app) that logs
information on the progress of the sign in procedure to a NullHandler.
Log output can be redirected as desired by the application importing the
submodule.

Written by Nikolaus Ruf
"""

from flask import Flask, redirect, url_for, flash, request, session, \
    make_response
import json
import logging
from oauth2client import client
import os
import requests


logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())
# log output is configured for the root logger in the startup script

app = Flask(__name__)


def get_token():
    """Generate a random 16 byte token encoded as a 32 character hex string.

    :return: string; URL-safe token
    """
    return os.urandom(16).encode("hex")


def get_client_id(file_name):
    """Retrieve the client ID from the client secret file.

    The ID is inserted into each web page template as part of the Google OAuth2
    sign in configuration.

    :param file_name: string; file name with full or relative path
    :return: string; client ID
    """
    with open(file_name, "r") as file_:
        client_id = json.load(file_)["web"]["client_id"]
    return client_id


@app.route("/")
def serve_main_page():
    """Serve main page.

    :return: HTML code for page
    """
    session["state"] = get_token()
    # each page has a sign-in button, so each page gets a state token to
    # protect against CSRF; on pages with HTML forms, the same state token is
    # used to protect the form submission
    return app.config["content"].render_main_page(
        client_id=get_client_id(app.config["google_client_secret_file"]),
        state=session["state"],
        user_id=session.get("user_id", None),
        user_name=session.get("user_name", None)
    )


@app.route("/sign_in", methods=["POST"])
def handle_sign_in():
    """Handle sign in request.

    This function logs every step since helps with debugging the workflow.

    :return: sign in response
    """
    logger.info("Attempt sign in.")
    logger.info("Check header.")
    if not request.headers.get('X-Requested-With'):
        # this check is recommended by Google as a an extra safeguard
        logger.warn("Invalid request header, abort sign in.")
        response = make_response(json.dumps("Invalid request header."), 401)
        response.headers["Content-Type"] = "application/json"
        return response

    logger.info("Check anti-CSRF token.")
    if request.args.get("state") != session["state"]:
        logger.warn("Token mismatch, abort sign in.")
        response = make_response(json.dumps("Token mismatch."), 401)
        response.headers["Content-Type"] = "application/json"
        return response

    logger.info("Request credentials.")
    try:
        credentials = client.credentials_from_clientsecrets_and_code(
            filename=app.config["google_client_secret_file"],
            scope="openid",
            code=request.data
        )
    except client.FlowExchangeError:
        logger.warn("Failed to obtain credentials, abort sign in.")
        response = make_response(
            json.dumps("Failed to obtain credentials."), 401
        )
        response.headers["Content-Type"] = "application/json"
        return response

    logger.info("Revoke access token.")  # no need to keep it
    response = requests.post(
        'https://accounts.google.com/o/oauth2/revoke',
        params={'token': credentials.access_token},
        headers={'content-type': 'application/x-www-form-urlencoded'}
    )
    if response.status_code != 200:
        logger.info("Failed to revoke token.")
        # this does not affect sign in since we know the user

    logger.info("Check user ID against database.")
    auth_id = credentials.id_token["sub"]
    user_name = credentials.id_token["name"]
    user_id = app.config["content"].get_user_id(auth_id)
    if user_id is None:
        # the content manager creates a new record for a non-existent user as
        # long as the user ID is not the empty string after running it through
        # bleach.clean() - so this should really not happen
        logger.warn("Invalid user ID, abort sign in.")
        response = make_response(
            json.dumps("Invalid user ID."), 401
        )
        response.headers["Content-Type"] = "application/json"
        return response

    logger.info("Sign-in complete.")
    session["user_id"] = user_id
    session["user_name"] = user_name
    response = make_response(json.dumps('Sign in complete'), 200)
    response.headers['Content-Type'] = 'application/json'
    return response


@app.route("/sign_out/")
def handle_sign_out():
    """Handle sign in out request.

    :return: redirect to main page
    """
    session.pop("user_id", None)
    session.pop("user_name", None)
    # revoking the OAuth2 token already happened during sign in since the app
    # does not need the token for anything else
    return redirect(url_for("serve_main_page"))


@app.route("/category/view/<int:category_id>/")
def serve_category_page(category_id):
    """Serve page for one category.

    :return: HTML code for page or redirect URL
    """
    session["state"] = get_token()
    page = app.config["content"].render_category_page(
        client_id=get_client_id(app.config["google_client_secret_file"]),
        state=session["state"],
        user_id=session.get("user_id", None),
        user_name=session.get("user_name", None),
        category_id=category_id
    )
    if page is not None:
        return page
    # page can be None of the ID is invalid or something is wrong with the
    # database; the content manager generates an appropriate flash message in
    # this case
    return redirect(url_for("serve_main_page"))


@app.route("/category/add/", methods=["GET", "POST"])
def serve_add_category_page():
    """Serve page for adding a category or handle POST request.

    :return: HTML code for page or redirect URL
    """
    user_id = session.get("user_id", None)
    # both GET and POST require sign in so we check it first
    if user_id is None:
        flash("You need to be logged in to edit content.")
        return redirect(url_for("serve_main_page"))
    if request.method == "GET":
        session["state"] = get_token()
        return app.config["content"].render_add_category_page(
            client_id=get_client_id(app.config["google_client_secret_file"]),
            state=session["state"],
            user_name=session.get("user_name", None)
        )
    # POST
    if request.form.get("state", default="") != session["state"]:
        # this can happen if somebody uses the 'back' button of the browser
        # since the state token is generated for every page
        flash("Sorry, the form data was stale. Please try again.")
        return redirect(url_for("serve_add_category_page"))
    category_id = app.config["content"].add_category(
        name=request.form.get("name", type=str), user_id=user_id
    )
    if category_id is None:
        return redirect(url_for("serve_main_page"))
    return redirect(url_for("serve_category_page", category_id=category_id))


@app.route("/category/edit/<int:category_id>/", methods=["GET", "POST"])
def serve_edit_category_page(category_id):
    """Serve page for editing a category or handle POST request.

    :param category_id: integer; category ID
    :return: HTML code for page or redirect URL
    """
    user_id = session.get("user_id", None)
    if user_id is None:
        flash("You need to be logged in to edit content.")
        return redirect(url_for("serve_main_page"))
    if request.method == "GET":
        session["state"] = get_token()
        page = app.config["content"].render_edit_category_page(
            client_id=get_client_id(app.config["google_client_secret_file"]),
            state=session["state"],
            user_id=user_id,
            user_name=session.get("user_name", None),
            category_id=category_id
        )
        if page is not None:
            return page
        return redirect(url_for("serve_main_page"))
    # POST
    if request.form.get("state", default="") != session["state"]:
        flash("Sorry, the form data was stale. Please try again.")
        return redirect(url_for("serve_edit_category_page", id_=category_id))
    app.config["content"].edit_category(
        category_id=category_id,
        name=request.form.get("name", type=str),
        user_id=user_id
    )
    return redirect(url_for("serve_category_page", category_id=category_id))


@app.route("/category/delete/<int:category_id>/", methods=["GET", "POST"])
def serve_delete_category_page(category_id):
    """Serve page for deleting a category or handle POST request.

    :param category_id: integer; category ID
    :return: HTML code for page or redirect URL
    """
    user_id = session.get("user_id", None)
    if user_id is None:
        flash("You need to be logged in to edit content.")
        return redirect(url_for("serve_main_page"))
    if request.method == "GET":
        session["state"] = get_token()
        page = app.config["content"].render_delete_category_page(
            client_id=get_client_id(app.config["google_client_secret_file"]),
            state=session["state"],
            user_id=user_id,
            user_name=session.get("user_name", None),
            category_id=category_id
        )
        if page is not None:
            return page
        return redirect(url_for("serve_main_page"))
    # POST
    if request.form.get("state", default="") != session["state"]:
        flash("Sorry, the form data was stale. Please try again.")
        return redirect(
            url_for("serve_delete_category_page", category_id=category_id)
        )
    app.config["content"].delete_category(category_id, user_id)
    return redirect(url_for("serve_main_page"))


@app.route("/item/view/<int:item_id>/")
def serve_item_page(item_id):
    """Serve page for one item.

    :param item_id: integer; item ID
    :return: HTML code for page
    """
    session["state"] = get_token()
    page = app.config["content"].render_item_page(
        client_id=get_client_id(app.config["google_client_secret_file"]),
        state=session["state"],
        user_id=session.get("user_id", None),
        user_name=session.get("user_name", None),
        item_id=item_id
    )
    if page is not None:
        return page
    return redirect(url_for("serve_main_page"))


@app.route("/item/add/", methods=["GET", "POST"])
@app.route("/item/add/<int:category_id>/")
# category ID as path parameter is only used with GET requests to pre-select
# the category in the form; a POST request must provide it as a form parameter
def serve_add_item_page(category_id=-1):
    """Serve page for adding an item or handle POST request.

    :param category_id: integer; category ID proposed for item or -1 to
        indicate no proposal
    :return: HTML code for page or redirect URL
    """
    user_id = session.get("user_id", None)
    if user_id is None:
        flash("You need to be logged in to edit content.")
        return redirect(url_for("serve_main_page"))
    if request.method == "GET":
        session["state"] = get_token()
        page = app.config["content"].render_add_item_page(
            client_id=get_client_id(app.config["google_client_secret_file"]),
            state=session["state"],
            user_id=user_id,
            user_name=session.get("user_name", None),
            category_id=category_id
        )
        if page is not None:
            return page
        return redirect(url_for("serve_main_page"))
    # POST
    if request.form.get("state", default="") != session["state"]:
        flash("Sorry, the form data was stale. Please try again.")
        return redirect(
            url_for("serve_add_item_page", category_id=category_id)
        )
    item_id = app.config["content"].add_item(
        name=request.form.get("name", type=str),
        description=request.form.get("description", type=str),
        category_id=int(request.form.get("category", type=str)),
        user_id=user_id
    )
    if item_id is None:
        return redirect(url_for("serve_main_page"))
    return redirect(url_for("serve_item_page", item_id=item_id))


@app.route("/item/edit/<int:item_id>/", methods=["GET", "POST"])
def serve_edit_items_page(item_id):
    """Serve page for editing an item or handle POST request.

    :param item_id: integer; item ID
    :return: HTML code for page or redirect URL
    """
    user_id = session.get("user_id", None)
    if user_id is None:
        flash("You need to be logged in to edit content.")
        return redirect(url_for("serve_main_page"))
    if request.method == "GET":
        session["state"] = get_token()
        page = app.config["content"].render_edit_item_page(
            client_id=get_client_id(app.config["google_client_secret_file"]),
            state=session["state"],
            user_id=user_id,
            user_name=session.get("user_name", None),
            item_id=item_id
        )
        if page is not None:
            return page
        return redirect(url_for("serve_main_page"))
    # POST
    if request.form.get("state", default="") != session["state"]:
        flash("Sorry, the form data was stale. Please try again.")
        return redirect(url_for("serve_edit_items_page", item_id=item_id))
    app.config["content"].edit_item(
        item_id=item_id,
        name=request.form.get("name", type=str),
        description=request.form.get("description", type=str),
        category_id=int(request.form.get("category", type=str)),
        user_id=user_id
    )
    return redirect(url_for("serve_item_page", item_id=item_id))


@app.route("/item/delete/<int:item_id>/", methods=["GET", "POST"])
def serve_delete_items_page(item_id):
    """Serve page for deleting an item or handle POST request.

    :param item_id: integer; item ID
    :return: HTML code for page or redirect URL
    """
    user_id = session.get("user_id", None)
    if user_id is None:
        flash("You need to be logged in to edit content.")
        return redirect(url_for("serve_main_page"))
    if request.method == "GET":
        session["state"] = get_token()
        page = app.config["content"].render_delete_item_page(
            client_id=get_client_id(app.config["google_client_secret_file"]),
            state=session["state"],
            user_id=user_id,
            user_name=session.get("user_name", None),
            item_id=item_id
        )
        if page is not None:
            return page
        return redirect(url_for("serve_main_page"))
    # POST
    if request.form.get("state", default="") != session["state"]:
        flash("Sorry, the form data was stale. Please try again.")
        return redirect(url_for("serve_delete_items_page", item_id=item_id))
    app.config["content"].delete_item(item_id, user_id)
    return redirect(url_for("serve_main_page"))


@app.route("/json/categories/")
@app.route("/json/latest_items/<int:num>/")
@app.route("/json/category/<int:id_>/")
@app.route("/json/item/<int:id_>/")
def serve_json(num=None, id_=None):
    """Provide selected database content as JSON object.

    :param num: positive integer or None; request for latest items needs to
        provide a number of items to return
    :param id_: integer or None; requests for a specific category or item need
        to provide an ID
    :return: JSON response
    """
    resource = request.path.split("/")[2]
    content = app.config["content"].get_content(resource, num, id_)
    if content is None:
        response = make_response(
            json.dumps("Requested content not found."), 404
        )
        response.headers["Content-Type"] = "application/json"
        return response
    response = make_response(json.dumps(content), 200)
    # build response by hand and do not use flask.jsonify() as the latter
    # destroys the order in an ordered dict
    response.headers["Content-Type"] = "application/json"
    return response
