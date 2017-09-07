# coding: utf-8

import os
import re
import copy
import logging
import openpyxl

from collections import defaultdict

from clabel.helper import utils
from clabel.config import LEXICON_DEGREE_WORDS_FILE
from clabel.config import LEXICON_IRRELEVANT_WORDS_DIR
from clabel.config import LEXICON_FIXED_SENTIMENT_WORDS_FILE

logger = logging.getLogger(__file__)


class IrrelevantLexicon(object):
    """
    无关词库，人名、地名、品牌、型号等
    """

    _lexicon = defaultdict(set)

    '''加载无关词'''
    for word_file in os.listdir(LEXICON_IRRELEVANT_WORDS_DIR):
        _lexicon[word_file.replace('.txt', '')] = set(
            [w.decode('utf-8') for w in utils.read_file(os.path.join(LEXICON_IRRELEVANT_WORDS_DIR, word_file))])

    @staticmethod
    def is_irrelevant_word(word):
        """
        判断是否是无关词
        :param word:
        :return:
        """
        word = utils.convert2unicode(word)
        return IrrelevantLexicon.is_brand(word) or IrrelevantLexicon.is_model(word) or IrrelevantLexicon.is_personals(
            word) or IrrelevantLexicon.is_color(word) or IrrelevantLexicon.is_place(
            word) or IrrelevantLexicon.is_position(word) or IrrelevantLexicon.is_date(word)

    @staticmethod
    def is_brand(word):
        return word in IrrelevantLexicon._lexicon['brand']

    @staticmethod
    def is_model(word):
        return (word in IrrelevantLexicon._lexicon['model']) or (re.match(r'^[a-zA-Z]+[0-9]$', word) is not None)

    @staticmethod
    def is_personals(word):
        return utils.convert2unicode(word) in IrrelevantLexicon._lexicon['personal']

    @staticmethod
    def is_color(word):
        return utils.convert2unicode(word) in IrrelevantLexicon._lexicon['color']

    @staticmethod
    def is_place(word):
        return utils.convert2unicode(word) in IrrelevantLexicon._lexicon['place']

    @staticmethod
    def is_position(word):
        return utils.convert2unicode(word) in IrrelevantLexicon._lexicon['position']

    @staticmethod
    def is_date(word):
        return utils.convert2unicode(word) in IrrelevantLexicon._lexicon['date']

    @staticmethod
    def get_words(word_type):
        return copy.deepcopy(IrrelevantLexicon._lexicon[word_type])


class FixedSentimentLexicon(object):
    """
    通用情感词库，这里的情感词的极性是固定的，不会随着上下文环境的改变而改变
    """

    _positives = set()
    _negatives = set()
    _neutrals = set()

    '''加载情感词'''
    wb = openpyxl.load_workbook(LEXICON_FIXED_SENTIMENT_WORDS_FILE)
    sheet = wb.active

    __opinions = {
        0: _neutrals,
        1: _positives,
        2: _negatives
    }

    for row in list(sheet.rows)[1:]:
        main_polar = row[6].value
        aux_polar = row[9].value

        if main_polar not in __opinions:
            continue

        if aux_polar is None or main_polar == aux_polar:
            __opinions[main_polar].add(row[0].value)

    @staticmethod
    def is_positive(word):
        return utils.convert2unicode(word) in FixedSentimentLexicon._positives

    @staticmethod
    def is_negative(word):
        return utils.convert2unicode(word) in FixedSentimentLexicon._negatives

    @staticmethod
    def is_neutral(word):
        return utils.convert2unicode(word) in FixedSentimentLexicon._neutrals

    @staticmethod
    def get_polar(word):
        word = utils.convert2unicode(word)
        if word in FixedSentimentLexicon._positives:
            return '+'
        elif word in FixedSentimentLexicon._negatives:
            return '-'
        elif word in FixedSentimentLexicon._neutrals:
            return '0'
        else:
            return 'x'


class DegreeLexicon(object):
    """程度词表"""

    _degrees = defaultdict(set)

    __current_degree = ''
    for word in utils.iter_file(LEXICON_DEGREE_WORDS_FILE):
        if word.startswith('['):
            word = word.replace('[', '').replace(']', '')
            __current_degree = word

        _degrees[__current_degree].add(utils.convert2unicode(word))

    @staticmethod
    def is_degree(word):
        word = utils.convert2unicode(word)

        for head in DegreeLexicon._degrees:
            if word in DegreeLexicon._degrees[head]:
                return True

        return False

    @staticmethod
    def get_head(word):
        word = utils.convert2unicode(word)

        for head in DegreeLexicon._degrees:
            if word in DegreeLexicon._degrees[head]:
                return head

        return None
