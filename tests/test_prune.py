# coding: utf-8

import os
import unittest

from clabel.helper import utils
from clabel.config import RESOURCE_DIR

import clabel.pipeline.prune as prune


class MyTestCase(unittest.TestCase):
    def test_something(self):
        self.assertEqual(True, False)

    def test_is_compact(self):
        self.assertTrue(True)

        itemset = '手机 屏幕'
        sentence = '不错，是手机屏幕正品！'
        print(prune._is_compact(itemset, sentence))

    def test_redundant_prune(self):
        self.assertTrue(True)

        itemsets = utils.read_obj(os.path.join(RESOURCE_DIR, 'mobile.itemsets.pruned.1'))
        tx_file = os.path.join(RESOURCE_DIR, 'mobile.sample.tx.basket')
        prune.redundant_prune(itemsets, tx_file)

    def test_find_atomic_children(self):
        self.assertTrue(True)

        itemsets = ['买 手机', '手机', '手机 屏幕', '手机 屏幕', ]
        itemset = '手机'
        prune._find_atomic_children()

    def test_find_paths(self):
        self.assertTrue(True)

        tree = {'手机 拍照 功能': {'手机 拍照': {'拍照': {}}, '功能': {}}}
        paths = []
        find_paths(tree, '屏幕', paths)
        print(paths)
        print('/'.join(paths))

    def test_tree_itemset(self):
        self.assertTrue(True)

        itemsets = utils.read_obj(os.path.join(RESOURCE_DIR, 'mobile.itemsets'))

        itemsets = [itemset for itemset, _ in itemsets]
        itemsets = sorted(itemsets, key=lambda i: len(i.split()), reverse=True)

        itemset_tree = dict()
        for itemset in itemsets:
            paths = []
            find_paths(itemset_tree, itemset, paths)
            put(itemset_tree, paths, itemset)

        print_tree(itemset_tree, 1)

    def test_find_super_itmesets(self):
        self.assertTrue(True)

        import clabel.pipeline.prune2 as prune2

        frequents = utils.read_obj(os.path.join(RESOURCE_DIR, 'mobile.itemsets'))
        itemsets = [itemset for itemset, _ in frequents]
        for x in prune2._find_super_itemsets(itemsets, '手机'):
            print(x)

    def test_redundant_prune2(self):
        self.assertTrue(True)

        import clabel.pipeline.prune2 as prune2

        # frequents = utils.read_obj(os.path.join(RESOURCE_DIR, 'mobile.itemsets'))
        # itemsets = [itemset for itemset, _ in frequents]
        # tx_file = os.path.join(RESOURCE_DIR, 'mobile.sample.tx.basket')
        # counter = prune2.redundant_prune(itemsets, tx_file)
        # utils.save_obj(counter, os.path.join(RESOURCE_DIR, 'mobile.prune.psupport'))

        counter = utils.read_obj(os.path.join(RESOURCE_DIR, 'mobile.prune.psupport'))
        for x, c in counter.most_common():
            print(x, c)

    def test_order_prune(self):
        self.assertTrue(True)

        import clabel.pipeline.prune2 as prune2

        frequents = utils.read_obj(os.path.join(RESOURCE_DIR, 'mobile.itemsets'))
        itemsets = [itemset for itemset, _ in frequents]
        tx_file = os.path.join(RESOURCE_DIR, 'mobile.sample.tx.basket')
        itemsets = prune2.order_prune(itemsets, tx_file)
        for x in itemsets:
            print(x)

    def test_order_prune_x(self):
        self.assertTrue(True)

        lines = utils.read_file(os.path.join(RESOURCE_DIR, 'mobile.sample.tx.basket'))
        lines = [line.replace('_', ' ') for line in lines]
        utils.write_file(os.path.join(RESOURCE_DIR, 'mobile.sample.tx.basket.1'), lines)

        features = get_features()
        features = [f.replace('_', ' ') for f in features]

        features = prune.order_prune(features, os.path.join(RESOURCE_DIR, 'mobile.sample.tx.basket.1'))
        for f in features:
            print(f)


def get_features():
    fcounter = utils.read_obj(os.path.join(RESOURCE_DIR, 'dp', 'feature.counter'))
    return [f for f in fcounter if fcounter[f] > 1]


def print_tree(tree, level):
    for item, children in list(tree.items()):
        print('-' * level * 4 + item)

        print_tree(children, level + 1)


def put(tree, paths, item):
    for path in paths:
        tree = tree.get(path)

    tree[item] = {}


def find_paths(tree, item, paths=[]):
    for key, children in list(tree.items()):
        if set(item.split()).issubset(set(key.split())):
            paths.append(key)
            find_paths(children, item, paths)
            return


if __name__ == '__main__':
    unittest.main()
