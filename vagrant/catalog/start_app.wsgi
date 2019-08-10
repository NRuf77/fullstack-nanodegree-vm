#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Entry point for serving catalog app from Apache2.

Written by Nikolaus Ruf
"""

import os
import sys

sys.path.append(os.getcwd())
# Python under Ubuntu appears to not automatically look for modules in the
# current working directory; this hack would not be necessary under Windows

# noinspection PyUnresolvedReferences
from start_script import app as application, logger

logger.info("Start catalog app in server mode")
