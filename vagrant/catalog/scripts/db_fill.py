"""Fill database with sample content.

Written by Nikolaus Ruf
"""

from sqlalchemy import create_engine
import time

from catalog import DBManager

db_file = "data/catalog.db"
db_manager = DBManager(create_engine("sqlite:///" + db_file))

id_ = db_manager.add_category("Big things")[0]
db_manager.add_item("Elephant", "A gray pachyderm.", id_)
time.sleep(1)  # ensure timestamps for items are distinct
db_manager.add_item("House", "Where I live.", id_)
time.sleep(1)
db_manager.add_item("Moon", "Where I want to go.", id_)

id_ = db_manager.add_category("Small things")[0]
time.sleep(1)
db_manager.add_item("Mouse", "A gray rodent.", id_)
time.sleep(1)
db_manager.add_item("Another mouse", "A brown rodent.", id_)
time.sleep(1)
db_manager.add_item("Speck of dust", "You really should clean up.", id_)

id_ = db_manager.add_category("Red things")[0]
time.sleep(1)
db_manager.add_item("Rubber ball", "Very bouncy.", id_)
time.sleep(1)
db_manager.add_item("Porsche 911", "Vroom!", id_)
time.sleep(1)
db_manager.add_item("Fly agaric", "Eat at your own risk.", id_)

id_ = db_manager.add_category("Blue things")[0]
time.sleep(1)
db_manager.add_item("Parrot", "It's dead (obviously).", id_)
time.sleep(1)
db_manager.add_item("Ocean", "So blue!", id_)
