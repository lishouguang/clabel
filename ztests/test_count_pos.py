# coding: utf-8

import os
import re
import pickle
import unittest

from collections import Counter
from collections import defaultdict

from common.utils import iter_file
from common.utils import save_obj
from common.utils import read_obj

from clabel.config import RESOURCE_DIR

from nlp.normalize import PosNormalizer


class MyTestCase(unittest.TestCase):
    def test_something(self):
        self.assertEqual(True, False)

    def test_extract_zh(self):
        self.assertTrue(True)

        txt = '人民网/nz 1月1日/t 讯/ng 据/p 《/w [纽约/nsf 时报/n]/nz 》/w 报道/v ，/w 美国/nsf 华尔街/nsf 股市/n 在/p 2013年/t 的/ude1 最后/f 一天/mq 继续/v 上涨/vn ，/w 和/cc [全球/n 股市/n]/nz 一样/uyy ，/w 都/d 以/p [最高/a 纪录/n]/nz 或/c 接近/v [最高/a 纪录/n]/nz 结束/v 本/rz 年/qt 的/ude1 交易/vn 。/w '
        for wp in re.findall(r'([\u4e00-\u9fa5]+)/([a-zA-Z]+)', txt):
            print(wp, type(wp))

        txt = '上海_NR 浦东_NR 开发_NN 与_CC 法制_NN 建设_NN 同步_VV '
        for wp in re.findall(r'([\u4e00-\u9fa5]+)_([a-zA-Z]+)', txt):
            print(wp, type(wp))

    def test_count_multiple_pos(self):
        self.assertTrue(True)

        poses = defaultdict(set)
        counts = defaultdict(int)

        # 人民日报语料
        # base_dir = 'D:\\commons\\中文语料\\people2014\\2014'
        # pattern = r'([\u4e00-\u9fa5]+)/([a-zA-Z]+)'

        # CTB语料
        base_dir = 'D:\\commons\\中文语料\\树库\\LDC\\LDC2013T21\\ctb8.0\\data\\postagged'
        pattern = r'([\u4e00-\u9fa5]+)_([a-zA-Z]+)'

        def iter_corpus(poses_, counts_, base_dir_):
            for f in os.listdir(base_dir_):
                f = os.path.join(base_dir_, f)

                if os.path.isdir(f):
                    iter_corpus(poses_, f)
                else:
                    for line in iter_file(f):
                        for w, p in re.findall(pattern, line):
                            poses_[w].add(p)
                            counts_[w] += 1

        iter_corpus(poses, counts, base_dir)

        save_obj(poses, 'word.pos')
        save_obj(counts, 'word.count')

    def test_query_word_pos(self):
        self.assertTrue(True)

        poses = read_obj('word.pos')
        counts = read_obj('word.count')

        multiples = defaultdict(set)
        # poses = defaultdict(set)
        for w, ps in poses.items():
            s = set([x[0] for x in ps])
            if len(s) > 1:
                multiples[w] |= ps

        results = [(w, ps, counts[w]) for w, ps in multiples.items()]
        results = sorted(results, key=lambda tp: tp[2], reverse=True)

        for w, ps, c in results:
            if c < 5:
                break
            print(w, c, ps)

        print('total:', len(counts))
        print('multiple:', len(multiples))
        print('percent:', 1.0*len(multiples)/len(counts))

        print(poses['真'])

    def test_query_word_pos2(self):
        self.assertTrue(True)

        poses = defaultdict(list)
        counts = defaultdict(int)

        # CTB语料
        base_dir = 'D:\\commons\\中文语料\\树库\\LDC\\LDC2013T21\\ctb8.0\\data\\postagged'
        pattern = r'([\u4e00-\u9fa5]+)_([a-zA-Z]+)'

        def iter_corpus(poses_, counts_, base_dir_):
            for f in os.listdir(base_dir_):
                f = os.path.join(base_dir_, f)

                if os.path.isdir(f):
                    iter_corpus(poses_, f)
                else:
                    for line in iter_file(f):
                        for w, p in re.findall(pattern, line):
                            p = PosNormalizer.normalize(p)
                            poses_[w].append(p)
                            counts_[w] += 1

        iter_corpus(poses, counts, base_dir)

        multiples = defaultdict(list)
        for w, ps in poses.items():
            s = set([x[0] for x in ps])
            if len(s) > 1:
                multiples[w] += ps

        results = [(w, ps, counts[w]) for w, ps in multiples.items()]
        results = sorted(results, key=lambda tp: tp[2], reverse=True)

        for w, ps, c in results:
            if c < 5:
                break

            counter = Counter()
            counter.update(ps)
            ps = ' '.join(['%s=%d' % (p, c) for p, c in counter.most_common()])
            print(w, c, ps)

        print('total:', len(counts))
        print('multiple:', len(multiples))
        print('percent:', 1.0 * len(multiples) / len(counts))


if __name__ == '__main__':
    unittest.main()
