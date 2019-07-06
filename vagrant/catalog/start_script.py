#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import os
from sqlalchemy import create_engine

from catalog import app, ContentManager, DBManager


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


if __name__ == "__main__":
    logger.info("Configure catalog app")
    app.debug = True
    app.config["content"] = ContentManager(DBManager(
        create_engine("sqlite:///data/catalog.db")
    ))
    app.secret_key = os.urandom(16)
    logger.info("Start catalog app")
    app.run(host='0.0.0.0', port=8080)
