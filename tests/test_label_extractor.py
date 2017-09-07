# coding: utf-8

import os
import unittest

from collections import Counter

from clabel.helper import utils
from clabel.config import RESOURCE_DIR

from clabel.nlp import parser as parser

from clabel.pipeline import label_extractor as labeler


class MyTestCase(unittest.TestCase):
    def test_something(self):
        self.assertEqual(True, False)

    def test_extract_txt(self):
        self.assertTrue(True)

        txt = u'通话声音比较小，触屏效果不好，其他还行'
        labels = labeler.extract_from_txt(txt)
        for label in labels:
            print label
            print label.raw
            print label.normalized

    def test_extract_file(self):
        self.assertTrue(True)

        labels = labeler.extract_from_file(os.path.join(RESOURCE_DIR, 'mobile', 'mobile.sample.min'))

        counter = Counter()
        for label in labels:
            counter.update(['%s%s' % (label.nfeature.replace('_', ''), label.nopinion)])

        for l, c in counter.most_common():
            print l, c

    def test_extract_root_va(self):
        self.assertTrue(True)

        sentences = parser.parse_sentence('稍微厚了一点，机子不错。')
        for sent in sentences:
            root_relation = sent.get_root_relation()
            if root_relation.token2.pos == 'VA':
                print root_relation.token2.word
                print root_relation

    def test_extract_file1(self):
        self.assertTrue(True)

        results = {}

        pinglun_file = os.path.join(RESOURCE_DIR, 'mobile', 'mobile.sample.min')
        for pinglun in utils.iter_file(pinglun_file):
            print pinglun

            labels = labeler.extract_from_txt(pinglun)
            results[pinglun] = labels

        utils.save_obj(results, os.path.join(RESOURCE_DIR, 'tmp', 'label.dict'))

    def test_read_extract_file1(self):
        self.assertTrue(True)

        results = utils.read_obj(os.path.join(RESOURCE_DIR, 'tmp', 'label.dict'))
        print len(results.keys())

        xx = []
        for pinglun in results:
            print 'pinglun: ', pinglun
            xx.append('pinglun: %s' % pinglun)
            for label in results[pinglun]:
                print '-> %s -> %s' % (label.raw, label.normalized)
                xx.append('-> %s -> %s' % (label.raw, label.normalized))

        utils.write_file(u'D:\\meizu\\京东&天猫评论数据挖掘_全品类\\汇报_20170214\\label.txt', xx)

    def test_count_extract_file1(self):
        self.assertTrue(True)

        results = utils.read_obj(os.path.join(RESOURCE_DIR, 'tmp', 'label.dict'))
        print len(results.keys())

        counter = Counter()

        i = 0
        for pinglun in results:
            i += 1
            if i > 143:
                break

            print 'pinglun: ', pinglun

            for label in results[pinglun]:
                print '-> %s -> %s' % (label.raw, label.normalized)
                counter.update(['%s%s' % (label.nfeature.replace('_', ''), label.nopinion)])

        counter = ['%s %d' % (k, c) for k, c in counter.most_common(10000)]
        utils.write_file(u'D:\\meizu\\京东&天猫评论数据挖掘_全品类\\汇报_20170214\\label.counter', counter)

    def test_f1(self):
        self.assertTrue(True)

        import re

        real_count = 0
        extract_count = 0
        right_count = 0

        pinglun_count = 0

        for line in utils.iter_file(u'D:\\meizu\\京东&天猫评论数据挖掘_全品类\\汇报_20170214\\label.txt'):
            if line.startswith('pinglun:'):
                pinglun_count += 1

                xx = re.findall(ur'\[(.*)\]', line.decode('utf-8'))[0]
                realc, extractc, rightc = xx.split()
                print realc, extractc, rightc

                real_count += int(realc)
                extract_count += int(extractc)
                right_count += int(rightc)

        print real_count, extract_count, right_count

        print '评论量：', pinglun_count

        r = extract_count * 1.0 / real_count
        print '召回率：', r

        p = right_count * 1.0 / extract_count
        print '准确率：', p

        print 'F1：', 2 * p * r / (p + r)

if __name__ == '__main__':
    unittest.main()
