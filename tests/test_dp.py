# coding: utf-8

import os
import unittest

from clabel.nlp import parser
from clabel.pipeline import double_propagation
from clabel.config import RESOURCE_DIR
from clabel.helper.utils import read_obj
from clabel.helper.utils import save_obj
from clabel.helper.utils import write_file


class MyTestCase(unittest.TestCase):
    def test_something(self):
        self.assertEqual(True, False)

    def test_extract(self):
        self.assertTrue(True)

        '''
        R = []
        source_dir = os.path.join(RESOURCE_DIR, 'parsed3')
        i = 0
        for d in os.listdir(source_dir):
            i += 1
            print i

            R += read_obj(os.path.join(source_dir, d))
            if len(R) >= 50000:
                break

        save_obj(R, os.path.join(RESOURCE_DIR, 'dp', 'dp.R'))
        '''

        R = read_obj(os.path.join(RESOURCE_DIR, 'dp', 'dp.R'))

        R = [sentence for _, parsed in R for sentence in parsed['sentences']]

        # R = ['价格实惠']

        print '单句总数：', len(R)

        O = {u'不错', u'漂亮', u'流畅', u'方便', u'高', u'持久'}

        F, O_expanded = double_propagation.extract(O, R, parsed=True)
        write_file(os.path.join(RESOURCE_DIR, 'dp', 'dp.features'), F)
        write_file(os.path.join(RESOURCE_DIR, 'dp', 'dp.opinions'), O_expanded)

    def test_show_feature_counter(self):
        self.assertTrue(True)

        fcounter = read_obj(os.path.join(RESOURCE_DIR, 'dp', 'feature.counter'))
        for f, c in fcounter.most_common():
            print f, c

    def test_show_opinion_counter(self):
        self.assertTrue(True)

        ocounter = read_obj(os.path.join(RESOURCE_DIR, 'dp', 'opinion.counter'))
        for o, c in ocounter.most_common():
            print o, c

    def test_prune_features(self):
        self.assertTrue(True)

        features = {u'服务_非常好', u'手机', u'sudu_速度'}
        features = double_propagation.prune_features(features)
        for f in features:
            print f

    def test_prune_order_features(self):
        self.assertTrue(True)

        double_propagation.prune_order_features([u'手机_屏幕', u'手机'], None)

    def test_prune_xx(self):
        self.assertTrue(True)

        F = read_obj(os.path.join(RESOURCE_DIR, 'dp', 'dp.F'))
        O = read_obj(os.path.join(RESOURCE_DIR, 'dp', 'dp.O'))
        fcounter = read_obj(os.path.join(RESOURCE_DIR, 'dp', 'dp.fcounter'))
        ocounter = read_obj(os.path.join(RESOURCE_DIR, 'dp', 'dp.ocounter'))

        print 'len1: ', len(F)

        F, O = double_propagation.prune_by_threshold(F, O, fcounter, ocounter)

        print 'len2: ', len(F)

        F = double_propagation.prune_order_features(F, fcounter)

        print 'len3: ', len(F)

        save_obj(F, os.path.join(RESOURCE_DIR, 'dp', 'dp.F.pruned'))

    def test_is_feature(self):
        self.assertTrue(True)

        fs = [u'模式']
        if len(fs) == 1 and len(fs[0]) > 1 and double_propagation.is_meaningful_word(fs[0]):
            print 'yes'
        elif fs:
            print 'no'

        print double_propagation.is_meaningful_word(fs[0])
        print double_propagation.is_spe_word(fs[0])

    def test_fcounter(self):
        self.assertTrue(True)
        pass

if __name__ == '__main__':
    unittest.main()
