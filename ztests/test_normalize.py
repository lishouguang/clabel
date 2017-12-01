# coding: utf-8

import re
import os
import codecs
import unittest
from collections import Counter
from collections import defaultdict

import numpy as np

import jieba
from jieba import posseg
from nlp.parser import combParser
from nlp.parser import ltpParser

from nlp.config import RESOURCE_DIR

from clabel.config import RESOURCE_DIR
from common.utils import iter_file
from common.utils import write_file

from common.clean import clean_txt2
from nlp.normalize import PosReviser
from nlp.normalize import PosNormalizer
from nlp.normalize import build_multiple_pos_vocab


class MyTestCase(unittest.TestCase):
    def test_something(self):
        self.assertEqual(True, False)

    def test_jieba_pos(self):
        self.assertTrue(True)

        jieba.load_userdict(os.path.join(RESOURCE_DIR, 'nlp', 'lexicon', 'jieba', 'user.dict'))
        jieba.load_userdict(os.path.join(RESOURCE_DIR, 'nlp', 'lexicon', 'jieba', 'user2.dict'))

        jieba.add_word('好用', tag='a')
        txt = '之前买的另外一个手环质量就不行'
        print(posseg.lcut(txt, HMM=False))

    def test_normalize_pos(self):
        self.assertTrue(True)

        jieba.add_word('好', tag='d')
        txt = '质量不行'
        for relation in combParser.parse2relations(txt):
            print(relation)

    def test_revise_map(self):
        self.assertTrue(True)

        for x in PosReviser.revise_map.items():
            print(x)

    def test_normalize_revise_txt(self):
        self.assertTrue(True)

        txt = '手机很不好用'

        def tokens2str(tokens):
            return ' '.join(['%s/%s' % (token.word, token.pos) for token in tokens])

        tokens = combParser.pos(txt, revise=False)
        s1 = tokens2str(tokens)
        print(s1)
        # ss.append('jba1- ' + s1)

        tokens = combParser.pos(txt, revise=True)
        s2 = tokens2str(tokens)
        print(s2)
        # ss.append('jba2- ' + s2)

        for relation in combParser.parse2relations(txt):
            print(relation)

        # tokens = ltpParser.pos(line)
        # ss.append('ltp1- ' + tokens2str(tokens))
        #
        # PosReviser.revise(tokens)
        # ss.append('ltp2- ' + tokens2str(tokens))

    def test_normalize_revise_file(self):
        self.assertTrue(True)

        import html.parser

        html_parser = html.parser.HTMLParser()

        def tokens2str(tokens):
            return ' '.join(['%s/%s' % (token.word, token.pos) for token in tokens])

        ss = []

        sb_file = os.path.join(RESOURCE_DIR, 'tmp', 'sbracelet', 'sbracelet.txt')
        for i, line in enumerate(iter_file(sb_file)):
            print(i)

            # 还原html转义字符，&hellip; => ……
            line = html_parser.unescape(line)

            # Todo HTMLParser不能讲&#039;转换，而单独测试时是可以的，不知为何。。
            line = line.replace('&#039;', '\'')

            for sentence in combParser.ssplit(line):
                tokens = combParser.pos(sentence, revise=False)
                s1 = tokens2str(tokens)
                # ss.append('jba1- ' + s1)

                tokens = combParser.pos(sentence, revise=True)
                s2 = tokens2str(tokens)
                # ss.append('jba2- ' + s2)

                if s1 != s2:
                    ss.append('jba1- ' + s1)
                    ss.append('jba2- ' + s2)

                # tokens = ltpParser.pos(line)
                # ss.append('ltp1- ' + tokens2str(tokens))
                #
                # PosReviser.revise(tokens)
                # ss.append('ltp2- ' + tokens2str(tokens))

            if i > 1000:
                break

        write_file(os.path.join(RESOURCE_DIR, 'tmp', 'sbracelet', 'sbracelet.pos.1.txt'), ss)

    def test_normalize_revise_file_count(self):
        self.assertTrue(True)

        import html.parser

        counter = Counter()
        dd = defaultdict(set)

        html_parser = html.parser.HTMLParser()

        def tokens2str(tokens):
            return ' '.join(['%s/%s' % (token.word, token.pos) for token in tokens])

        total = 0
        rc = 0
        dayu10 = 0
        sb_file = os.path.join(RESOURCE_DIR, 'tmp', 'sbracelet', 'sbracelet.txt')
        for i, line in enumerate(iter_file(sb_file)):

            # 还原html转义字符，&hellip; => ……
            line = html_parser.unescape(line)

            # Todo HTMLParser不能讲&#039;转换，而单独测试时是可以的，不知为何。。
            line = line.replace('&#039;', '\'')

            for sentence in combParser.ssplit(line):
                total += 1

                tokens1 = combParser.pos(sentence, revise=False)
                s1 = tokens2str(tokens1)
                # ss.append('jba1- ' + s1)

                if len(tokens1) < 10:
                    dayu10 += 1
                    tokens2 = combParser.pos(sentence, revise=True)
                else:
                    tokens2 = tokens1

                s2 = tokens2str(tokens2)
                # ss.append('jba2- ' + s2)

                for t1, t2 in zip(tokens1, tokens2):
                    if t1.pos != t2.pos:
                        rc += 1

                        fmt = '%s -> %s' % ('%s/%s' % (t1.word, t1.pos), '%s/%s' % (t2.word, t2.pos))
                        counter.update([fmt])
                        dd[fmt].add((s1, s2))

                # if s1 != s2:
                #     ss.append('jba1- ' + s1)
                #     ss.append('jba2- ' + s2)

                # tokens = ltpParser.pos(line)
                # ss.append('ltp1- ' + tokens2str(tokens))
                #
                # PosReviser.revise(tokens)
                # ss.append('ltp2- ' + tokens2str(tokens))

            if i > 20000:
                break

        for x, c in counter.most_common():
            print(x, c)

        lines = []
        for x, c in counter.most_common():
            lines.append('-------%s %d-------' % (x, c))
            samples = dd[x]
            for sample in samples:
                lines.append(sample[0])
                lines.append(sample[1])

        write_file(os.path.join(RESOURCE_DIR, 'tmp', 'sbracelet', 'sbracelet.pos.2.txt'), lines)

        print('total: %d, revise count: %d, dayu10: %d' % (total, rc, dayu10))

        '''词性之间的转换概率'''
        # {'好': {'好/d': 10, '好/a': 14}}
        cdict = defaultdict(lambda: defaultdict(int))
        for s, c in counter.most_common():
            w = s.split('->')[1].strip().split('/')[0]
            cdict[w][s] += c

        lines = []
        for w, ss in sorted(cdict.items(), key=lambda tp: sum(tp[1].values()), reverse=True):
            lines.append('-----------%s-----------' % w)
            for p, c in ss.items():
                lines.append('%s %d' % (p, c))

        write_file(os.path.join(RESOURCE_DIR, 'tmp', 'sbracelet', 'sbracelet.pos.3.txt'), lines)

    def test_revise(self):
        self.assertTrue(True)

        for w, s in PosReviser.revise_map.items():
            print(w, s)

    def test_create_revise_map_data(self):
        self.assertTrue(True)

        sb_file = os.path.join(RESOURCE_DIR, 'tmp', 'sbracelet', 'sbracelet.txt')
        build_multiple_pos_vocab(sb_file)


if __name__ == '__main__':
    unittest.main()
