# -*- coding: utf-8 -*-
"""Content manager for catalog server.

Written by Nikolaus Ruf
"""

# noinspection PyPep8Naming
from collections import OrderedDict as odict
from flask import render_template, flash


class ContentManager:
    """Content manager for catalog server.
    """

    def __init__(self, db_manager):
        """Initialize content manager.

        :param db_manager: an instance of catalog.database.DBManager
        """
        self._db_manager = db_manager

    def get_user_id(self, auth_id):
        """Retrieve user ID.

        :param auth_id: string; ID from OAuth2 service provider
        :return: integer user ID or None if there was a problem
        """
        return self._db_manager.get_or_add_user_id(auth_id)

    def render_main_page(self, client_id, state, user_id, user_name):
        """Render main page template.

        :param client_id: string; Google client ID
        :param state: string; anti-CSRF token
        :param user_id: integer; active user ID
        :param user_name: string; user name
        :return: HTML page
        """
        return render_template(
            "main.html",
            client_id=client_id,
            state=state,
            is_logged_in=user_id is not None,
            user_name=user_name,
            categories=self._db_manager.get_category_list(),
            items=self._db_manager.get_latest_items(10)
        )

    def render_category_page(
            self, client_id, state, user_id, user_name, category_id):
        """Render category page template.

        :param client_id: string; Google client ID
        :param state: string; anti-CSRF token
        :param user_id: integer; active user ID
        :param user_name: string; user name
        :param category_id: integer; category ID
        :return: HTML page or None if something went wrong
        """
        category = self._db_manager.get_category(category_id)
        if category is None:
            flash("Invalid category.")
            return
        items = self._db_manager.get_category_items(category_id)
        return render_template(
            "category_view.html",
            client_id=client_id,
            state=state,
            is_logged_in=user_id is not None,
            is_creator=category["user_id"] == user_id,
            user_name=user_name,
            category=category,
            items=items
        )

    @staticmethod
    def render_add_category_page(client_id, state, user_name):
        """Render add category page template.

        :param client_id: string; Google client ID
        :param state: string; anti-CSRF token
        :param user_name: string; user name
        :return: HTML page
        """
        # the check whether the user is signed in and may thus add an item is
        # already performed by the app
        return render_template(
            "category_add.html",
            client_id=client_id,
            state=state,
            is_logged_in=True,
            user_name=user_name
        )

    def add_category(self, name, user_id):
        """Add a new category.

        :param name: string; desired category name
        :param user_id: integer; active user ID
        :return: integer ID of new category or None to indicate a failure
        """
        category_id, message = self._db_manager.add_category(name, user_id)
        flash(message)
        return category_id

    def render_edit_category_page(
            self, client_id, state, user_id, user_name, category_id):
        """Render edit category page template.

        :param client_id: string; Google client ID
        :param state: string; anti-CSRF token
        :param user_id: integer; active user ID
        :param user_name: string; user name
        :param category_id: integer; category ID
        :return: HTML page or None if something went wrong
        """
        category = self._db_manager.get_category(category_id)
        if category is None:
            flash("Invalid category.")
            return
        if category["user_id"] != user_id:
            # the check whether the user owns the category can only be made
            # here since the database needs to be consulted
            flash("Only the original creator can edit a category.")
            return
        return render_template(
            "category_edit.html",
            client_id=client_id,
            state=state,
            is_logged_in=True,
            user_name=user_name,
            category=category
        )

    def edit_category(self, category_id, name, user_id):
        """Edit an existing category.

        :param category_id: integer; category ID
        :param name: string; desired category name; must not be empty
        :param user_id: integer; active user ID
        :return: no return value
        """
        category = self._db_manager.get_category(category_id)
        if category is None:
            flash("Invalid category.")
            return
        if category["user_id"] != user_id:
            flash("Only the original creator can edit a category.")
            return
        flash(self._db_manager.edit_category(category_id, name))

    def render_delete_category_page(
            self, client_id, state, user_id, user_name, category_id):
        """Render delete category page.

        :param client_id: string; Google client ID
        :param state: string; anti-CSRF token
        :param user_id: integer; active user ID
        :param user_name: string; user name
        :param category_id: integer; category ID
        :return: HTML page or None if something went wrong
        """
        category = self._db_manager.get_category(category_id)
        if category is None:
            flash("Invalid category.")
            return
        if category["user_id"] != user_id:
            flash("Only the original creator can delete a category.")
            return
        return render_template(
            "category_delete.html",
            client_id=client_id,
            state=state,
            is_logged_in=True,
            user_name=user_name,
            category=category
        )

    def delete_category(self, category_id, user_id):
        """Delete an existing category.

        :param category_id: integer; category ID
        :param user_id: integer; active user ID
        :return: no return value
        """
        category = self._db_manager.get_category(category_id)
        if category is None:
            flash("Invalid category.")
            return
        if category["user_id"] != user_id:
            flash("Only the original creator can delete a category.")
            return
        flash(self._db_manager.delete_category(category_id))

    def render_item_page(self, client_id, state, user_id, user_name, item_id):
        """Render item page template.

        :param client_id: string; Google client ID
        :param state: string; anti-CSRF token
        :param user_id: integer; active user ID
        :param user_name: string; user name
        :param item_id: integer; item ID
        :return: HTML page or None if something went wrong
        """
        item = self._db_manager.get_item(item_id)
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
            client_id=client_id,
            state=state,
            is_logged_in=user_id is not None,
            is_creator=item["user_id"] == user_id,
            user_name=user_name,
            category=category,
            item=item
        )

    def render_add_item_page(
            self, client_id, state, user_id, user_name, category_id):
        """Render add item page template.

        :param client_id: string; Google client ID
        :param state: string; anti-CSRF token
        :param user_id: integer; active user ID
        :param user_name: string; user name
        :param category_id: integer; category ID proposed for item, if invalid,
            the select box will initialize to the default value
        :return: HTML page or None if something went wrong
        """
        categories = self._db_manager.get_category_list(user_id)
        if len(categories) == 0:
            flash("You have created no categories to add items to.")
            return
        return render_template(
            "item_add.html",
            client_id=client_id,
            state=state,
            is_logged_in=True,
            user_name=user_name,
            category_id=category_id,
            categories=categories
        )

    def add_item(self, name, description, category_id, user_id):
        """Add a new item.

        :param name: string; item name
        :param description: string; item description
        :param category_id: integer; category ID associated with item
        :param user_id: integer; active user ID
        :return: integer item ID or None to indicate failure
        """
        category = self._db_manager.get_category(category_id)
        if category is None:
            flash("Invalid category.")
            return
        if category["user_id"] != user_id:
            flash("You can only add items to categories you created.")
            return
        item_id, message = self._db_manager.add_item(
            name=name,
            description=description,
            category_id=category_id,
            user_id=user_id
        )
        flash(message)
        return item_id

    def render_edit_item_page(
            self, client_id, state, user_id, user_name, item_id):
        """Render edit item page template.

        :param client_id: string; Google client ID
        :param state: string; anti-CSRF token
        :param user_id: integer; active user ID
        :param user_name: string; user name
        :param item_id: integer; item ID
        :return: HTML page or None if something went wrong
        """
        categories = self._db_manager.get_category_list(user_id)
        if len(categories) == 0:
            flash("You have created no categories to add items to.")
            return
        item = self._db_manager.get_item(item_id)
        if item is None:
            flash("Invalid item.")
            return
        if item["user_id"] != user_id:
            flash("Only the original creator can edit an item.")
            return
        return render_template(
            "item_edit.html",
            client_id=client_id,
            state=state,
            is_logged_in=True,
            user_name=user_name,
            categories=categories,
            item=item
        )

    def edit_item(self, item_id, name, description, category_id, user_id):
        """Edit an existing item.

        :param item_id: integer; item ID
        :param name: string; item name
        :param description: string; item description
        :param category_id: integer; category ID associated with item
        :param user_id: integer; active user ID
        :return: no return value
        """
        item = self._db_manager.get_item(item_id)
        if item is None:
            flash("Invalid item.")
            return
        if item["user_id"] != user_id:
            flash("Only the original creator can edit an item.")
            return
        category = self._db_manager.get_category(category_id)
        if category is None:
            flash("Invalid category.")
            return
        if category["user_id"] != user_id:
            flash("You can only add items to categories you created.")
            return
        flash(self._db_manager.edit_item(
            item_id=item_id,
            name=name,
            description=description,
            category_id=category_id
        ))

    def render_delete_item_page(
            self, client_id, state, user_id, user_name, item_id):
        """Render delete item page template.

        :param client_id: string; Google client ID
        :param state: string; anti-CSRF token
        :param user_id: integer; active user ID
        :param user_name: string; user name
        :param item_id: integer; item ID
        :return: HTML page or None if something went wrong
        """
        item = self._db_manager.get_item(item_id)
        if item is None:
            flash("Invalid item.")
            return
        if item["user_id"] != user_id:
            flash("Only the original creator can delete an item.")
            return
        category = self._db_manager.get_category(item["category_id"])
        if category is None:
            flash("Sorry, something went wrong.")
            return
        return render_template(
            "item_delete.html",
            client_id=client_id,
            state=state,
            is_logged_in=True,
            user_name=user_name,
            category=category["name"],
            item=item
        )

    def delete_item(self, item_id, user_id):
        """Delete an existing item.

        :param item_id: integer; item ID
        :param user_id: integer; active user ID
        :return: no return value
        """
        item = self._db_manager.get_item(item_id)
        if item is None:
            flash("Invalid item.")
            return
        if item["user_id"] != user_id:
            flash("Only the original creator can delete an item.")
            return
        flash(self._db_manager.delete_item(item_id))

    def get_content(self, resource, num, id_):
        """Provide selected database content.

        :param resource: string; either 'categories', 'latest_items',
            'category', or 'item'
        :param num: positive integer or None; resource type 'latest_items'
            requires a number of items to return
        :param id_: integer or None; resource types 'category' and 'item'
            require a specific ID
        :return: None if the requested resource does not exist, otherwise:
            - categories: ordered dict with integer item ID as key and category
              name as value
            - latest_items: ordered dict with integer item ID as key and a dict
              with keys 'name', 'category_id', and 'category_name' containing
              the item name and category information
            - category: ordered dict with fields id, name, and items containing
              the integer id, category name, and an ordered dict; the latter
              contains item IDs as keys and item names as values in
              alphabetical order
            - item: ordered dict with fields id, name, description category_id,
              and category_name
        """
        if resource == "categories":
            return self._db_manager.get_category_list()
        if resource == "latest_items" and num > 0:
            return self._db_manager.get_latest_items(num)
        if resource == "category" and id_ is not None:
            category = self._db_manager.get_category(id_)
            if category is not None:
                items = self._db_manager.get_category_items(category["id"])
                return odict([
                    ("id", category["id"]),
                    ("name", category["name"]),
                    ("items", items)
                ])
        if resource == "item" and id_ is not None:
            item = self._db_manager.get_item(id_)
            if item is not None:
                category = self._db_manager.get_category(item["category_id"])
                if category is not None:
                    return odict([
                        ("id", item["id"]),
                        ("name", item["name"]),
                        ("description", item["description"]),
                        ("category_id", item["category_id"]),
                        ("category_name", category["name"])
                    ])
        # if no conditions for a valid return value apply, exit with None
