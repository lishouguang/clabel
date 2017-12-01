# coding: utf-8

import os
import sys
import jieba
import jpype

from logging import config as logconfig


APP_DIR = os.path.dirname(__file__)
ROOT_DIR = os.path.dirname(APP_DIR)
RESOURCE_DIR = os.path.join(ROOT_DIR, 'zresource')
TMP_DIR = os.path.join(RESOURCE_DIR, 'tmp')

logconfig.fileConfig(os.path.join(ROOT_DIR, 'logging.ini'))


APP_RESOURCE_DIR = os.path.join(RESOURCE_DIR, os.path.basename(APP_DIR))

'''lexicon'''
# 无关词
LEXICON_IRRELEVANT_WORDS_DIR = os.path.join(APP_RESOURCE_DIR, 'lexicon', 'irrelevant')
# 情感固定的通用情感词
LEXICON_FIXED_SENTIMENT_WORDS_FILE = os.path.join(APP_RESOURCE_DIR, 'lexicon', 'fixed_sentiment', '情感词汇本体.xlsx')
# 程度词词库
LEXICON_DEGREE_WORDS_FILE = os.path.join(APP_RESOURCE_DIR, 'lexicon', 'degree', '程度词.txt')


'''syntax parser'''
DEFAULT_PARSER = 'comb'


'''LTP Model'''
LTP_MODEL_DIR = os.path.join(APP_RESOURCE_DIR, 'model', 'ltp')
CUSTOM_TOKEN_FILE = os.path.join(APP_RESOURCE_DIR, 'lexicon', 'ltp', 'custom.token.txt')
CUSTOM_POS_FILE = os.path.join(APP_RESOURCE_DIR, 'lexicon', 'ltp', 'custom.pos.txt')


'''HanLP Model'''
HANLP_MODEL_DIR = os.path.join(APP_RESOURCE_DIR, 'model', 'hanlp')

jars_hanlp = [HANLP_MODEL_DIR, os.path.join(HANLP_MODEL_DIR, 'hanlp-1.3.4.jar')]

separator = ';' if sys.platform.startswith('win') else ':'
classpath = separator.join(jars_hanlp)
classpath_option = '-Djava.class.path=' + classpath

# -Dfile.encoding=UTF8
print(jpype.isJVMStarted())
if not jpype.isJVMStarted():
    jpype.startJVM(jpype.getDefaultJVMPath(), classpath_option, '-Xrs', '-Xmx2048m')


def add_user_words(words):
    for word, freq, tag in words:
        jieba.add_word(word, freq=freq, tag=tag)


# 更改jieba默认字典
# jieba.set_dictionary(os.path.join(RESOURCE_DIR, 'nlp', 'lexicon', 'jieba', 'dict.big.txt'))
