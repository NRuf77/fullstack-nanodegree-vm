#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Configure catalog app.

If called directly, will also start to server the app in debug mode using
Flask's built in server. Do not use this in production!

Written by Nikolaus Ruf
"""

import logging
from sqlalchemy import create_engine

from catalog import app, ContentManager, DBManager, get_token


# configure root logger to capture all log messages
handler = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
logger = logging.getLogger()
logger.addHandler(handler)
handler = logging.FileHandler("catalog.log", mode="w")
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

logger.info("Configure catalog app")
app.static_folder = "../static"
# HTML and style files are outside the Python module directory
app.template_folder = "../templates"
app.secret_key = get_token()
app.config["content"] = ContentManager(DBManager(
    create_engine("sqlite:///data/catalog.db")
))
app.config["google_client_secret_file"] = "data/client_secret.json"


if __name__ == "__main__":
    logger.info("Start catalog app in debug mode")
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
