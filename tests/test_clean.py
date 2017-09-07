# coding: utf-8

import os
import unittest

from clabel.config import RESOURCE_DIR

from clabel.pipeline import clean
from clabel.nlp import parser_local as parser


class MyTestCase(unittest.TestCase):
    def test_something(self):
        self.assertEqual(True, False)

    def test_clean(self):
        self.assertTrue(True)

        source_file = os.path.join(RESOURCE_DIR, 'mobile.sample')
        dest_file = os.path.join(RESOURCE_DIR, 'clean', 'mobile.sample.clean')

        clean.clean_file(source_file, dest_file)

    def test_clean_txt(self):
        self.assertTrue(True)

        for txt in clean.clean_txt('质量还行。'):
            print txt


if __name__ == '__main__':
    unittest.main()
