# -*- coding: utf-8 -*-
"""Content manager for catalog server.

Written by Nikolaus Ruf
"""

from flask import render_template, flash


class ContentManager:
    """Content manager for catalog server.
    """

    def __init__(self, db_manager):
        """Initialize content manager.

        :param db_manager: an instance of catalog.database.DBManager
        """
        self._db_manager = db_manager

    def get_main_page(self, is_logged_in, user_name):
        """Render main page:

        :param is_logged_in: boolean flag; whether the user is logged in
        :param user_name: string, user name
        :return: HTML page
        """
        categories = self._db_manager.get_category_list()
        items = self._db_manager.get_latest_items(10)
        return render_template(
            "main.html", is_logged_in=is_logged_in, user_name=user_name,
            categories=categories, items=items
        )
