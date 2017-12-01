# coding: utf-8

import os
import sys
import jpype
import logging.config

APP_DIR = os.path.dirname(os.path.dirname(__file__))
ROOT_DIR = os.path.join(APP_DIR, 'clabel')
RESOURCE_DIR = os.path.join(APP_DIR, 'zresource')
TMP_DIR = os.path.join(RESOURCE_DIR, 'tmp')

logging.config.fileConfig(os.path.join(APP_DIR, 'logging.ini'))

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


'''设置jvm classpath'''
separator = ';' if sys.platform.startswith('win') else ':'

'''BerkerleyLM的classpath'''
LM_RESOURCE_DIR = os.path.join(RESOURCE_DIR, 'lm')
LM_MODEL_DIR = os.path.join(LM_RESOURCE_DIR, 'model', 'berkerley')
jars_lm = [os.path.join(LM_MODEL_DIR, 'lm.jar'), os.path.join(LM_MODEL_DIR, 'berkeleylm.jar')]

'''Hanlp的classpath'''
NLP_RESOURCE_DIR = os.path.join(RESOURCE_DIR, 'nlp')
HANLP_MODEL_DIR = os.path.join(NLP_RESOURCE_DIR, 'model', 'hanlp')
jars_hanlp = [HANLP_MODEL_DIR, os.path.join(HANLP_MODEL_DIR, 'hanlp-1.3.4.jar')]

classpath = separator.join(jars_lm + jars_hanlp)
classpath_option = '-Djava.class.path=' + classpath

# -Dfile.encoding=UTF8
if not jpype.isJVMStarted():
    jpype.startJVM(jpype.getDefaultJVMPath(), classpath_option, '-Xrs', '-Xmx2048m')
