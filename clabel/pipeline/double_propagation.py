# coding: utf-8

import os
import logging
import itertools

from itertools import product
from collections import Counter

from clabel.helper import utils
from clabel.pipeline import lexicon
from clabel.config import RESOURCE_DIR

from clabel.nlp import parser

logger = logging.getLogger(__file__)


def extract(O_seed, R, threshold=0.00001):
    """
    使用Double Propagation提取特征词/评价词
    :param O_seed: 种子评价词
    :param R: 评论集（已经被处理过）
    :param threshold: 阈值，0.00001表示10W条评论中至少出现一次
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

    utils.save_obj(F, os.path.join(RESOURCE_DIR, 'dp', 'dp.F'))
    utils.save_obj(O, os.path.join(RESOURCE_DIR, 'dp', 'dp.O'))
    utils.save_obj(fcounter, os.path.join(RESOURCE_DIR, 'dp', 'dp.fcounter'))
    utils.save_obj(ocounter, os.path.join(RESOURCE_DIR, 'dp', 'dp.ocounter'))

    F, O = prune_by_threshold(F, O, fcounter, ocounter, rcount * threshold)
    F = prune_order_features(F, fcounter)

    return F, O


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

        # 手机(外形)很(漂亮)
        if fmt == 'nsubj(VA, NN)':
            if token1 in O:
                features.add(token2)

        if fmt == 'amod(NN, VA)':
            if token2 in O:
                features.add(token1)

        # 这个手机有很(漂亮)的(外形)
        if fmt == 'amod(NN, JJ)':
            if token2 in O:
                features.add(token1)

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

        # 手机的(拍照)和(摄像)不错
        if fmt == 'conj(NN, NN)':
            if token1 in F:
                features.add(token2)
            if token2 in F:
                features.add(token1)

        # (手机外形)不错
        if fmt == 'compound:nn(NN, NN)':
            if token1 in F or token2 in F:
                features.add('%s_%s' % (token2, token1))

        # (手机)的(外形)很漂亮
        if fmt == 'nmod:assmod(NN, NN)':
            if token1 in F or token2 in F:
                features.add('%s_%s' % (token2, token1))

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

        if fmt == 'dep(VA, VA)':
            if token1 in O:
                opinions.add(token2)
            if token2 in O:
                opinions.add(token1)
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

        if fmt == 'nsubj(VA, NN)':
            if token2 in F:
                opinions.add(token1)

        if fmt == 'amod(NN, VA)':
            if token1 in F:
                opinions.add(token2)

        if fmt == 'amod(NN, JJ)':
            if token1 in F:
                opinions.add(token2)

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


def prune_by_threshold(F, O, fcounter, ocounter, threshold):
    logger.info('threshold pruning...')

    l1 = len(F)
    o1 = len(O)

    for f in fcounter:
        # if fcounter[f] == 1:
        if fcounter[f] < threshold:
            logger.debug('remove %s', f)
            F.remove(f)

    for o in ocounter:
        if ocounter[o] == 1:
            logger.debug('remove %s', o)
            O.remove(o)

    logger.info('once pruning features %d: %d -> %d ', l1 - len(F), l1, len(F))
    logger.info('once pruning opinions %d: %d -> %d ', o1 - len(O), o1, len(O))

    return F, O


def prune_order_features(F, fcounter):
    """
    词序修正
    :param fcounter:
    :param F:
    :return:
    """

    logger.info('order pruning...')

    # 列出包含多项的频繁项集的所有排序可能
    f_nps = []
    for f in F:
        nps = f.split('_')

        if len(nps) > 1:
            params = [nps for _ in range(len(nps))]
            combinations = [x for x in product(*params) if len(set(x)) == len(nps)]
            f_nps.append((f, combinations))

    correct = dict()
    # 统计每种可能出现的次数
    for f, combinations in f_nps:
        mmax = -1
        for combin in combinations:
            c = fcounter.get('_'.join(combin), 0)
            if c > mmax:
                correct[f] = '_'.join(combin)
                mmax = c

    f_pruned = set()
    for f in F:
        f_ordered = correct.get(f, f)

        if f != f_ordered:
            logger.debug('修正词序: %s -> %s' % (f, f_ordered))

        f_pruned.add(f_ordered)

    return f_pruned


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
            tokens = parser.pos_with_cache(f + '。')[0]
            if len(tokens) > 2:
                logging.debug('prune: [%s]-[%s]不是一个词' % (np, f))
                return False

            pos = tokens[0][1]
            if pos not in {u'VV', u'NN'}:
                logging.debug('prune: [%s]-[%s/%s]特词性不对' % (np, f, pos))
                return False

        return True
    else:
        return False


def is_meaningful_word(word):
    return (not is_meaningless_word(word)) and (not is_spe_word(word))


def is_meaningless_word(word):
    mwords = [u'的', u'了', u'我']
    for mw in mwords:
        if word.find(mw) != -1:
            return True
    return False


def is_spe_word(word):
    return lexicon.is_brand(word) or lexicon.is_model(word) or lexicon.is_personals(word) or lexicon.is_color(
        word) or lexicon.is_place(word) or lexicon.is_date(word)
