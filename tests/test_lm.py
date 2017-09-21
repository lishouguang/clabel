# coding: utf-8

import os
import unittest

from clabel.config import LM_MODEL_DIR
from clabel.config import RESOURCE_DIR

from clabel.model import lm


class MyTestCase(unittest.TestCase):
    def test_something(self):
        self.assertEqual(True, False)

    def test_build_train_data(self):
        self.assertTrue(True)

        lm.build_lm_train_data(os.path.join(RESOURCE_DIR, 'mobile', 'std.txt'),
                               os.path.join(RESOURCE_DIR, 'tmp', 'std.hanzi.txt'),
                               os.path.join(RESOURCE_DIR, 'tmp', 'std.pinyin.txt'))

    def test_lm_preprocess(self):
        self.assertTrue(True)

        txt = 'Iphonex不知道会不会火, Iphone8肯定是不行了。'
        hanzis, pnyins = lm.LM.preprocess(txt)
        print(hanzis)
        print(pnyins)

    def test_hanzi_lm(self):
        self.assertTrue(True)

        hanzi_model_file = os.path.join(LM_MODEL_DIR, 'hanzi.arpa')

        hanziLM = lm.HanziLM(hanzi_model_file)
        prob = hanziLM.predict_prob('手机性价比很高。')
        print(prob)

    def test_pinyin_lm(self):
        self.assertTrue(True)

        pnyin_model_file = os.path.join(LM_MODEL_DIR, 'pinyin.arpa')

        pinyinLM = lm.PinyinLM(pnyin_model_file)
        prob = pinyinLM.predict_prob('手机性价比很高。')
        print(prob)


if __name__ == '__main__':
    unittest.main()
