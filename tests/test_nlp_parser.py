# coding: utf-8

import os
import unittest

from clabel.config import RESOURCE_DIR
from clabel.helper.utils import iter_file
from clabel.helper.utils import write_file

from clabel.nlp.parser import default_parser as parser


class MyTestCase(unittest.TestCase):
    def test_something(self):
        self.assertEqual(True, False)

    def test_ssplit(self):
        self.assertTrue(True)
        txt = '手机屏幕很大。'
        for sent in parser.ssplit(txt):
            print('sent: ', sent)

    def test_token(self):
        self.assertTrue(True)
        for t in parser.segment('很给力'):
            print(t)

    def test_pos(self):
        self.assertTrue(True)

        tokens = parser.pos('配件太少。')
        for token in tokens:
            print(token)

    def test_parse(self):
        self.assertTrue(True)

        relations = parser.parse2relations('触摸屏效果还不错')
        for relation in relations:
            print(relation)

    def test_parse_cache(self):
        self.assertTrue(True)

        feature = '运行流畅'
        posed = parser.pos(feature.replace('_', ''), cache=True)
        print(posed)

    def test_parse_sentence(self):
        self.assertTrue(True)

        sent_txt = '手机屏幕很大。'
        for sent in parser.parse2sents(sent_txt):
            print('sent: ', sent)


if __name__ == '__main__':
    unittest.main()
