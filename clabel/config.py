# coding: utf-8

import os
import sys
import logging.config

reload(sys)
sys.setdefaultencoding('utf-8')

APP_DIR = os.path.dirname(os.path.dirname(__file__))
ROOT_DIR = os.path.join(APP_DIR, 'clabel')
RESOURCE_DIR = os.path.join(APP_DIR, 'resource')
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

# 无关词
LEXICON_IRRELEVANT_WORDS_DIR = os.path.join(RESOURCE_DIR, 'lexicon', 'irrelevant')
# 情感固定的通用情感词
LEXICON_FIXED_SENTIMENT_WORDS_FILE = os.path.join(RESOURCE_DIR, 'lexicon', 'fixed_sentiment', u'情感词汇本体.xlsx')
# 程度词词库
LEXICON_DEGREE_WORDS_FILE = os.path.join(RESOURCE_DIR, 'lexicon', 'degree', u'程度词.txt')

CATEGORY = 'mobile'

# os.path.join(RESOURCE_DIR, 'dp', 'dp.CF')
LEXICON_FEATURE_RAW = os.path.join(RESOURCE_DIR, CATEGORY, 'mobile.features.raw')
LEXICON_FEATURE_REVISED = os.path.join(RESOURCE_DIR, CATEGORY, 'mobile.features.revised')

# PMI search url
PMI_SEARCH_URL = 'http://123.56.26.142:13148/query/api/v1.0/%s'

DB_FILE = os.path.join(RESOURCE_DIR, 'db', 'label.db')

LTP_MODEL_DIR = os.path.join(RESOURCE_DIR, 'ltp_data')
CUSTOM_TOKEN_FILE = os.path.join('lexicon', 'ltp', 'custom.token.txt')
CUSTOM_POS_FILE = os.path.join('lexicon', 'ltp', 'custom.pos.txt')
