# -*- coding: utf-8 -*-
"""Flask app for catalog server.

Written by Nikolaus Ruf
"""

from flask import Flask


app = Flask(
    __name__, static_folder="../static", template_folder="../templates"
)  # HTML and style files are outside the Python module


@app.route("/")
def view_only():
    """

    :return:
    """
    return app.config["content"].get_main_page(
        is_logged_in=True, user_name="Niko"
    )
