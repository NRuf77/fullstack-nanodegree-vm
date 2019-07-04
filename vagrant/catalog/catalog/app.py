# -*- coding: utf-8 -*-
"""Flask app for catalog server.

Written by Nikolaus Ruf
"""

from flask import Flask, render_template


app = Flask(
    __name__, static_folder="../static", template_folder="../templates"
)  # HTML and style files are outside the Python module


@app.route("/", methods=["GET", "POST"])
def main_page():
    return render_template("base.html")
