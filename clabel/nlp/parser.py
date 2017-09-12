# coding: utf-8

import os
import re

import queue
import logging

from pyltp import Parser
from pyltp import Segmentor
from pyltp import Postagger
from pyltp import SentenceSplitter
from pyltp import NamedEntityRecognizer

from clabel.helper import utils
from clabel.config import RESOURCE_DIR
from clabel.config import LTP_MODEL_DIR
from clabel.config import CUSTOM_POS_FILE
from clabel.config import CUSTOM_TOKEN_FILE

logger = logging.getLogger(__file__)


def ssplit(txt):
    """
    对文本分句/分词
    :param txt: 一段文本
    :return: [[word1, word2, ...], [word3, word4, ...], ...]
    """

    return [x for x in re.split(r'[\s,，.。:：!！?？、]', txt) if x]


_segmentor = Segmentor()
_segmentor.load_with_lexicon(os.path.join(LTP_MODEL_DIR, 'cws.model'), CUSTOM_TOKEN_FILE)
# _segmentor.load(os.path.join(MODEL_DIR, 'cws.model'))


def segment(txt):
    """
    分词
    :param txt: 文本
    :return: [word1, word2, ...]
    """
    return list(_segmentor.segment(txt))


_tagger = Postagger()
_tagger.load_with_lexicon(os.path.join(LTP_MODEL_DIR, 'pos.model'), CUSTOM_POS_FILE)
# _tagger.load()


def pos(text):
    """
    对文本进行词性标注，附带了分句
    :param text:
    :return: [Token1, Token2, ...]
    """
    tokenized = segment(text)
    tags = _tagger.postag(tokenized)

    result = []
    for i, w, t in zip(list(range(len(tokenized))), tokenized, tags):
        result.append(Token(w, t, i))

    return result


def pos_with_cache(text):
    """
    带缓存的标注
    :param text:
    :return:
    """
    result = _get_from_cache(text)

    if result is None:
        result = pos(text)
        _set_cache(text, result)

    return result


_ner = NamedEntityRecognizer()
_ner.load(os.path.join(LTP_MODEL_DIR, 'ner.model'))


def ner(raw):
    tokens = pos(raw)
    return list(_ner.recognize([t.word for t in tokens], [t.pos for t in tokens]))


_parser = Parser()
_parser.load(os.path.join(LTP_MODEL_DIR, 'parser.model'))


def parse2relations(text):
    """
    依存句法分析
    :param text:
    :return:
    :rtype: list of Relation
    """
    tokens = pos(text)

    words = [t.word for t in tokens]
    tags = [t.pos for t in tokens]

    arcs = _parser.parse(words, tags)

    result = []
    for i, w, p, a in zip(list(range(len(words))), words, tags, arcs):
        head_token = Token(words[a.head - 1] if a.head > 0 else 'Root', tags[a.head - 1] if a.head > 0 else 'Root', a.head-1)
        dep_token = Token(w, p, i)

        result.append(Relation(a.relation, head_token, dep_token))

    return result


def parse2sents(txt):
    """
    解析一个句子文本
    :param txt:
    :return: Sentence对象
    :rtype: list of Sentence
    """
    sents = []

    for sent_txt in ssplit(txt):
        sent_relations = parse2relations(sent_txt)
        tokens = set()

        for relation in sent_relations:
            if relation.token1.word != 'ROOT':
                tokens.add(relation.token1)
            tokens.add(relation.token2)

        tokens = sorted(tokens, key=lambda t: t.id)

        # sent = Sentence(''.join([w.word for w in tokens]))
        sent = Sentence(sent_txt)

        sent.tokens = tokens
        sent.relations = sent_relations

        sents.append(sent)

    return sents


__pos_cache = dict()
__queue = queue.Queue(500000)


def _get_from_cache(text):
    return __pos_cache.get(text)


def _set_cache(text, result):
    __pos_cache[text] = result
    __queue.put(text)

    if __queue.full():
        key = __queue.get()
        __pos_cache.pop(key)


class Token(object):

    def __init__(self, word, pos, index=-1):
        self.word = word
        self.pos = pos
        self.id = index

    def __eq__(self, other):
        if other is None or not isinstance(other, Token):
            return False
        return self.id == other.id and self.word == other.word and self.pos == other.pos

    def __str__(self):
        return '%s/%d/%s' % (self.word, self.id, self.pos)

    def __hash__(self):
        return hash('%s/%d/%s' % (self.word, self.id, self.pos))


class Relation(object):

    def __init__(self, relation, token1, token2):
        self.relation = relation
        self.token1 = token1
        self.token2 = token2

        self.format = '%s(%s, %s)' % (self.relation, self.token1.pos, self.token2.pos)

    def match(self, relation_format):
        return self.format.lower() == relation_format.lower()

    def __str__(self):
        return '%s(%s/%s, %s/%s)' % (self.relation, self.token1.word, self.token1.pos, self.token2.word, self.token2.pos)


class Sentence(object):

    def __init__(self, raw):
        self.__raw = raw
        self.__tokens = []
        self.__relations = []

    @property
    def raw(self):
        return self.__raw

    @raw.setter
    def raw(self, value):
        self.__raw = value

    @property
    def tokens(self):
        return self.__tokens

    @tokens.setter
    def tokens(self, value):
        self.__tokens = value

    @property
    def relations(self):
        """
        :rtype: list of Relation
        """
        return self.__relations

    @relations.setter
    def relations(self, value):
        self.__relations = value

    def get_token(self, id_or_word):

        if isinstance(id_or_word, int):
            return self.__tokens[id_or_word - 1]

        if isinstance(id_or_word, str):
            for token in self.__tokens:
                if token.word == id_or_word:
                    return token

        return None

    def get_root_relation(self):
        for relation in self.__relations:
            if relation.relation == 'HED':
                return relation

        return None

    def find_relations(self, rel, token1_pos=None, token2_pos=None):
        for relation in self.__relations:

            cdn = relation.relation == rel
            cdn1 = (relation.token1.pos == token1_pos) if token1_pos else True
            cdn2 = (relation.token2.pos == token2_pos) if token2_pos else True

            if cdn and cdn1 and cdn2:
                return relation

        return None

    def __str__(self):
        return ' '.join([str(relation) for relation in self.__relations])

