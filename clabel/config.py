# coding: utf-8

import os
import sys
import jpype
import logging.config

# reload(sys)
# sys.setdefaultencoding('utf-8')

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
LEXICON_FIXED_SENTIMENT_WORDS_FILE = os.path.join(RESOURCE_DIR, 'lexicon', 'fixed_sentiment', '情感词汇本体.xlsx')
# 程度词词库
LEXICON_DEGREE_WORDS_FILE = os.path.join(RESOURCE_DIR, 'lexicon', 'degree', '程度词.txt')

CATEGORY = 'mobile'

# os.path.join(RESOURCE_DIR, 'dp', 'dp.CF')
LEXICON_FEATURE_RAW = os.path.join(RESOURCE_DIR, CATEGORY, 'mobile.features.raw')
LEXICON_FEATURE_REVISED = os.path.join(RESOURCE_DIR, CATEGORY, 'mobile.features.revised')

# PMI search url
PMI_SEARCH_URL = 'http://123.56.26.142:13148/query/api/v1.0/%s'

DB_FILE = os.path.join(RESOURCE_DIR, 'db', 'label.db')

HANLP_MODEL_DIR = os.path.join(RESOURCE_DIR, 'model', 'external_model_data', 'hanlp')

LTP_MODEL_DIR = os.path.join(RESOURCE_DIR, 'model', 'external_model_data', 'ltp')
CUSTOM_TOKEN_FILE = os.path.join('lexicon', 'ltp', 'custom.token.txt')
CUSTOM_POS_FILE = os.path.join('lexicon', 'ltp', 'custom.pos.txt')

DEFAULT_PARSER = 'hanlp'

LM_MODEL_DIR = os.path.join(RESOURCE_DIR, 'model', 'internal_model', 'lm')


jars_hanlp = [HANLP_MODEL_DIR, os.path.join(HANLP_MODEL_DIR, 'hanlp.jar')]
jars_lm = [os.path.join(LM_MODEL_DIR, 'lm.jar'), os.path.join(LM_MODEL_DIR, 'berkeleylm.jar')]
jars = jars_hanlp + jars_lm

separator = ';' if sys.platform.startswith('win') else ':'
classpath = separator.join(jars)
classpath_option = '-Djava.class.path=' + classpath
# -Dfile.encoding=UTF8
jpype.startJVM(jpype.getDefaultJVMPath(), classpath_option, '-Xrs', '-Xmx1024m')
