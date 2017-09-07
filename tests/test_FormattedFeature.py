# coding: utf-8

import os

import unittest

from clabel.helper import utils
from clabel.config import RESOURCE_DIR

from clabel.pipeline import lexicon_extractor as lextractor


class MyTestCase(unittest.TestCase):
    def test_something(self):
        self.assertEqual(True, False)

    def test_formattedfeature(self):
        self.assertTrue(True)

        print lextractor.FormattedFeature.get_instance()
        print lextractor.FormattedFeature.get_instance()
        print lextractor.FormattedFeature.get_instance()


if __name__ == '__main__':
    unittest.main()
