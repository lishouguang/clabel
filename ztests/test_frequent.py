# coding: utf-8

import os
import unittest

from clabel.config import FREQUENT_MIN_SUPPORT
from clabel.config import RESOURCE_DIR
from clabel.pipeline import frequent as fq
from common import utils


class MyTestCase(unittest.TestCase):
    def test_something(self):
        self.assertEqual(True, False)

    def test_frequent_support(self):
        self.assertTrue(True)

        frequents = utils.read_obj(os.path.join(RESOURCE_DIR, 'mobile.itemsets'))
        for itemset, support in frequents:
            print(itemset, support)
        print(len(frequents))

    def test_frequent_pruned(self):
        self.assertTrue(True)

        frequents = utils.read_obj(os.path.join(RESOURCE_DIR, 'mobile.itemsets.pruned.1'))
        for f in frequents:
            print(type(f))

    def test_frequent(self):
        self.assertTrue(True)
        tx_file = os.path.join(RESOURCE_DIR, 'mobile.sample.tx.basket')
        frequents = fq.create(tx_file, min_support=FREQUENT_MIN_SUPPORT)
        for itemset, support in frequents:
            print(itemset, support)


if __name__ == '__main__':
    unittest.main()
