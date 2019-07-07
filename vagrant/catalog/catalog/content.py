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
        return render_template(
            "main.html",
            is_logged_in=is_logged_in,
            user_name=user_name,
            categories=self._db_manager.get_category_list(),
            items=self._db_manager.get_latest_items(10)
        )

    def render_category_page(self, is_logged_in, user_name, id_):
        """Render category page template.

        :param is_logged_in: boolean flag; whether the user is logged in
        :param user_name: string; user name
        :param id_: integer; category ID
        :return: HTML page or None if something went wrong
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

        :param name: string; desired category name
        :return: integer ID of new category or None to indicate a failure
        """
        id_, message = self._db_manager.add_category(name)
        flash(message)
        return id_

    def render_edit_category_page(self, user_name, id_):
        """Render edit category page template.

        :param user_name: string; user name
        :param id_: integer; category ID
        :return: HTML page or None if something went wrong
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
        flash(self._db_manager.edit_category(id_=id_, name=name))

    def render_delete_category_page(self, user_name, id_):
        """Render delete category page.

        :param user_name: string; user name
        :param id_: integer; category ID
        :return: HTML page or None if something went wrong
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
        :return: HTML page or None if something went wrong
        """
        item = self._db_manager.get_item(id_)
        if item is None:
            flash("Invalid item.")
            return
        category = self._db_manager.get_category(item["category_id"])
        if category is None:
            # this should not happen unless there is a concurrent delete
            flash("Sorry, something went wrong.")
            return
        return render_template(
            "item_view.html",
            is_logged_in=is_logged_in,
            user_name=user_name,
            category=category,
            item=item
        )

    def render_add_item_page(self, user_name, id_):
        """Render add item page template.

        :param user_name: string; user name
        :param id_: integer; category ID proposed for item, if invalid, the
            select box will initialize to the default value
        :return: HTML page or None if something went wrong
        """
        categories = self._db_manager.get_category_list()
        if len(categories) == 0:
            # this should not happen unless there is a concurrent delete
            flash("Sorry, something went wrong.")
            return
        return render_template(
            "item_add.html",
            is_logged_in=True,
            user_name=user_name,
            category_id=id_,
            categories=categories
        )

    def add_item(self, name, description, id_):
        """Add a new item.

        :param name: string; item name
        :param description: string; item description
        :param id_: integer; category ID associated with item
        :return: integer item ID or None to indicate failure
        """
        id_, message = self._db_manager.add_item(
            name=name, description=description, category_id=id_
        )
        flash(message)
        return id_

    def render_edit_item_page(self, user_name, id_):
        """Render edit item page template.

        :param user_name: string; user name
        :param id_: integer; item ID
        :return: HTML page or None if something went wrong
        """
        categories = self._db_manager.get_category_list()
        if len(categories) == 0:
            # this should not happen unless there is a concurrent delete
            flash("Sorry, something went wrong.")
            return
        item = self._db_manager.get_item(id_)
        if item is None:
            flash("Invalid item.")
            return
        return render_template(
            "item_edit.html",
            is_logged_in=True,
            user_name=user_name,
            categories=categories,
            item=item
        )

    def edit_item(self, id_, name, description, category_id):
        """Edit an existing item.

        :param id_: integer; item ID
        :param name: string; item name
        :param description: string; item description
        :param category_id: integer; category ID associated with item
        :return: no return value
        """
        flash(self._db_manager.edit_item(
            id_=id_,
            name=name,
            description=description,
            category_id=category_id
        ))

    def render_delete_item_page(self, user_name, id_):
        """Render delete item page template.

        :param user_name: string; user name
        :param id_: integer; item ID
        :return: HTML page or None if something went wrong
        """
        item = self._db_manager.get_item(id_)
        if item is None:
            flash("Invalid item.")
            return
        category = self._db_manager.get_category(item["category_id"])
        if category is None:
            # this should not happen unless there is a concurrent delete
            flash("Sorry, something went wrong.")
            return
        return render_template(
            "item_delete.html",
            is_logged_in=True,
            user_name=user_name,
            category=category["name"],
            item=item
        )

    def delete_item(self, id_):
        """Delete an existing item.

        :param id_: integer; item ID
        :return: no return value
        """
        flash(self._db_manager.delete_item(id_))
