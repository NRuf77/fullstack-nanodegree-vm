# -*- coding: utf-8 -*-
"""Table definitions and database manager class for catalog server.

This submodule creates a logger named like itself (catalog.database) that logs
information on database exceptions to a NullHandler. Log output can be
redirected as desired by the application importing the submodule.

The database manager catches many exceptions and provides empty containers or
None values in return instead of failing. The exception messages are merely
logged.

Written by Nikolaus Ruf
"""

import bleach
# noinspection PyPep8Naming
from collections import OrderedDict as odict
from contextlib import contextmanager
import logging
from sqlalchemy import Column, Integer, String, DateTime, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.orm.session import sessionmaker
from sqlalchemy.schema import ForeignKey


logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())
# log output is configured for the root logger in the startup script

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    auth_id = Column(String, nullable=False, unique=True)
    # the user name is not tracked in the database since it may change for
    # a given account; it is instead take from the credentials passed by
    # the OAuth2 provider for the session

    relationship("category", backref="user", passive_deletes=True)
    # this is necessary for the ON DELETE CASCADE condition on the foreign key
    # 'user_id' in table 'categories' so that it works with
    # query().filter().delete()
    relationship("item", backref="user", passive_deletes=True)
    # this is necessary for the ON DELETE CASCADE condition on the foreign key
    # 'user_id' in table 'items' so that it works with
    # query().filter().delete()


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False, unique=True)
    user_id = Column(
        Integer,
        ForeignKey(User.id, ondelete="CASCADE"),
        nullable=False
    )
    # this ON DELETE CASCADE condition works with query().filter().delete()

    relationship("item", backref="category", passive_deletes=True)
    # this is necessary for the ON DELETE CASCADE condition on the foreign key
    # 'category_id' in table 'items' so that it works with
    # query().filter().delete()


class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False, unique=True)
    description = Column(String, nullable=False)
    created = Column(DateTime, server_default=func.now())
    category_id = Column(
        Integer,
        ForeignKey(Category.id, ondelete="CASCADE"),
        nullable=False
    )
    # this ON DELETE CASCADE condition works with query().filter().delete()
    user_id = Column(
        Integer,
        ForeignKey(User.id, ondelete="CASCADE"),
        nullable=False
    )
    # this ON DELETE CASCADE condition works with query().filter().delete()


