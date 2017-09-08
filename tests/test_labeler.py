# coding: utf-8

import os
import unittest

from clabel.config import RESOURCE_DIR
from clabel.labeler import LexiconExtractor
from clabel.labeler import LabelExtractor


class MyTestCase(unittest.TestCase):
    def test_something(self):
        self.assertEqual(True, False)

    def test_LexiconExtractor(self):
        self.assertTrue(True)

        pinglun_file = os.path.join(RESOURCE_DIR, 'pinglun', 'mobile.sample.min')
        workspace = os.path.join(RESOURCE_DIR, 'tmp', 'test1')
        O_seeds = {u'不错', u'漂亮', u'流畅', u'方便', u'高', u'持久'}

        lexicon_extractor = LexiconExtractor(workspace=workspace)
        lexicon_extractor.run(pinglun_file, O_seeds)

    def test_labelExtractor(self):
        self.assertTrue(True)

        txt = '手机不错，手机运行很流畅'

        feature_file = os.path.join(RESOURCE_DIR, 'extractor', 'mobile.features.revised')
        label_extractor = LabelExtractor(feature_file)
        labels = label_extractor.extract_from_txt(txt)
        for label in labels:
            print label

if __name__ == '__main__':
    unittest.main()
