# coding: utf-8

import os
import logging.config

APP_DIR = os.path.dirname(os.path.dirname(__file__))
ROOT_DIR = os.path.join(APP_DIR, 'clabel')
RESOURCE_DIR = os.path.join(APP_DIR, 'zresource')
TMP_DIR = os.path.join(RESOURCE_DIR, 'tmp')

logging.config.fileConfig(os.path.join(ROOT_DIR, 'logging.ini'))

# NLP_API_LOCAL = True

# NLP_SERVER_URL = 'http://120.77.204.144:9000/'
# NLP_SERVER_URL = 'http://127.0.0.1:9000/'
NLP_POS_SEPARATOR = '\001'
NLP_SENT_SEPARATORS = ['。', '!', '?', '！', '？', ',', '，']
# NLP_SENT_SEPARATORS = ['。', '!', '?', '！', '？']

FREQUENT_MIN_SUPPORT = 0.0012
FREQUENT_FEATURE_POSES = ['NN']


CATEGORY = 'mobile'

# os.path.join(RESOURCE_DIR, 'dp', 'dp.CF')
LEXICON_FEATURE_RAW = os.path.join(RESOURCE_DIR, CATEGORY, 'mobile.features.raw')
LEXICON_FEATURE_REVISED = os.path.join(RESOURCE_DIR, CATEGORY, 'mobile.features.revised')

# PMI search url
PMI_SEARCH_URL = 'http://123.56.26.142:13148/query/api/v1.0/%s'

DB_FILE = os.path.join(RESOURCE_DIR, 'db', 'label.db')
