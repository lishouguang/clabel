# coding: utf-8

import unittest

import os

import nltk

from clabel.config import RESOURCE_DIR
from clabel.nlp import parser as parser
from clabel.pipeline import clean
from clabel.helper import utils


class MyTestCase(unittest.TestCase):
    def test_something(self):
        self.assertEqual(True, False)

    def test_clean_txt(self):
        self.assertTrue(True)

        corpus_path = os.path.join(RESOURCE_DIR, 'standard', 'corpus')
        std_raw_path = os.path.join(corpus_path, 'std.raw.txt')
        std_path = os.path.join(corpus_path, 'std.txt')
        clean.clean_file(std_raw_path, std_path)

    def test_segment(self):
        self.assertTrue(True)

        corpus_path = os.path.join(RESOURCE_DIR, 'standard', 'corpus')
        std_raw_path = os.path.join(corpus_path, 'std.txt')
        std_token_path = os.path.join(corpus_path, 'std.token.txt')

        with open(std_token_path, 'wb') as df:
            for line in utils.iter_file(std_raw_path):
                df.write('%s\n' % ' '.join(parser.segment(line)))

    def test_split_sentence(self):
        self.assertTrue(True)

        corpus_path = os.path.join(RESOURCE_DIR, 'standard', 'corpus')
        std_token_path = os.path.join(corpus_path, 'std.token.txt')
        std_sent_path = os.path.join(corpus_path, 'std.token.sent.txt')
        with open(std_sent_path, 'wb') as df:
            for line in utils.iter_file(std_token_path):
                line = line.replace('，', '。').replace('！', '。').replace('？', '。').replace('\r', '')
                for sent in line.split('。'):
                    sent = sent.strip()
                    if sent:
                        df.write('%s\n' % sent.lower())


if __name__ == '__main__':
    unittest.main()
