# coding: utf-8

import logging

from clabel.helper import utils
from clabel.config import NLP_API_LOCAL

from clabel.pipeline import pmi
from clabel.pipeline import clean
from clabel.pipeline.lexicon import DegreeLexicon
from clabel.pipeline.lexicon import FixedSentimentLexicon

if NLP_API_LOCAL:
    from clabel.nlp import parser_local as parser
else:
    from clabel.nlp import parser

from clabel.pipeline.lexicon_extractor import FormattedFeature

logger = logging.getLogger(__file__)


def extract_from_file(txt_file):
    """
    提取标签，输入源是一个文本文件
    :param txt_file:
    :return: [Label, Label, ...]
    """
    labels = []

    for line in utils.iter_file(txt_file):
        labels += extract_from_txt(line)

    return labels


def extract_from_txt(txt):
    """
    提取标签，输入源是一段文本
    :param txt:
    :return: [Label, Label, ...]
    """
    txts = clean.clean_txt2(txt)
    logger.debug('清洗后的文本是：\n%s' % ('\n'.join(txts)))

    labels = []
    for txt in txts:
        for sent in parser.parse_sentence(txt):
            slabels, features, opinions = _extract_labels_stem(sent)

            for label in slabels:
                # 获取特征修饰符，名词
                ftoken = features[id(label)]
                label.fmodifier = _extract_feature_modifier(sent, ftoken)

                # 获取评价词修饰符，程度词/否定词
                otoken = opinions[id(label)]
                label.omodifier = _extract_opinion_modifier(sent, otoken)
                label.omodifier2 = label.omodifier

            labels += slabels

        # 标准化标签的特征
        for label in labels:
            label.nfeature = normalize_feature(label.feature_np)

        # 标准化标签的评价词
        for label in labels:
            label.nopinion = normalize_opinion(label.opinion)

        # 标准化标签的程度词修饰符
        for label in labels:
            label.omodifier2 = normalize_opinion_degree(label.omodifier)

        # 判断情感极性
        for label in labels:
            label.polar = get_polar(label.feature_np, label.opinion, label.nfeature, label.nopinion)

    return labels


def normalize_feature(feature):
    """
    标准化标签的特征
    :param feature:
    :return:
    """
    feature = utils.convert2unicode(feature)

    nfeature = FormattedFeature.get_instance().get_head(feature)
    if nfeature is None:
        nfeature = feature

    return nfeature


def normalize_opinion(opinion):
    """
    标准化标签的评价词
    :param opinion:
    :return:
    """
    return opinion


def normalize_opinion_degree(omodifier):
    """
    标准化评价词的程度修饰符
    :param omodifier:
    """
    words = omodifier.split(Label.OPINION_MODIFIER_SEPARATOR)
    for index, word in enumerate(words):
        if DegreeLexicon.is_degree(word):
            words[index] = DegreeLexicon.get_head(word)
    return Label.OPINION_MODIFIER_SEPARATOR.join(words)


def get_polar(feature, opinion, nfeature, nopinion):
    """
    判断标签的情感极性
    :param feature:
    :param opinion:
    :param nfeature:
    :param nopinion:
    """
    polar = FixedSentimentLexicon.get_polar(opinion)

    if polar == 'x' and nopinion is not None:
        polar = FixedSentimentLexicon.get_polar(nopinion)

    if polar == 'x':
        pmi.get_polar('%s_%s' % (feature, opinion))

    return polar


def _extract_labels_stem(sentence):
    """
    提取出标签主干
    :param sentence:
    :return:
    """
    labels = []

    opinions = {}
    features = {}

    # 有评价对象的提取方式
    for relation in sentence.relations:

        if relation.format == 'nsubj(VA, NN)':
            save_labels(labels, features, opinions, relation.token2, relation.token1)
        elif relation.format == 'amod(NN, VA)':
            save_labels(labels, features, opinions, relation.token1, relation.token2)
        elif relation.format == 'amod(NN, JJ)':
            save_labels(labels, features, opinions, relation.token1, relation.token2)

    # 无评价对象的提取方式，root(ROOT/None, 厚/VA)
    rrelation = sentence.get_root_relation()
    if rrelation.token2.pos == 'VA':

        is_exist = False
        for label in labels:
            if label.opinion == rrelation.token2.word:
                is_exist = True
                break

        if not is_exist:
            save_labels(labels, features, opinions, parser.Token('', '', ''), rrelation.token2)

    return labels, features, opinions


def _extract_feature_modifier(sentence, ftoken):
    """
    填充标签的特征词修饰语，组成特征短语
    :param sentence:
    :param ftoken:
    """
    for relation in sentence.relations:
        if relation.format == 'compound:nn(NN, NN)' and relation.token1 == ftoken:
            return relation.token2.word
        elif relation.format == 'nmod:assmod(NN, NN)' and relation.token1 == ftoken:
            return relation.token2.word
        elif relation.format == 'amod(NN, JJ)' and relation.token1 == ftoken:
            return relation.token2.word
    return None


def _extract_opinion_modifier(sentence, otoken):
    """
    填充评价词的修饰语，程度词/否定词
    :param sentence:
    :param otoken:
    """
    modifiers = []
    for relation in sentence.relations:

        if relation.format == 'advmod(VA, AD)' and relation.token1 == otoken:
            modifiers.append(relation.token2)
        elif relation.format == 'neg(VA, AD)' and relation.token1 == otoken:
            modifiers.append(relation.token2)

    return Label.OPINION_MODIFIER_SEPARATOR.join([t.word for t in modifiers])


def save_labels(labels, features, opinions, ftoken, otoken):
    label = Label(ftoken.word, otoken.word)
    labels.append(label)

    features[id(label)] = ftoken
    opinions[id(label)] = otoken


class Label(object):

    OPINION_MODIFIER_SEPARATOR = ','

    def __init__(self, feature, opinion, fmodifier='', omidifier=''):
        self.fmodifier = fmodifier
        self.feature = feature

        self.omodifier = omidifier
        self.omodifier2 = omidifier
        self.opinion = opinion

        self.polar = '0'

        self.nfeature = self.feature
        self.nopinion = self.opinion

    @property
    def feature_np(self):
        if self.fmodifier:
            return '%s_%s' % (self.fmodifier, self.feature)
        return self.feature

    @property
    def raw(self):
        return '%s_%s__(%s)%s %s' % (self.fmodifier, self.feature, self.omodifier, self.opinion, self.polar)

    @property
    def normalized(self):
        # 1）特征标准化 2）程度词标准化 3）评价词标准化
        return '%s__(%s)%s %s' % (self.nfeature, self.omodifier2, self.nopinion, self.polar)

    def __str__(self):
        return '(%s)%s[%s]__(%s)%s[%s]' % (self.fmodifier, self.feature, self.nfeature, self.omodifier, self.opinion,
                                           self.nopinion)
