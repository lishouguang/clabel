# coding: utf-8

import logging

from itertools import product

logger = logging.getLogger(__name__)


def prune(F, O, fcounter, ocounter, rcount, threshold):
    F, O = prune_by_threshold(F, O, fcounter, ocounter, rcount * threshold)
    F = prune_order_features(F, fcounter)

    return F, O


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
