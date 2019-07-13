#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Fill database with sample content.

Written by Nikolaus Ruf
"""

from sqlalchemy import create_engine
import time

from catalog import DBManager

db_file = "data/catalog.db"
db_manager = DBManager(create_engine("sqlite:///" + db_file))

user_id = db_manager.get_or_add_user_id("test_user")

id_ = db_manager.add_category("Big things", user_id)[0]
db_manager.add_item("Elephant", "A gray pachyderm.", id_, user_id)
time.sleep(1)  # ensure timestamps for items are distinct
db_manager.add_item("House", "Where I live.", id_, user_id)
time.sleep(1)
db_manager.add_item("Moon", "Where I want to go.", id_, user_id)

id_ = db_manager.add_category("Small things", user_id)[0]
time.sleep(1)
db_manager.add_item("Mouse", "A gray rodent.", id_, user_id)
time.sleep(1)
db_manager.add_item("Another mouse", "A brown rodent.", id_, user_id)
time.sleep(1)
db_manager.add_item(
    "Speck of dust", "You really should clean up.", id_, user_id
)

id_ = db_manager.add_category("Red things", user_id)[0]
time.sleep(1)
db_manager.add_item("Rubber ball", "Very bouncy.", id_, user_id)
time.sleep(1)
db_manager.add_item("Porsche 911", "Vroom!", id_, user_id)
time.sleep(1)
db_manager.add_item("Fly agaric", "Eat at your own risk.", id_, user_id)

id_ = db_manager.add_category("Blue things", user_id)[0]
time.sleep(1)
db_manager.add_item("Parrot", "It's dead (obviously).", id_, user_id)
time.sleep(1)
db_manager.add_item("Ocean", "So blue!", id_, user_id)
