# coding: utf-8

import os
import unittest

from clabel.helper import utils

from clabel.config import RESOURCE_DIR


class MyTestCase(unittest.TestCase):
    def test_something(self):
        self.assertEqual(True, False)

    def test_itemset(self):
        self.assertTrue(True)

        itemsets = utils.read_obj(os.path.join(RESOURCE_DIR, 'mobile.itemsets.pruned.1'))
        for itemset in itemsets:
            print itemset

    def test_show(self):
        self.assertTrue(True)

        features = utils.read_obj(os.path.join(RESOURCE_DIR, 'dp', 'dp.F.pruned'))
        for feature in features:
            print feature

        print len(features)

    def test_fcounter(self):
        self.assertTrue(True)

        fcounter = utils.read_obj(os.path.join(RESOURCE_DIR, 'dp', 'dp.fcounter'))
        for x, c in fcounter.most_common(99999):
            print x, c


if __name__ == '__main__':
    unittest.main()
