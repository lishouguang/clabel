# coding: utf-8

import os
import unittest

from clabel.config import RESOURCE_DIR
from clabel.pipeline import lexicon_extractor


class MyTestCase(unittest.TestCase):
    def test_something(self):
        self.assertEqual(True, False)

    def test_pipeline(self):
        self.assertTrue(True)

        pinglun_file = os.path.join(RESOURCE_DIR, 'mobile.sample.min')
        O_seeds = get_opinion_seeds()

        cluster_features, opinions = lexicon_extractor.extract(pinglun_file, O_seeds)

        for cls in cluster_features:
            print('%s --- %s' % (cls, ' '.join(cluster_features[cls])))

        # utils.save_obj(cluster_features, os.path.join(RESOURCE_DIR, 'dp', 'dp.CF'))
        # utils.save_obj(opinions, os.path.join(RESOURCE_DIR, 'dp', 'dp.O'))


def get_opinion_seeds():
    """
    获取种子评价词
    :return:
    """
    O = {'不错', '漂亮', '流畅', '方便', '高', '持久'}
    return O


if __name__ == '__main__':
    unittest.main()
