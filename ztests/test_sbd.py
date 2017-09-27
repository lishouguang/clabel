# coding: utf-8

import os
import re
import time
import unittest

from sbd.config import RESOURCE_DIR
from sbd.config import APP_RESOURCE_DIR
from common.utils import iter_file
from common.utils import write_file
from sbd.sbd import SBDModel

from nlp.parser import default_parser as parser


class MyTestCase(unittest.TestCase):
    def test_something(self):
        self.assertEqual(True, False)

    def test_sbd_train(self):
        self.assertTrue(True)

        model = SBDModel(os.path.join(RESOURCE_DIR, 'mobile', 'std.min.txt'))
        model._build_ctable()
        model.train()
        model.save()

    def test_sbd(self):
        self.assertTrue(True)

        model = SBDModel.load(keras_model_file=os.path.join(APP_RESOURCE_DIR, 'sbd.keras.model'))

        while True:
            line = input('请输入一段文本：')

            stime = time.time()

            words = re.findall(r'[a-zA-Z0-9\u4e00-\u9fa5]', line)
            sent = ''.join(words)
            pline = model.predict_txt(sent)

            etime = time.time()

            print(pline, '耗时:', etime - stime)

    def test_sbd_file(self):
        self.assertTrue(True)

        model = SBDModel.load(keras_model_file=os.path.join(APP_RESOURCE_DIR, 'sbd.keras.model'))

        lines = []
        for line in iter_file(os.path.join(RESOURCE_DIR, 'tmp', 'comment.mobile.txt')):
            words = re.findall(r'[a-zA-Z0-9\u4e00-\u9fa5]', line)
            sent = ''.join(words)
            # sequence = model.predict_sequence(sent)
            pline = model.predict_txt(sent)
            lines.append('{} -> {}'.format(line, pline))
            print('{} -> {}'.format(line, pline))

        write_file(os.path.join(RESOURCE_DIR, 'tmp', 'sbd.result.txt'), lines)

    def test_sbd_eval(self):
        self.assertTrue(True)

        t = 0
        for line in iter_file(os.path.join(RESOURCE_DIR, 'tmp', 'sbd.result.txt')):
            txt1, txt2 = line.split('->')
            txt1 = txt1.strip()
            txt2 = txt2.strip()

            sents1 = parser.ssplit(txt1)
            sents2 = parser.ssplit(txt2)

            if sents1 == sents2:
                t += 1
            else:
                print(line)

        print('true:', t)


if __name__ == '__main__':
    unittest.main()
