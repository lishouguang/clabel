# coding: utf-8

import unittest

import jieba

from itertools import product

from common.utils import iter_file
from common.utils import write_file

from nlp.lexicon import degreeLexicon
from nlp.lexicon import fixedSentimentLexicon


class MyTestCase(unittest.TestCase):
    def test_something(self):
        self.assertEqual(True, False)

    def test_compare_pos(self):
        self.assertTrue(True)

        wd = dict()

        jieba_vocab_file = 'D:\\soft\\anaconda2\\envs\\clabel\\Lib\\site-packages\\jieba\\dict.txt'
        for line in iter_file(jieba_vocab_file):
            word, freq, tag = line.split()
            wd[word] = tag

        jieba_user1_vocab_file = 'D:\\workspace\\pycharm\\clabel\\zresource\\nlp\lexicon\\jieba\\user1.dict'
        for line in iter_file(jieba_user1_vocab_file):
            word, freq, tag = line.split()
            wd[word] = tag

        ds = degreeLexicon.items
        adjs = fixedSentimentLexicon.items

        print('--------------degree-------------------')
        for d in ds:
            if d in wd and wd[d] != 'd':
                # print(d, wd[d])
                pass

        print('--------------adj-------------------')
        for a in adjs:
            if a not in wd:
                # print('-miss- ', a, 10000, 'a')
                pass

            elif wd[a] != 'a' and wd[a][0] in ['n', 'i']:
                # print(a, 10000, 'a')
                pass

        print('--------------d + adj-------------------')
        for d, a in product(ds, adjs):
            x = d + a
            if x in wd and wd[x] != 'a':
                print(x, wd[x])
                pass


if __name__ == '__main__':
    unittest.main()
