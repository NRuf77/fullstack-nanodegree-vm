# -*- coding: utf-8 -*-
"""Content manager for catalog server.

Written by Nikolaus Ruf
"""

from flask import render_template, flash
import logging


logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())
# log output is configured for the root logger in the startup script


class ContentManager:
    """Content manager for catalog server.
    """

    def __init__(self, db_manager):
        """Initialize content manager.

        :param db_manager: an instance of catalog.database.DBManager
        """
        self._db_manager = db_manager

    def render_main_page(self, is_logged_in, user_name):
        """Render main page template.

        :param is_logged_in: boolean flag; whether the user is logged in
        :param user_name: string; user name
        :return: HTML page
        """
        categories = self._db_manager.get_category_list()
        items = self._db_manager.get_latest_items(10)
        return render_template(
            "main.html",
            is_logged_in=is_logged_in,
            user_name=user_name,
            categories=categories,
            items=items
        )

    def render_category_page(self, is_logged_in, user_name, id_):
        """Render category page template.

        :param is_logged_in: boolean flag; whether the user is logged in
        :param user_name: string; user name
        :param id_: integer; category ID
        :return: HTML page
        """
        category = self._db_manager.get_category(id_)
        if category is None:
            flash("Invalid category.")
            return
        items = self._db_manager.get_category_items(id_)
        return render_template(
            "category_view.html",
            is_logged_in=is_logged_in,
            user_name=user_name,
            category=category,
            items=items
        )

    @staticmethod
    def render_add_category_page(user_name):
        """Render add category page template.

        :param user_name: string; user name
        :return: HTML page
        """
        return render_template(
            "category_add.html",
            is_logged_in=True,
            user_name=user_name
        )

    def add_category(self, name):
        """Add a new category.

        :param name: string; desired category name; must not be empty
        :return: integer ID of new category or None to indicate a failure
        """
        if name == "":
            flash("Invalid category name.")
            return
        id_, message = self._db_manager.add_category(name)
        flash(message)
        return id_

    def render_edit_category_page(self, user_name, id_):
        """Render edit category page template.

        :param user_name: string; user name
        :param id_: integer; category ID
        :return: HTML page
        """
        category = self._db_manager.get_category(id_)
        if category is None:
            flash("Invalid category.")
            return
        return render_template(
            "category_edit.html",
            is_logged_in=True,
            user_name=user_name,
            category=category
        )

    def edit_category(self, id_, name):
        """Edit an existing category.

        :param id_: integer; category ID
        :param name: string; desired category name; must not be empty
        :return: no return value
        """
        if name == "":
            flash("Invalid category name.")
            return
        flash(self._db_manager.edit_category(id_=id_, name=name))

    def render_delete_category_page(self, user_name, id_):
        """Render delete category page.

        :param user_name: string; user name
        :param id_: integer; category ID
        :return: HTML page
        """
        category = self._db_manager.get_category(id_)
        if category is None:
            flash("Invalid category.")
            return
        return render_template(
            "category_delete.html",
            is_logged_in=True,
            user_name=user_name,
            category=category
        )

    def delete_category(self, id_):
        """Delete an existing category.

        :param id_: integer; category ID
        :return: no return value
        """
        flash(self._db_manager.delete_category(id_=id_))

    def render_item_page(self, is_logged_in, user_name, id_):
        """Render item page template.

        :param is_logged_in: boolean flag; whether the user is logged in
        :param user_name: string; user name
        :param id_: integer; item ID
        :return: HTML page
        """
        item = self._db_manager.get_item(id_)
        if item is None:
            flash("Invalid item.")
            return
        category = self._db_manager.get_category(item["category_id"])
        if category is None:
            flash("Sorry, something went wrong.")
            return
        return render_template(
            "item_view.html",
            is_logged_in=is_logged_in,
            user_name=user_name,
            category=category,
            item=item
        )
