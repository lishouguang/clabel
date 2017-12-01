# coding: utf-8

import unittest

from nlp.parser import default_parser as parser


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

        while True:
            line = input('请输入文本：')
            relations = parser.parse2relations(line)
            for relation in relations:
                print(relation)

    def test_parse_cache(self):
        self.assertTrue(True)

        feature = '运行流畅'
        posed = parser.pos(feature.replace('_', ''), cache=True)
        print(posed)

    def test_parse_sentence(self):
        self.assertTrue(True)

        import jieba
        jieba.del_word('价格便宜')

        sent_txt = '价格便宜。'
        for sent in parser.parse2sents(sent_txt):
            print('sent: ', sent)

    def test_parse2(self):
        self.assertTrue(True)

        line = '之前买的另外一个手环质量就不行'
        relations = parser.parse2relations(line)
        for relation in relations:
            print(relation)

    def test_pos2(self):
        self.assertTrue(True)

        import jieba
        from jieba import dt

        from common.utils import write_file

        # jieba.del_word('价格便宜')

        # write_file('words.txt', dt.FREQ.keys())
        txt = '价格便宜'
        r = jieba.lcut(txt, HMM=False)
        print(r)

        print('dt.cache_file: ', dt.cache_file)
        print('dt.tmp_dir: ', dt.tmp_dir)


if __name__ == '__main__':
    unittest.main()
