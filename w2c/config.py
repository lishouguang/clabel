# coding: utf-8

import os
from logging import config as logconfig


APP_DIR = os.path.dirname(__file__)
ROOT_DIR = os.path.dirname(APP_DIR)
RESOURCE_DIR = os.path.join(ROOT_DIR, 'zresource')
TMP_DIR = os.path.join(RESOURCE_DIR, 'tmp')

APP_RESOURCE_DIR = os.path.join(RESOURCE_DIR, os.path.basename(APP_DIR))

DEFAULT_MODEL_FILE = os.path.join(APP_RESOURCE_DIR, 'w2c.model')

WORD_POS_SEPARATOR = '\001'

logconfig.fileConfig(os.path.join(ROOT_DIR, 'logging.ini'))

