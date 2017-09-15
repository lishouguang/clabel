# coding: utf-8

import unittest
import logging

from collections import Counter

from clabel.helper import utils
from clabel.nlp import parser as parser

from clabel.pipeline.lexicon_extractor import FormattedFeature

logger = logging.getLogger(__file__)


class MyTestCase(unittest.TestCase):
    def test_something(self):
        self.assertEqual(True, False)

    def test_stem(self):
        self.assertTrue(True)
        features = FormattedFeature.get_instance()

        txt = '打电话人家听不到'

        extract_label(features, txt)


def extract_label(features, txt):
    for sentence in parser.parse2sents(txt):
        labels = extract_stems(features, sentence)
        for label in labels:
            logger.debug('标签主干：%s', label.stem)

            extract_omodifier(label, sentence)
            logger.debug('提取出的评价词修饰语：%s', label.omodifier)

            extract_fmodifier(label, sentence)
            logger.debug('提取出的评价对象修饰语：%s', label.fmodifier)

            print(label)


def extract_fmodifier(label, sentence):
    """
    抽取评价对象修饰语

    评价对象定语抽取规则：
    寻找左依赖于评价对象词的语法元素，如果依赖关系为 ATT(定中关系)，
    且该语法元素的词性为“名词”或“动词”，则该元素为评价对象的定语，将该元素与原评价对象词合并，构成新评价对象。
    :param label:
    :param sentence:
    """
    index = sentence.tokens.index(label.ftoken)
    for relation in sentence.relations[:index - 1]:
        if relation.token1 == label.ftoken and relation.relation == 'ATT' and relation.token2.pos in ['n', 'v']:
            label.add_fmodifier(relation.token2)


def extract_omodifier(label, sentence):
    """
    提取评价词修饰语
    :param label:
    :param sentence:
    :return:
    """

    '''
    评价词修饰语的抽取
    查找左依赖于情感评价词的语法元素，如果该元素词性为“副词”且依赖关系为 ADV(状中关系)，则认为该词为修饰情感评价词的副词。
    '''
    index = sentence.tokens.index(label.otoken)
    for relation in sentence.relations[:index - 1]:
        omodifiers = []

        # 提取评价词的修饰语
        if relation.relation == 'ADV' and relation.token1 == label.otoken:
            omodifiers.append(relation.token2)

            # 提取修饰语的修饰语，目前只处理2层
            index2 = sentence.tokens.index(relation.token2)
            for relation2 in sentence.relations[:index2 - 1]:
                if relation2.relation == 'ADV' and relation2.token1 == relation.token2:
                    omodifiers.insert(0, relation2.token2)

        for om in omodifiers:
            label.add_omodifier(om)
    logger.debug('提取出的评价词修饰语：%s', label.omodifier)

    '''
    句子否定词的抽取
    识别间接关系中的中间语法元素的左依赖词，若为“副词”并存在于否定词集中，则该词为“否定词”。
    这里所指否定词是对意见评价起到意见反转作用的词，而作为副词的否定词不属于此类情况。
    例如，“这个手机不是很好看”中的“不”为句子的否定词，而“我认为这个手机不漂亮”中的“不”为“漂亮”的副词。
    '''
    counter = Counter()
    for relation in sentence.relations:
        if relation.token2 == label.ftoken:
            counter.update([relation.token1])

        if relation.token1 == label.ftoken:
            counter.update([relation.token2])

        if relation.token1 == label.otoken:
            counter.update([relation.token2])

        if relation.token2 == label.otoken:
            counter.update([relation.token1])
    mtoken, c = counter.most_common(1)[0]
    if c == 2:
        for relation in sentence.relations:
            if relation.relation == 'ADV' and relation.token1 == mtoken:
                label.add_omodifier(relation.token2, first=True)


