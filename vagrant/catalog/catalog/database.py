# -*- coding: utf-8 -*-
"""Table definitions and database manager class.

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
logger.addHandler(logging.NullHandler)
# log output is configured for the root logger in the startup script

Base = declarative_base()


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False, unique=True)

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

        :return:
        """
        session = sessionmaker(self._engine)()
        if self._engine.driver == 'pysqlite':
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

    def create_tables(self):
        """Create database tables that do not already exist.

        :return: no return value
        """
        Base.metadata.create_all(self._engine)

    def add_category(self, name):
        """Add a new category.

        :param name: string; name of the category
        :return: integer ID of the new category if the query was successful,
            None if it was not; flash message string
        """
        # noinspection PyBroadException
        try:
            name = bleach.clean(name)
            with self._get_session() as session:
                new_category = Category(name=bleach.clean(name))
                session.add(new_category)
                session.flush()
                new_id = new_category.id
        except BaseException:
            message = "Failed to add a category."
            logger.exception(message)
            # this logs a stacktrace but no implementation details are leaked
            # to the client
            return None, message
        return new_id, "Added new category '{}'.".format(name)

    def edit_category(self, id_, name):
        """Change an existing category.

        :param id_: integer; category ID
        :param name: string; new category name
        :return: flash message string
        """
        # noinspection PyBroadException
        try:
            name = bleach.clean(name)
            with self._get_session() as session:
                category = session.query(Category).filter(
                    Category.id == id_
                ).one()
                old_name = bleach.clean(category.name)
                category.name = name
                session.add(category)
        except BaseException:
            message = "Failed to edit a category."
            logger.exception(message)
            return message
        return "Changed category '{}' name to '{}'.".format(old_name, name)

    def delete_category(self, id_):
        """Delete an existing category.

        :param id_: integer; category ID
        :return: flash message string
        """
        # noinspection PyBroadException
        try:
            with self._get_session() as session:
                category = session.query(Category).filter(
                    Category.id == id_
                )
                name = bleach.clean(category.one().name)
                category.delete()
        except BaseException:
            message = "Failed to delete a category."
            logger.exception(message)
            return message
        return "Deleted category '{}'.".format(name)

    def get_category(self, id_):
        """Retrieve an existing category.

        :param id_: integer; category ID
        :return: dict with fields id and name if the query was successful, None
            if not
        """
        # noinspection PyBroadException
        try:
            with self._get_session() as session:
                category = session.query(Category).filter(
                    Category.id == id_
                ).one()
                result = {
                    "id": category.id,
                    "name": bleach.clean(category.name)
                }
        except BaseException:
            logger.exception("Failed to retrieve a category.")
            return
        return result

    def get_category_list(self):
        """Retrieve all categories in alphabetical order.

        :return: ordered dict with category IDs as keys and category names as
            values if the query was successful, an empty ordered dict if not
        """
        # noinspection PyBroadException
        try:
            with self._get_session() as session:
                categories = session.query(Category).order_by(
                    Category.name
                ).all()
            result = odict([
                (category.id, bleach.clean(category.name))
                for category in categories
            ])
        except BaseException:
            logger.exception("Failed to retrieve category list.")
            return odict()
        return result

    def add_item(self, name, description, category_id):
        """Add a new item.

        :param name: string; item name
        :param description: string; item description
        :param category_id: integer; associated category ID
        :return: integer ID of the new item if the query was successful, None
            if not; flash message string
        """
        # noinspection PyBroadException
        try:
            name = bleach.clean(name)
            description = bleach.clean(description)
            with self._get_session() as session:
                new_item = Item(
                    name=name,
                    description=description,
                    category_id=category_id
                )
                session.add(new_item)
                session.flush()
                new_id = new_item.id
        except BaseException:
            message = "Failed to add an item."
            logger.exception(message)
            return None, message
        return new_id, "Added new item '{}'.".format(name)

    def edit_item(self, id_, name, description, category_id):
        """Edit an existing item.

        :param id_: integer; item ID
        :param name: string; item name
        :param description: string; item description
        :param category_id: integer; associated category ID
        :return: flash message string
        """
        # noinspection PyBroadException
        try:
            name = bleach.clean(name)
            description = bleach.clean(description)
            with self._get_session() as session:
                item = session.query(Item).filter(Item.id == id_).one()
                old_name = bleach.clean(item.name)
                item.name = name
                item.description = description
                item.category_id = category_id
                session.add(item)
        except BaseException:
            message = "Failed to edit an item."
            logger.exception(message)
            return message
        return "Edited item '{}' (formerly '{}').".format(name, old_name)

    def delete_item(self, id_):
        """Delete and existing item.

        :param id_: integer; item ID
        :return: flash message string
        """
        # noinspection PyBroadException
        try:
            with self._get_session() as session:
                item = session.query(Item).filter(Item.id == id_)
                name = bleach.clean(item.one().name)
                item.delete()
        except BaseException:
            message = "Failed to delete an item."
            logger.exception(message)
            return message
        return "Deleted item '{}'.".format(name)

    def get_item(self, id_):
        """Retrieve an existing item.

        :param id_: integer; item ID
        :return: dict with fields id, name, description, created, and
            category_id if the query was successful, None if not
        """
        # noinspection PyBroadException
        try:
            with self._get_session() as session:
                item = session.query(Item).filter(Item.id == id_).one()
                result = {
                    "id": item.id,
                    "name": bleach.clean(item.name),
                    "description": bleach.clean(item.description),
                    "created": item.created,
                    "category_id": item.category_id
                }
        except BaseException:
            logger.exception("Failed to retrieve an item.")
            return
        return result

    def get_latest_items(self, num):
        """Retrieve the names of items which were added last.

        :param num: integer, number of items to retrieve
        :return: ordered dict with item IDs as keys and item names as values
            in order of creation timestamp if the query was successful, an
            empty ordered dict if not
        """
        # noinspection PyBroadException
        try:
            with self._get_session() as session:
                items = session.query(Item).order_by(
                    Item.created.desc()
                ).limit(num).all()
                result = odict([
                    (item.id, bleach.clean(item.name)) for item in items
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
                (item.id, bleach.clean(item.name)) for item in items
            ])
        except BaseException:
            logger.exception("Failed to retrieve items by category.")
            return odict()
        return result
