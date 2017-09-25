# coding: utf-8

import os
import unittest

from clabel.config import RESOURCE_DIR
from clabel.labeler import LabelExtractor
from clabel.labeler import LexiconExtractor
from common import utils


class MyTestCase(unittest.TestCase):
    def test_something(self):
        self.assertEqual(True, False)

    def test_LexiconExtractor(self):
        self.assertTrue(True)

        pinglun_file = os.path.join(RESOURCE_DIR, 'mobile', 'std.5w.txt')
        workspace = os.path.join(RESOURCE_DIR, 'tmp', 'test1')
        O_seeds = {'不错', '漂亮', '流畅', '方便', '高', '持久'}

        lexicon_extractor = LexiconExtractor(workspace=workspace)
        lexicon_extractor.run(pinglun_file, O_seeds)

    def test_labelExtractor(self):
        self.assertTrue(True)

        feature_file = os.path.join(RESOURCE_DIR, 'tmp', 'test1', '_result', 'features.revise')
        opinion_file = os.path.join(RESOURCE_DIR, 'tmp', 'test1', '_result', 'opinions.revise')

        label_extractor = LabelExtractor(feature_file, opinion_file)

        txt = '4x很好用，正好过年抢红包使用，速度很快'
        labels = label_extractor.extract_from_txt(txt)
        print(' '.join([str(label) for label in labels]))

    def test_labelExtractor_batch(self):
        self.assertTrue(True)

        feature_file = os.path.join(RESOURCE_DIR, 'tmp', 'test1', '_result', 'features.revise')
        opinion_file = os.path.join(RESOURCE_DIR, 'tmp', 'test1', '_result', 'opinions.revise')

        label_extractor = LabelExtractor(feature_file, opinion_file)

        '''
        labels = label_extractor.extract_from_txt(txt)
        for label in labels:
            print(label)
        '''

        results = []

        comment_file = os.path.join(RESOURCE_DIR, 'tmp', 'test2', 'comment.mobile.txt')
        for i, line in enumerate(utils.iter_file(comment_file)):
            if i > 100:
                break

            labels = label_extractor.extract_from_txt(line)
            # print(line, '->', labels)
            results.append(line)
            results.append('->')
            results.append(' '.join([str(label) for label in labels]))
            results.append('')

        utils.write_file(os.path.join(RESOURCE_DIR, 'tmp', 'test2', 'labels.txt'), results)


if __name__ == '__main__':
    unittest.main()