class DBManager:
    """This class wraps all database transactions.
    """

    def __init__(self, engine):
        """Initialize DB manager.

        :param engine: sqlalchemy database engine
        """
        self._engine = engine

    @contextmanager
    def _get_session(self):
        """Provide a context manager for DB queries.

        Slightly modified from the sqlalchemy tutorial.

        :return: context manager
        """
        session = sessionmaker(self._engine)()
        if self._engine.driver == "pysqlite":
            session.execute("PRAGMA foreign_keys=ON")
            # enable foreign key support with sqlite
        try:
            yield session
            session.commit()
        except BaseException as ex:
            session.rollback()
            raise ex
        finally:
            session.close()

    @staticmethod
    def _clean(text):
        """Strip all HTML tags from a string.

        :param text: string
        :return: string without any tags
        """
        return bleach.clean(text, tags=[], strip=True)

    def create_tables(self):
        """Create database tables that do not already exist.

        :return: no return value
        """
        Base.metadata.create_all(self._engine)

    def get_or_add_user_id(self, auth_id):
        """Retrieve integer user ID, create new record if necessary.

        :param auth_id: string; ID from OAuth2 service provider
        :return: integer ID of the user if the query was successful, None if it
            was not
        """
        # noinspection PyBroadException
        try:
            auth_id = self._clean(auth_id)
            if auth_id == "":
                return None
            with self._get_session() as session:
                # check if the user already exists
                user = session.query(User).filter(
                    User.auth_id == auth_id
                ).first()
                if user:
                    user_id = user.id
                else:  # create a new user record
                    user = User(auth_id=auth_id)
                    session.add(user)
                    session.flush()
                    user_id = user.id
        except BaseException:
            message = "Failed to obtain user ID."
            logger.exception(message)
            # this logs a stacktrace but no implementation details are leaked
            # to the client
            return None
        return user_id

    def add_category(self, name, user_id):
        """Add a new category.

        :param name: string; name of the category; must not be empty
        :param user_id: integer; ID of creator
        :return: integer ID of the new category if the query was successful,
            None if it was not; message string
        """
        # noinspection PyBroadException
        try:
            name = self._clean(name)
            if name == "":
                return None, "Invalid category name."
            with self._get_session() as session:
                category = Category(name=name, user_id=user_id)
                session.add(category)
                session.flush()
                category_id = category.id
        except BaseException:
            message = "Failed to add a category."
            logger.exception(message)
            return None, message
        return category_id, "Added new category '{}'.".format(name)

    def edit_category(self, category_id, name):
        """Change an existing category.

        :param category_id: integer; category ID
        :param name: string; new category name; must not be empty
        :return: message string
        """
        # noinspection PyBroadException
        try:
            name = self._clean(name)
            if name == "":
                return "Invalid category name."
            with self._get_session() as session:
                category = session.query(Category).filter(
                    Category.id == category_id
                ).one()
                # one() fails if there is not exactly one record matching the
                # filter
                old_name = self._clean(category.name)
                category.name = name
                session.add(category)
        except BaseException:
            message = "Failed to edit a category."
            logger.exception(message)
            return message
        return "Changed name of category '{}' to '{}'.".format(old_name, name)

    def delete_category(self, category_id):
        """Delete an existing category.

        :param category_id: integer; category ID
        :return: message string
        """
        # noinspection PyBroadException
        try:
            with self._get_session() as session:
                category = session.query(Category).filter(
                    Category.id == category_id
                )
                name = self._clean(category.one().name)
                category.delete()
        except BaseException:
            message = "Failed to delete a category."
            logger.exception(message)
            return message
        return "Deleted category '{}'.".format(name)

    def get_category(self, category_id):
        """Retrieve an existing category.

        :param category_id: integer; category ID
        :return: dict with fields id, name, and user_id if the query was
            successful, None if not
        """
        # noinspection PyBroadException
        try:
            with self._get_session() as session:
                category = session.query(Category).filter(
                    Category.id == category_id
                ).one()
                result = {
                    "id": category.id,
                    "name": self._clean(category.name),
                    "user_id": category.user_id
                }
        except BaseException:
            logger.exception("Failed to retrieve a category.")
            return
        return result

    def get_category_list(self, user_id=None):
        """Retrieve categories in alphabetical order.

        :param user_id: integer or None; if not None, returns only categories
            created by the given user
        :return: ordered dict with category IDs as keys and category names as
            values if the query was successful, an empty ordered dict if not
        """
        # noinspection PyBroadException
        try:
            with self._get_session() as session:
                if user_id is None:
                    categories = session.query(Category).order_by(
                        Category.name
                    ).all()
                else:
                    categories = session.query(Category).filter(
                        Category.user_id == user_id
                    ).order_by(
                        Category.name
                    ).all()
                result = odict([
                    (category.id, self._clean(category.name))
                    for category in categories
                ])
        except BaseException:
            logger.exception("Failed to retrieve category list.")
            return odict()
        return result

    def add_item(self, name, description, category_id, user_id):
        """Add a new item.

        :param name: string; item name; must not be empty
        :param description: string; item description
        :param category_id: integer; associated category ID
        :param user_id: integer; ID of creator
        :return: integer ID of the new item if the query was successful, None
            if not; message string
        """
        # noinspection PyBroadException
        try:
            name = self._clean(name)
            if name == "":
                return None, "Invalid item name."
            description = self._clean(description)
            with self._get_session() as session:
                item = Item(
                    name=name,
                    description=description,
                    category_id=category_id,
                    user_id=user_id
                )
                session.add(item)
                session.flush()
                item_id = item.id
        except BaseException:
            message = "Failed to add an item."
            logger.exception(message)
            return None, message
        return item_id, "Added new item '{}'.".format(name)

    def edit_item(self, item_id, name, description, category_id):
        """Edit an existing item.

        :param item_id: integer; item ID
        :param name: string; item name; must not be empty
        :param description: string; item description
        :param category_id: integer; associated category ID
        :return: message string
        """
        # noinspection PyBroadException
        try:
            name = self._clean(name)
            if name == "":
                return "Invalid item name."
            description = self._clean(description)
            with self._get_session() as session:
                item = session.query(Item).filter(Item.id == item_id).one()
                old_name = self._clean(item.name)
                item.name = name
                item.description = description
                item.category_id = category_id
                session.add(item)
        except BaseException:
            message = "Failed to edit an item."
            logger.exception(message)
            return message
        return "Edited item '{}' (formerly '{}').".format(name, old_name)

    def delete_item(self, item_id):
        """Delete and existing item.

        :param item_id: integer; item ID
        :return: message string
        """
        # noinspection PyBroadException
        try:
            with self._get_session() as session:
                item = session.query(Item).filter(Item.id == item_id)
                name = self._clean(item.one().name)
                item.delete()
        except BaseException:
            message = "Failed to delete an item."
            logger.exception(message)
            return message
        return "Deleted item '{}'.".format(name)

    def get_item(self, item_id):
        """Retrieve an existing item.

        :param item_id: integer; item ID
        :return: dict with fields id, name, description, created, category_id,
            and user_id if the query was successful, None if not
        """
        # noinspection PyBroadException
        try:
            with self._get_session() as session:
                item = session.query(Item).filter(Item.id == item_id).one()
                result = {
                    "id": item.id,
                    "name": self._clean(item.name),
                    "description": self._clean(item.description),
                    "created": item.created,
                    "category_id": item.category_id,
                    "user_id": item.user_id
                }
        except BaseException:
            logger.exception("Failed to retrieve an item.")
            return
        return result

    def get_latest_items(self, num):
        """Retrieve the names of items which were added last.

        :param num: integer, number of items to retrieve
        :return: ordered dict; keys are item IDs and values are dicts with
            fields:
            - name: string; item name
            - category_id: integer; category ID
            - category_name: string; category name
            elements are provided in order of creation timestamp with ties
            broken in lexicographical order of item names; if the query fails,
            it returns an empty ordered dict, same as if there are no records
        """
        # noinspection PyBroadException
        try:
            with self._get_session() as session:
                items = session.query(Item, Category).join(
                    Category
                ).order_by(
                    Item.created.desc(), Item.name
                ).limit(num).all()
                result = odict([
                    (item[0].id, {
                        "name": item[0].name,
                        "category_id": item[1].id,
                        "category_name": item[1].name

                    })
                    for item in items
                ])
        except BaseException:
            logger.exception("Failed to retrieve latest items.")
            return odict()
        return result

    def get_category_items(self, category_id):
        """Retrieve the names if all items within one category.

        :param category_id: integer; category ID
        :return: ordered dict with item IDs as keys and item names as values
            in alphabetical order if the query was successful, an empty ordered
            dict if not
        """
        # noinspection PyBroadException
        try:
            with self._get_session() as session:
                items = session.query(Item).filter(
                    Item.category_id == category_id
                ).order_by(Item.name).all()
                result = odict([
                    (item.id, self._clean(item.name)) for item in items
                ])
        except BaseException:
            logger.exception("Failed to retrieve items by category.")
            return odict()
        return result
