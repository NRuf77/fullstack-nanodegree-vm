#!/usr/bin/env python
# -*- coding: utf-8 -*-

from sqlalchemy import create_engine

from catalog import app, DBManager


if __name__ == "__main__":
    app.debug = True
    app.config["db"] = DBManager(
        create_engine("sqlite:///data/catalog.db")
    )
    app.run(host='0.0.0.0', port=8080)
