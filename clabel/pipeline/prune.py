# coding: utf-8

import re
import os
import logging
from itertools import product
from collections import Counter

from clabel.config import RESOURCE_DIR
from clabel.helper.utils import iter_file
from clabel.helper.utils import save_obj

from . import lexicon

logger = logging.getLogger(__file__)


def run_prune(itemsets, ssplit_file, tx_file, min_psupport=100, min_ssupport=2):

    itemsets = single_prune(itemsets)
    save_obj(itemsets, os.path.join(RESOURCE_DIR, 'prune', 'itemsets.singled'))

    itemsets = lexicon_prune(itemsets)
    save_obj(itemsets, os.path.join(RESOURCE_DIR, 'prune', 'itemsets.lexiconed'))

    itemsets_sorted = order_prune(itemsets, tx_file)
    save_obj(itemsets, os.path.join(RESOURCE_DIR, 'prune', 'itemsets.ordered'))

    itemsets_compacted = compact_prune(itemsets_sorted, ssplit_file, min_ssupport)
    save_obj(itemsets, os.path.join(RESOURCE_DIR, 'prune', 'itemsets.compacted'))

    itemsets_redundanted = redundant_prune(itemsets_compacted, tx_file, min_psupport)
    save_obj(itemsets, os.path.join(RESOURCE_DIR, 'prune', 'itemsets.redundanted'))

    return itemsets_redundanted


def single_prune(itemsets):
    """
    过滤单字
    :param itemsets:
    :return:
    """
    logger.info('to prune by single...')

    itemsets_pruned = list()

    for itemset in itemsets:
        if len(itemset.decode('utf-8')) > 1:
            itemsets_pruned.append(itemset)
        else:
            logger.debug('单字过滤：%s' % itemset)

    logger.info('after single pruning: %d' % len(itemsets_pruned))
    return itemsets_pruned


def lexicon_prune(itemsets):
    """
    根据词典过滤
    人称代词、品牌词、型号词
    :param itemsets:
    """
    logger.info('to prune by lexicon...')

    itemsets_pruned = list()
    for itemset in itemsets:

        if not lexicon.is_personals(itemset) and not lexicon.is_brand(itemset) and not lexicon.is_model(itemset):
            itemsets_pruned.append(itemset)
        else:
            logger.debug('词典过滤：%s' % itemset)

    logger.info('after lexicon pruning: %d' % len(itemsets_pruned))
    return itemsets_pruned


def order_prune(itemsets, tx_file):
    """
    词序修正
    :param tx_file:
    :param itemsets:
    :return:
    """
    logger.info('to prune by order...')

    # 列出包含多项的频繁项集的所有排序可能
    multi_itemsets = []
    for itemset in itemsets:
        nps = itemset.split()

        if len(nps) > 1:
            params = []
            for i in range(len(nps)):
                params.append(nps)
            combinations = [x for x in product(*params) if len(set(x)) == len(nps)]
            multi_itemsets.append((itemset, combinations))

    # 统计每种可能出现的次数
    counter = Counter()
    for line in iter_file(tx_file):

        for _, tp in enumerate(multi_itemsets):
            itemset, combinations = tp
            nps = itemset.split()

            if set(nps).issubset(set(line.split(','))):

                for combin in combinations:
                    if re.match(re.compile('.*'.join(combin)), line):
                        counter.update([' '.join(combin)])

    # 取得次数最多的那个排列
    result = dict()
    for _, tp in enumerate(multi_itemsets):
        itemset, combinations = tp
        carr = []
        for combin in combinations:
            cstr = ' '.join(combin)
            carr.append((cstr, counter[cstr]))
        try:
            result[itemset] = sorted(carr, key=lambda ttp: ttp[1], reverse=True)[0][0]
        except:
            pass

    itemsets_pruned = list()
    for itemset in itemsets:
        item_ordered = result.get(itemset, itemset)

        if itemset != item_ordered:
            logger.debug('修正词序: %s -> %s' % (itemset, item_ordered))

        itemsets_pruned.append(item_ordered)

    logger.info('after order pruning: %d' % len(itemsets_pruned))
    return itemsets_pruned


