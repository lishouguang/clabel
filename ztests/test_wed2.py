# coding: utf-8

import os
import re
import unittest

from clabel import config

from common.utils import iter_file
from common.utils import write_file

from nlp.parser import default_parser as parser

from wed.wed2 import correct
from wed.config import RESOURCE_DIR

from clabel.preprocessing import std


class MyTestCase(unittest.TestCase):
    def test_something(self):
        self.assertEqual(True, False)

    def test_correct(self):
        self.assertTrue(True)

        txt = '屏幕太大了，不好看。'
        txt = ''.join(re.findall(r'[\u4e00-\u9fa5，。？！?,]', txt))
        ctxt = correct(txt)
        print('txt:', txt)
        print('correct txt:', ctxt)

    def test_correct2(self):
        self.assertTrue(True)

        txts = []

        for i, line in enumerate(iter_file(os.path.join(RESOURCE_DIR, 'tmp', 'comment.mobile.tiny.txt'))):

            if i % 100 == 0:
                print(i)

            txt = std.extract_txt(line)

            sents = []
            for sent in parser.ssplit(line):

                # 提取中文、英文、数字
                sent = std.extract_txt(sent)

                if not sent:
                    continue

                '''纠错，只对中文纠错'''
                if not re.findall(r'[a-zA-Z0-9]', sent):
                    csent = std.wed(sent)
                    if sent != csent:
                        sent_prob = std.prob(sent)
                        csent_prob = std.prob(csent)

                        # 新文本的概率大于旧文本，即纠错
                        if csent_prob > sent_prob:
                            sent = csent

                sents.append(sent)

            ctxt = ''.join(sents)
            if ctxt != txt:
                txts.append('{} -> {}'.format(txt, ctxt))

        write_file(os.path.join(RESOURCE_DIR, 'tmp', 'correct.result.txt'), txts)


if __name__ == '__main__':
    unittest.main()