def extract_stems(features, sentence):
    """
    提取标签主干
    :rtype: set of Label
    """
    labels = set()

    '''
    基于核心词的抽取规则
    '''
    # 核心词
    head_token = sentence.find_relations('HED').token2

    '''
    规则一:若核心词(HED 指向词)词性是“形容词(用 a 表示)”或“其他名词修饰符(用 b 表示)”，则认为该核心词为情感评价词，
    然后寻找左依赖于该核心词的语法元素，若它们之间依赖关系为 SBV(主谓关系)，则认为该语法元素为评价对象词。
    '''
    if head_token.pos in ['a', 'b']:
        opinion_token1 = head_token

        index = sentence.tokens.index(head_token)
        for relation in sentence.relations[:index - 1]:
            if relation.relation == 'SBV' and relation.token1 == opinion_token1:
                feature_token1 = relation.token2
                labels.add(Label(feature_token1, opinion_token1))
                logger.debug('主干规则一提取出: %s_%s', feature_token1.word, opinion_token1.word)
                break

    else:
        '''
        规则二:若不满足规则一题设要求，则寻找左依赖于核心词的语法元素，若它们之间依赖关系为 SBV(主谓关系)，则认为该语法元素为评价对象词。
        同时，寻找右依赖于核心词的语法元素，若其词性为“形容词”、“动词”或“其他名词修饰符”，则认为该语法元素为情感评价词。
        '''
        feature_token2 = None
        opinion_token2 = None

        index = sentence.tokens.index(head_token)

        for relation in sentence.relations[:index - 1]:
            if relation.relation == 'SBV' and relation.token1 == head_token:
                feature_token2 = relation.token2
                break

        for relation in sentence.relations[index - 1:]:
            if relation.token1 == head_token and relation.token1.pos in ['a', 'v', 'b']:
                opinion_token2 = relation.token2
                break

        if feature_token2 and opinion_token2:
            labels.add(Label(feature_token2, opinion_token2))
            logger.debug('主干规则二提取出：%s_%s', feature_token2.word, opinion_token2.word)

    '''
    基于特征词库的抽取规则
    '''

    '''
    规则三:匹配本体特征集，识别出评价语料中的特征词以及特征词所依赖的语法元素。
    若依赖关系为ATT(定中关系)、ADV(状中结构) 或 SBV(主谓关系)，
    而且其依赖的语法元素词性为“形容词”、“其他名词修饰符”、“副词”、“动词”或者“习语”，
    则认为该特征词为评价对象，其依赖的语法元素对应的词为情感评价词。
    '''
    rule3_has = False
    for relation in sentence.relations:
        is_feature = features.is_term(relation.token2.word)
        is_relation = relation.relation in ['ATT', 'ADV', 'SBV']
        is_pos = relation.token1.pos in ['a', 'b', 'd', 'v', 'i']

        if is_feature and is_relation and is_pos:
            feature_token3 = relation.token2
            opinion_token3 = relation.token1
            labels.add(Label(feature_token3, opinion_token3))
            rule3_has = True
            logger.debug('主干规则三提取出：%s_%s', feature_token3.word, opinion_token3.word)

    '''
    规则四:若规则三没有识别出情感评价词对，则认为该特征词所依赖的词为非情感评价词，
    继续寻找依赖于非情感评价词的语法元素，即寻找间接关联对象。
    寻找规则可描述为:寻找非情感评价词右依赖的语法元素，
    若它们之间的依赖关系为 SBV(主谓关系)、ATT(定中关系)、COO(并列关系)、VOB(动宾关系) 或CMP(动补结构)，
    且该语法元素词性为“形容词”、“其他名词修饰符”、“副词”、“动词”或者“习语”，
    则认为该特征词为评价对象，间接关联对象所对应的词为情感评价词。
    '''
    if not rule3_has:
        for relation in sentence.relations:
            if features.is_term(relation.token2.word):
                index = sentence.tokens.index(relation.token1)

                for relation_ in sentence.relations[index - 1:]:
                    is_token_ = relation_.token2 == relation.token1
                    is_relation_ = relation_.relation in ['SBV', 'ATT', 'COO', 'VOB', 'CMP']
                    is_pos_ = relation_.token1.pos in ['a', 'b', 'd', 'v', 'i']

                    if is_token_ and is_relation_ and is_pos_:
                        feature_token4 = relation.token2
                        opinion_token4 = relation_.token1
                        labels.add(Label(feature_token4, opinion_token4))
                        logger.debug('主干规则四提取出：%s_%s', feature_token4.word, opinion_token4.word)
    return labels


class Label(object):

    def __init__(self, ftoken, otoken):
        """
        :param ftoken:
        :param otoken:
        """
        self.__feature_token = ftoken
        self.__opinion_token = otoken

        self.__omodifier_tokens = []
        self.__fmodifier_tokens = []

    @property
    def ftoken(self):
        return self.__feature_token

    @property
    def otoken(self):
        return self.__opinion_token

    def add_omodifier(self, token, first=False):
        if first:
            self.__omodifier_tokens.insert(0, token)
        else:
            self.__omodifier_tokens.append(token)

    def add_fmodifier(self, token):
        self.__fmodifier_tokens.append(token)

    @property
    def fmodifier(self):
        return '_'.join([t.word for t in self.__fmodifier_tokens])

    @property
    def omodifier(self):
        return '_'.join([t.word for t in self.__omodifier_tokens])

    @property
    def stem(self):
        return '%s__%s' % (self.__feature_token.word, self.__opinion_token.word)

    def __hash__(self):
        return hash(self.__feature_token) + hash(self.__opinion_token)

    def __eq__(self, other):
        if not isinstance(other, Label):
            return False
        return self.__feature_token == other.__feature_token and self.__opinion_token == other.__opinion_token

    def __str__(self):
        omodifier_str = '_'.join([t.word for t in self.__omodifier_tokens])
        fmodifier_str = '_'.join([t.word for t in self.__fmodifier_tokens])
        return '(%s)%s__(%s)%s' % (fmodifier_str, self.__feature_token.word, omodifier_str, self.__opinion_token.word)

if __name__ == '__main__':
    unittest.main()
