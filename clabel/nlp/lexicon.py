# coding: utf-8

import os
import re
import copy
import logging
import openpyxl

from collections import defaultdict

from clabel.helper import utils

logger = logging.getLogger(__file__)


class IrrelevantLexicon(object):
    """
    无关词库，人名、地名、品牌、型号等
    """

    def __init__(self, lexicon_dir):
        self._lexicon = defaultdict(set)

        '''读取文件，加载词'''
        for word_file in os.listdir(lexicon_dir):
            word_type = word_file.replace('.txt', '')
            words = set([w.decode('utf-8') for w in utils.read_file(os.path.join(lexicon_dir, word_file)) if w])
            self._lexicon[word_type] = words

    def is_irrelevant_word(self, word):
        """
        判断是否是无关词
        :param word:
        :return:
        """
        word = utils.convert2unicode(word)
        return self.is_brand(word) or self.is_model(word) or self.is_personals(
            word) or self.is_color(word) or self.is_place(
            word) or self.is_position(word) or self.is_date(word)

    def is_brand(self, word):
        return word in self._lexicon['brand']

    def is_model(self, word):
        return (word in self._lexicon['model']) or (re.match(r'^[a-zA-Z]+[0-9]$', word) is not None)

    def is_personals(self, word):
        return utils.convert2unicode(word) in self._lexicon['personal']

    def is_color(self, word):
        return utils.convert2unicode(word) in self._lexicon['color']

    def is_place(self, word):
        return utils.convert2unicode(word) in self._lexicon['place']

    def is_position(self, word):
        return utils.convert2unicode(word) in self._lexicon['position']

    def is_date(self, word):
        return utils.convert2unicode(word) in self._lexicon['date']

    def get_words(self, word_type):
        return copy.deepcopy(self._lexicon[word_type])


class FixedSentimentLexicon(object):
    """
    通用情感词库，这里的情感词的极性是固定的，不会随着上下文环境的改变而改变
    """

    def __init__(self, lexicon_file):
        positives = set()
        negatives = set()
        neutrals = set()

        '''加载情感词'''
        wb = openpyxl.load_workbook(lexicon_file)
        sheet = wb.active

        __opinions = {
            0: neutrals,
            1: positives,
            2: negatives
        }

        for row in list(sheet.rows)[1:]:
            main_polar = row[6].value
            aux_polar = row[9].value

            if main_polar not in __opinions:
                continue

            if aux_polar is None or main_polar == aux_polar:
                __opinions[main_polar].add(row[0].value)

        self._positives = positives
        self._negatives = negatives
        self._neutrals = neutrals

    def is_positive(self, word):
        return utils.convert2unicode(word) in self._positives

    def is_negative(self, word):
        return utils.convert2unicode(word) in self._negatives

    def is_neutral(self, word):
        return utils.convert2unicode(word) in self._neutrals

    def get_polar(self, word):
        word = utils.convert2unicode(word)
        if word in self._positives:
            return '+'
        elif word in self._negatives:
            return '-'
        elif word in self._neutrals:
            return '0'
        else:
            return 'x'


class DegreeLexicon(object):
    """程度词表"""

    def __init__(self, lexicon_file):
        degrees = defaultdict(set)

        __current_degree = ''
        for word in utils.iter_file(lexicon_file):
            if word.startswith('['):
                word = word.replace('[', '').replace(']', '')
                __current_degree = word

            degrees[__current_degree].add(utils.convert2unicode(word))

        self._degrees = degrees

    def is_degree(self, word):
        word = utils.convert2unicode(word)

        for head in self._degrees:
            if word in self._degrees[head]:
                return True

        return False

    def get_head(self, word):
        word = utils.convert2unicode(word)

        for head in self._degrees:
            if word in self._degrees[head]:
                return head

        return None


class FormattedFeature(object):

    def __init__(self, f):
        lines = utils.read_file(f)

        self._clusters = {}

        for line in lines:
            if line.startswith('='):
                continue

            features = [f for f in line.split(' ') if f.strip() != '']
            self._clusters[features[0]] = set(features)

        self.__features = set()
        for head in self._clusters:
            for feature in self._clusters[head]:
                self.__features.add(feature)

    def get_head(self, feature):
        for head in self._clusters:
            if feature in self._clusters[head]:
                return head
        return None

    def get_heads(self):
        return self._clusters.keys()

    def is_feature(self, f):
        return f in self.__features


from clabel.config import LEXICON_DEGREE_WORDS_FILE
from clabel.config import LEXICON_IRRELEVANT_WORDS_DIR
from clabel.config import LEXICON_FIXED_SENTIMENT_WORDS_FILE

degreeLexicon = DegreeLexicon(LEXICON_DEGREE_WORDS_FILE)
irrelevantLexicon = IrrelevantLexicon(LEXICON_IRRELEVANT_WORDS_DIR)
fixedSentimentLexicon = FixedSentimentLexicon(LEXICON_FIXED_SENTIMENT_WORDS_FILE)

