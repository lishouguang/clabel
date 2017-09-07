# coding: utf-8

import os
import math
import requests
import unittest

from collections import Counter

from clabel.config import RESOURCE_DIR
from clabel.helper import utils

from clabel.pipeline import pmi


class MyTestCase(unittest.TestCase):
    def test_something(self):
        self.assertEqual(True, False)

    def test_get_tokens(self):
        self.assertTrue(True)

        hits = search([u'一般'], [])
        print hits

    def test_search(self):
        self.assertTrue(True)

        print pmi.search_single()
        print pmi.search_join(u'内存_大')

    def test_pmi(self):
        self.assertTrue(True)
        print pmi.get_polar(u'内存_大')


def search(tokens, words):
    count = 0
    for pinglun in tokens:
        for word in words:
            if word in pinglun:
                count += 1
                break
    return count


if __name__ == '__main__':
    unittest.main()
