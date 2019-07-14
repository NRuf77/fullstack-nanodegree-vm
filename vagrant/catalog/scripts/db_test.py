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
import sys
import time

if os.getcwd() not in sys.path:
    sys.path.append(os.getcwd())
# this script should be run from the 'catalog' directory using
#     $ python scripts/db_test.py
# but Python under Ubuntu appears to not automatically look for modules in the
# current working directory; this hack would not be necessary under Windows

from catalog import DBManager


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


print("* Test adding users")
user_id = db_manager.get_or_add_user_id("test_user")
assert(user_id is not None)

user_id_2 = db_manager.get_or_add_user_id("")
assert(user_id_2 is None)

user_id_3 = db_manager.get_or_add_user_id("</br>")
assert(user_id_3 is None)

user_id_4 = db_manager.get_or_add_user_id("test_user")
assert(user_id_4 == user_id)


print("* Test adding categories")
categories = db_manager.get_category_list()
assert(categories == odict())

id_1, message = db_manager.add_category("Big things", user_id)
assert(id_1 is not None)
assert(message == "Added new category 'Big things'.")

category = db_manager.get_category(id_1)
assert(category == {"id": id_1, "name": "Big things", "user_id": user_id})

id_2, message = db_manager.add_category("Big things", user_id)
# this logs an exception, name already exists
assert(id_2 is None)
assert(message == "Failed to add a category.")

id_2, message = db_manager.add_category("", user_id)
assert(id_2 is None)
assert(message == "Invalid category name.")

id_3, message = db_manager.add_category(
    "<strong>Small things</strong>", user_id
)
assert(id_3 is not None)
assert(message == "Added new category 'Small things'.")

category = db_manager.get_category(id_3)
assert(category == {"id": id_3, "name": "Small things", "user_id": user_id})

categories = db_manager.get_category_list()
assert(categories == odict([(id_1, "Big things"), (id_3, "Small things")]))

categories = db_manager.get_category_list(user_id)
assert(categories == odict([(id_1, "Big things"), (id_3, "Small things")]))


print("* Test editing categories")
message = db_manager.edit_category(id_1, "Blue things")
assert(message == "Changed name of category 'Big things' to 'Blue things'.")

category = db_manager.get_category(id_1)
assert(category == {"id": id_1, "name": "Blue things", "user_id": user_id})

message = db_manager.edit_category(id_1 + id_3 + 1, "Red things")
# this logs an exception, ID does not exist
assert(message == "Failed to edit a category.")

message = db_manager.edit_category(id_1, "")
assert(message == "Invalid category name.")

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

id_4, message = db_manager.add_item(
    "Leaf", "A leaf from a tree.", id_3, user_id
)
assert(id_4 is not None)
assert(message == "Added new item 'Leaf'.")

item = db_manager.get_item(id_4)
assert(
        sorted(list(item.keys())) ==
        ["category_id", "created", "description", "id", "name", "user_id"]
)
assert(item["category_id"] == id_3)
assert(type(item["created"] == datetime))
assert(item["description"] == "A leaf from a tree.")
assert(item["id"] == id_4)
assert(item["name"] == "Leaf")
assert(item["user_id"] == user_id)

id_5, message = db_manager.add_item(
    "Leaf", "A leaf from a tree.", id_3, user_id
)
# this logs an exception, name already exists
assert(id_5 is None)
assert(message == "Failed to add an item.")

id_5, message = db_manager.add_item("", "A leaf from a tree.", id_3, user_id)
assert(id_5 is None)
assert(message == "Invalid item name.")

id_6, message = db_manager.add_item(
    "Caterpillar", "A hungry caterpillar.", id_3 + 1, user_id
)
# this logs an exception, category ID does not exist
assert(id_6 is None)
assert(message == "Failed to add an item.")

time.sleep(1)  # ensure timestamps for items are distinct
id_7, message = db_manager.add_item(
    "<strong>Caterpillar</strong>", "<h1>A hungry caterpillar.</h1>", id_3,
    user_id
)
assert(id_7 is not None)
assert(message == "Added new item 'Caterpillar'.")

item = db_manager.get_item(id_7)
assert(
        sorted(list(item.keys())) ==
        ["category_id", "created", "description", "id", "name", "user_id"]
)
assert(item["category_id"] == id_3)
assert(type(item["created"] == datetime))
assert(item["description"] == "A hungry caterpillar.")
assert(item["id"] == id_7)
assert(item["name"] == "Caterpillar")
assert(item["user_id"] == user_id)

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
        ["category_id", "created", "description", "id", "name", "user_id"]
)
assert(item["category_id"] == id_3)
assert(type(item["created"] == datetime))
assert(item["description"] == "A leaf from an oak tree.")
assert(item["id"] == id_4)
assert(item["name"] == "Oak leaf")
assert(item["user_id"] == user_id)

message = db_manager.edit_item(
    id_4 + id_7 + 1, "Oak leaf", "A leaf from an oak tree.", id_3
)  # this logs an exception, item ID does not exist
assert(message == "Failed to edit an item.")

message = db_manager.edit_item(
    id_4, "", "A leaf from an oak tree.", id_3
)
assert(message == "Invalid item name.")

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
        ["category_id", "created", "description", "id", "name", "user_id"]
)
assert(item["category_id"] == id_3)
assert(type(item["created"] == datetime))
assert(item["description"] == "A leaf from a beech tree.")
assert(item["id"] == id_4)
assert(item["name"] == "Beech leaf")
assert(item["user_id"] == user_id)

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


print("* Test foreign key delete on cascade")
db_manager.delete_category(id_3)
items = db_manager.get_category_items(id_3)
assert(items == odict())


print("* Delete test database")
try:
    os.remove(db_file)
except OSError:
    pass


print("* Done")
# everything works as intended if this line is reached; exception messages
# that are logged but do not abort the script are fine
