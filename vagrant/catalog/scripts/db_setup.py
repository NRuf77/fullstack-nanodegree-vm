#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Create an empty sqlite database.

This script needs to be called from the main project directory as
scripts/db_setup.py since relative paths are defined from there.

Written by Nikolaus Ruf
"""

import os
from sqlalchemy import create_engine
import sys

if os.getcwd() not in sys.path:
    sys.path.append(os.getcwd())
# this script should be run from the 'catalog' directory using
#     $ python scripts/db_setup.py
# but Python under Ubuntu appears to not automatically look for modules in the
# current working directory; this hack would not be necessary under Windows

from catalog import DBManager

db_file = "data/catalog.db"

try:
    os.remove(db_file)
except OSError:
    pass

db_manager = DBManager(create_engine("sqlite:///" + db_file))
db_manager.create_tables()
