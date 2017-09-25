# coding: utf-8

import os
import re

import queue
import logging

from abc import ABC
from abc import abstractclassmethod

import jpype

from pyltp import Segmentor
from pyltp import Postagger
from pyltp import Parser as LParser
from pyltp import NamedEntityRecognizer

from nlp.config import LTP_MODEL_DIR
from nlp.config import CUSTOM_POS_FILE
from nlp.config import CUSTOM_TOKEN_FILE
from nlp.config import DEFAULT_PARSER
from nlp.config import HANLP_MODEL_DIR


logger = logging.getLogger(__file__)


class Parser(ABC):

    def __init__(self):
        self._pos_cache = dict()
        self._queue = queue.Queue(500000)

        super(Parser, self).__init__()

    def ssplit(self, txt):
        """
        对文本分句/分词
        :param txt: 一段文本
        :return: [[word1, word2, ...], [word3, word4, ...], ...]
        """
        self
        return [x for x in re.split(r'[\s,，.。:：!！?？、]', txt) if x]

    @abstractclassmethod
    def segment(self, txt):
        """
        分词
        :param txt: 文本
        :return: [word1, word2, ...]
        """
        pass

    @abstractclassmethod
    def pos(self, txt, cache=False):
        """
        对文本进行词性标注，附带了分句
        :param txt:
        :param cache:
        :return: [Token1, Token2, ...]
        """
        pass

    @abstractclassmethod
    def ner(self, txt):
        pass

    @abstractclassmethod
    def parse2relations(self, txt):
        """
        依存句法分析
        :param txt:
        :return: [Relation, Relation, ...]
        :rtype: list of Relation
        """
        pass

    @abstractclassmethod
    def parse2sents(self, txt):
        """
        解析一个句子文本
        :param txt:
        :return: [Sentence, Sentence, ...]
        :rtype: list of Sentence
        """
        pass

    def _get_from_cache(self, txt):
        return self._pos_cache.get(txt)

    def _set_cache(self, txt, result):
        self._pos_cache[txt] = result
        self._queue.put(txt)

        if self._queue.full():
            key = self._queue.get()
            self._pos_cache.pop(key)


class LTPParser(Parser):
    """
    基于LTP实现的Parser

    LTP对用户自定义词典的支持不是很好，http://www.ltp-cloud.com/support/
    1. 扩展自定义词典后，需要重新编译LTP
    2. 分词支持自定义词典，但词性标注不支持
    """

    def __init__(self, ltp_model_dir, custom_seg_file=None, custom_pos_file=None):
        """
        :param ltp_model_dir:
        """

        super(LTPParser, self).__init__()

        self._ltp_dir = ltp_model_dir

        '''加载分词模型'''
        seg_model_file = os.path.join(self._ltp_dir, 'cws.model')
        self._segmentor = Segmentor()
        if custom_seg_file:
            self._segmentor.load_with_lexicon(seg_model_file, custom_seg_file)
        else:
            self._segmentor.load(seg_model_file)

        '''加载词性标注模型'''
        self._tagger = Postagger()
        pos_model_file = os.path.join(self._ltp_dir, 'pos.model')
        if custom_pos_file:
            self._tagger.load_with_lexicon(pos_model_file, custom_pos_file)
        else:
            self._tagger.load(pos_model_file)

        '''加载命名实体识别模型'''
        self._ner = NamedEntityRecognizer()
        self._ner.load(os.path.join(self._ltp_dir, 'ner.model'))

        '''加载依存句法分析模型'''
        self._parser = LParser()
        self._parser.load(os.path.join(self._ltp_dir, 'parser.model'))

    def segment(self, txt):
        return list(self._segmentor.segment(txt))

    def pos(self, txt, cache=False):

        result = None

        if cache:
            result = self._get_from_cache(txt)

        if result is None:
            tokenized = self.segment(txt)
            tags = self._tagger.postag(tokenized)

            result = []
            for i, w, t in zip(list(range(len(tokenized))), tokenized, tags):
                result.append(Token(w, t, i))

            self._set_cache(txt, result)

        return result

    def ner(self, txt):
        tokens = self.pos(txt)
        return list(self._ner.recognize([t.word for t in tokens], [t.pos for t in tokens]))

    def parse2relations(self, txt):
        tokens = self.pos(txt)

        words = [t.word for t in tokens]
        tags = [t.pos for t in tokens]

        arcs = self._parser.parse(words, tags)

        result = []
        for i, w, p, a in zip(list(range(len(words))), words, tags, arcs):
            head_token = Token(words[a.head - 1] if a.head > 0 else 'Root', tags[a.head - 1] if a.head > 0 else 'Root',
                               a.head - 1)
            dep_token = Token(w, p, i)

            result.append(Relation(a.relation, head_token, dep_token))

        return result

    def parse2sents(self, txt):
        sents = []

        for sent_txt in self.ssplit(txt):
            sent_relations = self.parse2relations(sent_txt + '。')
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


