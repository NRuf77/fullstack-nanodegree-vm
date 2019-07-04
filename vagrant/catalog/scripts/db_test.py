#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Integration test for the database manager.

This script needs to be called from the main project directory as
scripts/db_test.py since relative paths are defined from there.

Written by Nikolaus Ruf
"""

# noinspection PyPep8Naming
from collections import OrderedDict as odict
from datetime import datetime
import logging
import os
from sqlalchemy import create_engine
import time

from catalog.database import DBManager


# add a logger to display messages for exceptions suppressed by the db manager
handler = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
logger = logging.getLogger()
logger.addHandler(handler)


print("* Create test database")
db_file = "data/test.db"

try:
    os.remove(db_file)
except OSError:
    pass

db_manager = DBManager(create_engine("sqlite:///" + db_file))
db_manager.create_tables()


print("* Test adding categories")
categories = db_manager.get_category_list()
assert(categories == odict())

id_1, message = db_manager.add_category("Big things")
assert(id_1 is not None)
assert(message == "Added new category 'Big things'.")

category = db_manager.get_category(id_1)
assert(category == {"id": id_1, "name": "Big things"})

id_2, message = db_manager.add_category("Big things")
# this logs an exception, name already exists
assert(id_2 is None)
assert(message == "Failed to add a category.")

id_3, message = db_manager.add_category("<strong>Small things</strong>")
assert(id_3 is not None)
assert(message == "Added new category 'Small things'.")

category = db_manager.get_category(id_3)
assert(category == {"id": id_3, "name": "Small things"})

categories = db_manager.get_category_list()
assert(categories == odict([(id_1, "Big things"), (id_3, "Small things")]))


print("* Test editing categories")
message = db_manager.edit_category(id_1, "Blue things")
assert(message == "Changed name of category 'Big things' to 'Blue things'.")

category = db_manager.get_category(id_1)
assert(category == {"id": id_1, "name": "Blue things"})

message = db_manager.edit_category(id_1 + id_3 + 1, "Red things")
# this logs an exception, ID does not exist
assert(message == "Failed to edit a category.")

message = db_manager.edit_category(id_3, "<strong>Green things</strong>")
assert(message == "Changed name of category 'Small things' to 'Green things'.")

categories = db_manager.get_category_list()
assert(categories == odict([(id_1, "Blue things"), (id_3, "Green things")]))


print("* Test deleting categories")
message = db_manager.delete_category(id_1)
assert(message == "Deleted category 'Blue things'.")

category = db_manager.get_category(id_1)
# this logs an exception, ID does no longer exist
assert(category is None)

message = db_manager.delete_category(id_1)
# this logs an exception, ID does no longer exist
assert(message == "Failed to delete a category.")

categories = db_manager.get_category_list()
assert(categories == odict([(id_3, "Green things")]))


print("* Test adding items")
items = db_manager.get_latest_items(10)
assert(items == odict())

id_4, message = db_manager.add_item("Leaf", "A leaf from a tree.", id_3)
assert(id_4 is not None)
assert(message == "Added new item 'Leaf'.")

item = db_manager.get_item(id_4)
assert(
        sorted(list(item.keys())) ==
        ["category_id", "created", "description", "id", "name"]
)
assert(item["category_id"] == id_3)
assert(type(item["created"] == datetime))
assert(item["description"] == "A leaf from a tree.")
assert(item["id"] == id_4)
assert(item["name"] == "Leaf")

id_5, message = db_manager.add_item("Leaf", "A leaf from a tree.", id_3)
# this logs an exception, name already exists
assert(id_5 is None)
assert(message == "Failed to add an item.")

id_6, message = db_manager.add_item(
    "Caterpillar", "A hungry caterpillar.", id_3 + 1
)
# this logs an exception, category ID does not exist
assert(id_6 is None)
assert(message == "Failed to add an item.")

time.sleep(1)  # ensure timestamps for items are distinct
id_7, message = db_manager.add_item(
    "<strong>Caterpillar</strong>", "<h1>A hungry caterpillar.</h1>", id_3
)
assert(id_7 is not None)
assert(message == "Added new item 'Caterpillar'.")

item = db_manager.get_item(id_7)
assert(
        sorted(list(item.keys())) ==
        ["category_id", "created", "description", "id", "name"]
)
assert(item["category_id"] == id_3)
assert(type(item["created"] == datetime))
assert(item["description"] == "A hungry caterpillar.")
assert(item["id"] == id_7)
assert(item["name"] == "Caterpillar")

items = db_manager.get_latest_items(10)
assert(items == odict([
    (id_7, {
        "name": "Caterpillar",
        "category_id": id_3,
        "category_name": "Green things"
    }), (id_4, {
        "name": "Leaf",
        "category_id": id_3,
        "category_name": "Green things"
    })
]))
# latest record first


print("* Test editing items")
message = db_manager.edit_item(
    id_4, "Oak leaf", "A leaf from an oak tree.", id_3
)
assert(message == "Edited item 'Oak leaf' (formerly 'Leaf').")

item = db_manager.get_item(id_4)
assert(
        sorted(list(item.keys())) ==
        ["category_id", "created", "description", "id", "name"]
)
assert(item["category_id"] == id_3)
assert(type(item["created"] == datetime))
assert(item["description"] == "A leaf from an oak tree.")
assert(item["id"] == id_4)
assert(item["name"] == "Oak leaf")

message = db_manager.edit_item(
    id_4 + id_7 + 1, "Oak leaf", "A leaf from an oak tree.", id_3
)  # this logs an exception, item ID does not exist
assert(message == "Failed to edit an item.")

message = db_manager.edit_item(
    id_4, "Oak leaf", "A leaf from an oak tree.", id_3 + 1
)  # this logs an exception, category ID does not exist
assert(message == "Failed to edit an item.")

message = db_manager.edit_item(
    id_4, "<h2>Beech leaf</h2>", "A leaf from a <strong>beech tree</strong>.",
    id_3
)
assert(message == "Edited item 'Beech leaf' (formerly 'Oak leaf').")

item = db_manager.get_item(id_4)
assert(
        sorted(list(item.keys())) ==
        ["category_id", "created", "description", "id", "name"]
)
assert(item["category_id"] == id_3)
assert(type(item["created"] == datetime))
assert(item["description"] == "A leaf from a beech tree.")
assert(item["id"] == id_4)
assert(item["name"] == "Beech leaf")

items = db_manager.get_latest_items(10)
assert(items == odict([
    (id_7, {
        "name": "Caterpillar",
        "category_id": id_3,
        "category_name": "Green things"
    }), (id_4, {
        "name": "Beech leaf",
        "category_id": id_3,
        "category_name": "Green things"
    })
]))


print("* Test deleting items")
message = db_manager.delete_item(id_4)
assert(message == "Deleted item 'Beech leaf'.")

item = db_manager.get_item(id_4)
assert(item is None)

message = db_manager.delete_item(id_4)
assert(message == "Failed to delete an item.")

items = db_manager.get_latest_items(10)
assert(items == odict([
    (id_7, {
        "name": "Caterpillar",
        "category_id": id_3,
        "category_name": "Green things"
    })
]))


print("* Test getting items by category")
items = db_manager.get_category_items(id_3)
assert(items == odict([(id_7, "Caterpillar")]))

items = db_manager.get_category_items(id_3 + 1)
assert(items == odict())


print("* Delete test database")
try:
    os.remove(db_file)
except OSError:
    pass


print("* Done")
