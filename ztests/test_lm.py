# coding: utf-8

import os
import unittest

from lm.config import LM_MODEL_DIR
from lm.config import RESOURCE_DIR
from lm import lm


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
        hanzis, pnyins = lm.BaseLM.preprocess(txt)
        print(hanzis)
        print(pnyins)

    def test_hanzi_lm(self):
        self.assertTrue(True)

        hanzi_model_file = os.path.join(LM_MODEL_DIR, 'hanzi.arpa')

        hanziLM = lm.HanziLM(hanzi_model_file)
        prob = hanziLM.predict_prob('很好')
        print(prob)

    def test_pinyin_lm(self):
        self.assertTrue(True)

        pnyin_model_file = os.path.join(LM_MODEL_DIR, 'pinyin.arpa')

        pinyinLM = lm.PinyinLM(pnyin_model_file)
        prob = pinyinLM.predict_prob('手机性价比很高。')
        print(prob)

    def test_lm(self):
        self.assertTrue(True)

        hanzi_model_file = os.path.join(LM_MODEL_DIR, 'hanzi.arpa')
        pnyin_model_file = os.path.join(LM_MODEL_DIR, 'pinyin.arpa')

        model = lm.LM(hanzi_model_file, pnyin_model_file)

        txts = ['手机性价比很高。', '吃好喝好啊', '像素很高', '相素很高', '分辨率低', '看不清楚', '反应很快', '反映很快']

        for txt in txts:
            rate = model.rate(txt)
            print(txt, rate)

    def test_lm_pinyin2hanzi(self):
        self.assertTrue(True)

        hanzi_model_file = os.path.join(LM_MODEL_DIR, 'hanzi.arpa')
        pnyin_model_file = os.path.join(LM_MODEL_DIR, 'pinyin.arpa')

        model = lm.LM(hanzi_model_file, pnyin_model_file)

        while True:
            try:
                line = input("请输入一串拼音：")
                hanzis = model.pinyin2hanzi(line.strip().split())
                print(hanzis)
            except Exception:
                pass


if __name__ == '__main__':
    unittest.main()
