# coding: utf-8

import re
import logging

from collections import Counter

from clabel.helper.utils import iter_file

logger = logging.getLogger(__file__)

PATTERN_REMOVE_POS = r'\001[A-Z]+\s'


def run_prune(itemsets, ssplit_file, tx_file):
    logger.info('to prune by compact...')
    itemsets_pruned = compact_prune(itemsets, ssplit_file)
    # itemsets_pruned = redundant_prune(itemsets, tx_file)
    return itemsets_pruned


def compact_prune(itemsets, ssplit_file):
    """
    紧凑剪枝
    对多个词组成的特征短语进行剪枝。如果特征短语是紧凑的，并且出现在2条以上的句子里，则认为这个特征短语是有效的。
    :param itemsets:
    :param ssplit_file:
    :return:
    """
    counter = Counter()

    for line in iter_file(ssplit_file):
        sentence = _remove_pos(line)

        for itemset in itemsets:
            if _is_compact(itemset, sentence):
                counter.update([itemset])

    return [itemset for itemset in itemsets if counter[itemset] > 2]


def redundant_prune(itemsets, tx_file):
    """
    p-support（纯支持度）剪枝
    psupport(手机) = psupport(手机 屏幕) - psupport(手机 电池) - psupport(手机 xx)
    :param itemsets:
    :param tx_file:
    """
    # 统计每个itemset的出现频率
    counter = Counter()
    for line in iter_file(tx_file):
        basket = set(line.split(','))
        for itemset in itemsets:
            if set(itemset.split()).issubset(basket):
                counter.update([itemset])

    # 将itemsets组织成树，itemsets里item数更多的在上层
    itemsets = sorted(itemsets, key=lambda i: len(i.split()), reverse=True)
    itemset_tree = dict()
    for itemset in itemsets:
        paths = []
        find_paths(itemset_tree, itemset, paths)
        put(itemset_tree, paths, itemset)

    # 计算每个itemset的p-support
    itemset_psupports = dict()
    calc_psupport(counter, itemset_tree, itemset_psupports)
    psupports = sorted([(k, v) for k, v in itemset_psupports.items()], key=lambda kv: kv[1], reverse=True)

    for x, y in psupports:
        print x, y
    return psupports


def calc_psupport(counter, itemset_tree, itemset_psupports):
    for itemset, children in itemset_tree.items():
        itemset_psupports[itemset] = counter[itemset]

        for subitemset, xchildren in children.items():
            itemset_psupports[subitemset] = counter[subitemset] - counter[itemset]

            calc_psupport(counter, xchildren, itemset_psupports)


def print_tree(tree, level):
    for item, children in tree.items():
        print '-' * level * 4 + item

        print_tree(children, level + 1)


def put(tree, paths, item):
    for path in paths:
        tree = tree.get(path)

    tree[item] = {}


def find_paths(tree, item, paths=[]):
    for key, children in tree.items():
        if set(item.split()).issubset(set(key.split())):
            paths.append(key)
            find_paths(children, item, paths)
            return


def _find_atomic_children(itemsets, itemset):
    all_children = []
    for tmp_itemset in itemsets:
        if set(itemset.split()).issubset(set(tmp_itemset.split())):
            all_children.append(tmp_itemset)

    return all_children


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
