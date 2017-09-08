# coding: utf-8

import logging
import itertools

from collections import Counter

from clabel.nlp.lexicon import irrelevantLexicon

from clabel.nlp import parser

logger = logging.getLogger(__file__)

from clabel.pipeline.relation_rule import foRule
from clabel.pipeline.relation_rule import ffRule
from clabel.pipeline.relation_rule import ooRule


def extract(O_seed, R):
    """
    使用Double Propagation提取特征词/评价词
    :param O_seed: 种子评价词
    :param R: 评论集（已经被处理过）
    :return:
    """
    logger.info('extract features/opinions by Double Propagation algorithm..')

    F = set()
    O = set(O_seed)

    i = 0
    last_f_count = len(F)
    last_o_count = len(O)
    R2 = R
    while True:
        R1, R2 = itertools.tee(R2)

        i += 1
        logger.info('Double Propagation迭代...第%d次...' % i)

        for sent_relations in R1:
            F |= extract_feature_by_opinion(sent_relations, O)

            O |= extract_opinions_by_opinion(sent_relations, O)

            F |= extract_feature_by_feature(sent_relations, F)

            O |= extract_opinions_by_feature(sent_relations, F)

        f_count = len(F)
        o_count = len(O)

        logger.info('本次迭代发现了%d个特征词，%d个评价词.' % (f_count - last_f_count, o_count - last_o_count))
        logger.info('累计发现了%d个特征词，%d个评价词.' % (f_count, o_count))

        if f_count == last_f_count and o_count == last_o_count:
            logging.info('未发现新的特征词/评价词，停止迭代.')
            break

        last_f_count = f_count
        last_o_count = o_count

    fcounter, ocounter, rcount = get_count(F, O, R2)

    return F, O, fcounter, ocounter, rcount


def extract_feature_by_opinion(relations, O):
    """
    评价词 => 特征词
    :param relations:
    :param O:
    :return:
    """
    features = set()

    for relation in relations:
        fmt = relation['format']
        token1 = relation['token1']
        token2 = relation['token2']

        feature, opinion = foRule.match(fmt, token1, token2)

        if opinion in O:
            features.add(feature)

    return prune_features(features)


def extract_feature_by_feature(relations, F):
    """
    特征词 => 特征词
    :param relations:
    :param F:
    :return:
    """
    features = set()

    for relation in relations:
        fmt = relation['format']
        token1 = relation['token1']
        token2 = relation['token2']

        feature1, feature2 = ffRule.match(fmt, token1, token2)

        if feature1 in F:
            features.add(feature2)

        if feature2 in F:
            features.add(feature1)

    return prune_features(features)


def extract_opinions_by_opinion(relations, O):
    """
    评价词 => 评价词
    :param relations:
    :param O:
    :return:
    """
    opinions = set()

    for relation in relations:
        fmt = relation['format']
        token1 = relation['token1']
        token2 = relation['token2']

        opinion1, opinion2 = ooRule.match(fmt, token1, token2)

        if opinion1 in O:
            opinions.add(opinion2)

        if opinion2 in O:
            opinions.add(opinion1)

    return opinions


def extract_opinions_by_feature(relations, F):
    """
    特征词 => 评价词
    :param relations:
    :param F:
    :return:
    """
    opinions = set()

    for relation in relations:
        fmt = relation['format']
        token1 = relation['token1']
        token2 = relation['token2']

        feature, opinion = foRule.match(fmt, token1, token2)

        if feature in F:
            print 'extract_opinions_by_feature: ', opinion
            opinions.add(opinion)

    return opinions


def prune_features(candidates):
    features = set()

    if not candidates:
        return features

    '''处理非短语特征词'''
    fs = [feature for feature in candidates if feature.find('_') == -1]

    # 对于特征词，需要满足：1）一个句子只提取一个特征词 2）是有意义的词
    if len(fs) == 1 and len(fs[0]) > 1 and is_meaningful_word(fs[0]):
        features.add(fs[0])
    elif fs:
        logging.debug('prune: [%s]不符合特征词条件' % ','.join(fs))

    '''处理短语特征词'''
    nps = [feature for feature in candidates if feature.find('_') != -1]

    for np in nps:
        if is_feature_phrase(np):
            features.add(np)
        else:
            logging.debug('prune: [%s]特征短语中有不符合的特征' % np)

    return features


def get_count(F, O, R):
    rcount = 0
    fcounter = Counter()
    ocounter = Counter()

    for sent_relations in R:
        rcount += 1

        fcounter.update(extract_feature_by_opinion(sent_relations, O))

        ocounter.update(extract_opinions_by_opinion(sent_relations, O))

        fcounter.update(extract_feature_by_feature(sent_relations, F))

        ocounter.update(extract_opinions_by_feature(sent_relations, F))

    return fcounter, ocounter, rcount


def is_feature_phrase(np):
    f1, f2 = np.split('_')

    # 1）是有意义的词 2）字数大于2
    if is_meaningful_word(f1) and is_meaningful_word(f2) and (len(f1) + len(f2)) > 2:

        # 词性判断，短语中不能包含形容词
        for f in [f1, f2]:
            print f
            token = parser.pos_with_cache(f + '。')[0]
            if len(token.word) > 2:
                logging.debug('prune: [%s]-[%s]不是一个词' % (np, f))
                return False

            pos = token.pos
            if pos not in {u'v', u'n', u'a'}:
                logging.debug('prune: [%s]-[%s/%s]特词性不对' % (np, f, pos))
                return False

        return True
    else:
        return False


def is_meaningful_word(word):
    return not irrelevantLexicon.is_irrelevant_word(word)

