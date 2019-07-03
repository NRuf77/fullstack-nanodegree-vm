"""Create an empty sqlite database.

Written by Nikolaus Ruf
"""

import os
from sqlalchemy import create_engine

from catalog.database import DBManager

db_file = "data/catalog.db"

try:
    os.remove(db_file)
except OSError:
    pass

db_manager = DBManager(create_engine("sqlite:///" + db_file))
db_manager.create_tables()
