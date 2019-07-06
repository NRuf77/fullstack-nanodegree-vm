#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from sqlalchemy import create_engine

from catalog import app, ContentManager, DBManager


if __name__ == "__main__":
    app.debug = True
    app.config["content"] = ContentManager(DBManager(
        create_engine("sqlite:///data/catalog.db")
    ))
    app.secret_key = os.urandom(16)
    app.run(host='0.0.0.0', port=8080)