def compact_prune(itemsets, ssplit_file, min_ssupport):
    """
    邻近剪枝
    如果一个频繁项集满足邻近规则，则将这个频繁项集组合成一个特征
    对多个词组成的特征短语进行剪枝。如果特征短语是紧凑的，并且出现在2条以上的句子里，则认为这个特征短语是有效的。
    :param min_ssupport:
    :param itemsets:
    :param ssplit_file:
    :return:
    """
    logger.info('to prune by compact...')
    logger.info('min_ssupport: %s' % min_ssupport)

    itemsets_pruned = list()

    multi_itemsets = []
    for itemset in itemsets:
        if len(itemset.split()) > 1:
            multi_itemsets.append(itemset)
        else:
            itemsets_pruned.append(itemset)

    counter = Counter()
    for line in iter_file(ssplit_file):
        sentence = _remove_pos(line)

        for itemset in multi_itemsets:
            if _is_compact(itemset, sentence):
                counter.update([itemset])

    for itemset in multi_itemsets:
        if counter[itemset] >= min_ssupport:
            itemsets_pruned.append(itemset)
        else:
            logger.debug('邻近剪枝：%s' % itemset)

    logger.info('after compact pruning: %d' % len(itemsets_pruned))
    return itemsets_pruned


def redundant_prune(itemsets, tx_file, min_psupport):
    """
    独立支持度剪枝，p-support
    psupport(手机) = psupport(手机 屏幕) - psupport(手机 电池) - psupport(手机 xx)
    :param min_psupport:
    :param itemsets:
    :param tx_file:
    """
    logger.info('to prune by redundant...')
    logger.info('min_psupport: %s' % min_psupport)

    # 找到每个itemset的所有超集
    supers = dict()
    for itemset in itemsets:
        supers[itemset] = _find_super_itemsets(itemsets, itemset)

    # 统计每个itemset的独立支持度
    counter = Counter()
    for tx in iter_file(tx_file):
        tx_itemset = set(tx.split(','))

        for itemset in itemsets:
            if set(itemset.split()).issubset(tx_itemset):

                # 判断是否独立（是否包含超集）
                is_p = True
                for isuper in supers[itemset]:
                    if set(isuper.split()).issubset(tx_itemset):
                        is_p = False
                        break

                if is_p:
                    counter.update([itemset])

    itemsets_pruned = list()
    for itemset in counter:
        if counter[itemset] >= min_psupport:
            itemsets_pruned.append(itemset)
        else:
            logger.debug('独立支持度剪枝：%s' % itemset)

    logger.info('after redundant pruning: %d' % len(itemsets_pruned))
    return itemsets_pruned


def _find_super_itemsets(itemsets, itemset):
    supers = []
    for itemset_tmp in itemsets:
        if itemset_tmp != itemset and set(itemset.split()).issubset(set(itemset_tmp.split())):
            supers.append(itemset_tmp)
    return supers


def _is_compact(itemset, sentence):
    """
    判断特征短语是不是紧凑的。
    1.特征只有一个词，则是紧凑的
    2.特征有多个词，那么相邻的词在句子里的距离都不超过2才是紧凑的
    :param itemset:
    :param sentence:
    :return:
    """
    itemset = itemset.decode('utf-8')
    sentence = sentence.decode('utf-8')

    items = itemset.split(' ')

    if len(items) == 1:
        return True

    last_index = 0
    for i, item in enumerate(items):
        index = sentence.find(item, last_index)

        if index == -1:
            return False

        if i > 0:
            d = index - len(items[i-1]) - last_index
            if d > 2:
                return False

        last_index = index

    return True


def _remove_pos(sentence):
    return re.sub(r'\001[A-Z]+\s', '', sentence + ' ').strip()
