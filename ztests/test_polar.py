# coding: utf-8

import os
import unittest

from clabel.config import RESOURCE_DIR
from clabel.pipeline import lexicon
from common import utils


class MyTestCase(unittest.TestCase):
    def test_something(self):
        self.assertEqual(True, False)

    def test_general_polar(self):
        self.assertTrue(True)

        opinion_file = os.path.join(RESOURCE_DIR, 'dp', 'dp.opinions')
        for word in utils.iter_file(opinion_file):

            polar = lexicon.get_polar(word)
            if polar == 'x':
                print(word, polar)


if __name__ == '__main__':
    unittest.main()