class HanLPParser(Parser):
    """
    基于HanLP实现的Parser
    在hanlp.properties里配置用户自定义词典。新添加词后，需要删除词库data\dictionary\custom\CustomDictionary.txt.bin缓存文件。
    """

    def __init__(self, hanlp_dir):
        """
        :param hanlp_dir:
        """
        super(HanLPParser, self).__init__()

        self._HanLP = jpype.JClass('com.hankcs.hanlp.HanLP')
        self._NLPTokenizer = jpype.JClass('com.hankcs.hanlp.tokenizer.NLPTokenizer')

        self._CustomDictionary = jpype.JClass('com.hankcs.hanlp.dictionary.CustomDictionary')

        self._CustomDictionary.add('好用', 'a 9999')

    def segment(self, txt):
        result = []

        # words = self._HanLP.segment(txt)
        words = self._NLPTokenizer.segment(txt)
        for word in words:
            result.append(word.word)

        return result

    def pos(self, txt, cache=False):
        result = None

        if cache:
            result = self._get_from_cache(txt)

        if result is None:
            result = []

            # words = self._HanLP.segment(txt)
            words = self._NLPTokenizer.segment(txt)
            for i, word in enumerate(words):
                result.append(Token(word.word, word.nature.toString(), i))

            self._set_cache(txt, result)

        return result

    def ner(self, txt):
        pass

    def parse2relations(self, txt):
        result = []

        relations = self._HanLP.parseDependency(txt)
        iterator = relations.iterator()

        while iterator.hasNext():
            word2 = iterator.next()
            word1 = word2.HEAD

            token1 = Token(word1.LEMMA, word1.POSTAG, word1.ID)
            token2 = Token(word2.LEMMA, word2.POSTAG, word2.ID)

            result.append(Relation(word2.DEPREL, token1, token2))

        return result

    def parse2sents(self, txt):
        sents = []

        for sent_txt in self.ssplit(txt):
            sent_relations = self.parse2relations(sent_txt + '。')
            tokens = set()

            for relation in sent_relations:
                if relation.token1.word != '##核心##':
                    tokens.add(relation.token1)
                tokens.add(relation.token2)

            tokens = sorted(tokens, key=lambda t: t.id)

            # sent = Sentence(''.join([w.word for w in tokens]))
            sent = Sentence(sent_txt)

            sent.tokens = tokens
            sent.relations = sent_relations

            sents.append(sent)

        return sents


class StandfordParser(Parser):

    def segment(self, txt):
        pass

    def pos(self, txt, cache=False):
        pass

    def ner(self, txt):
        pass

    def parse2relations(self, txt):
        pass

    def parse2sents(self, txt):
        pass


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
            if relation.relation in ['HED', '核心关系']:
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


if DEFAULT_PARSER == 'ltp':
    default_parser = LTPParser(LTP_MODEL_DIR, custom_seg_file=CUSTOM_TOKEN_FILE, custom_pos_file=CUSTOM_POS_FILE)
elif DEFAULT_PARSER == 'hanlp':
    default_parser = HanLPParser(HANLP_MODEL_DIR)
else:
    default_parser = None
