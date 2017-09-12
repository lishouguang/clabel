# coding: utf-8

import os
import unittest

from clabel.pipeline import lexicon

from clabel.config import RESOURCE_DIR

from clabel.helper.utils import iter_file
from clabel.helper.utils import write_file


class MyTestCase(unittest.TestCase):
    def test_something(self):
        self.assertEqual(True, False)

    def test_create_brand(self):
        self.assertTrue(True)

        import re

        brands = set()
        for line in iter_file(os.path.join(RESOURCE_DIR, 'lexicon', 'tmp', 'brand_raw.txt')):
            words = re.sub(r'[（）/()]', '/', line).split('/')
            for word in words:
                word = word.strip()
                if word:
                    brands.add(word)

        brands = sorted(list(brands))

        write_file(os.path.join(RESOURCE_DIR, 'lexicon', 'sys', 'brand.txt'), brands)
        print(brands)

    def test_create_model(self):
        self.assertTrue(True)

        import re

        models = set()
        for line in iter_file(os.path.join(RESOURCE_DIR, 'lexicon', 'tmp', 'model_raw.txt')):
            words = re.sub(r'[（）/()]', '/', line).split('/')
            for word in words:
                word = word.strip()
                if word:
                    models.add(word)

        models = sorted(list(models))

        write_file(os.path.join(RESOURCE_DIR, 'lexicon', 'sys', 'model.txt'), models)
        print(models)

    def test_create_lexicon(self):
        self.assertTrue(True)

        pairs = [('地名_pl!.txt', 'place.txt'),
                 ('方位词_po!.txt', 'position.txt'),
                 ('日期词_de!.txt', 'date.txt'),
                 ('颜色词_co!.txt', 'color.txt')]

        for pair in pairs:
            words = []
            for line in iter_file(os.path.join(RESOURCE_DIR, 'lexicon', 'tmp', pair[0])):
                for word in line.split():
                    word = word.strip()
                    if word:
                        words.append(word)

            write_file(os.path.join(RESOURCE_DIR, 'lexicon', 'sys', pair[1]), sorted(words))

    def test_lexicon(self):
        self.assertTrue(True)

        print(lexicon.IrrelevantLexicon.is_personals('老人'))
        print(lexicon.IrrelevantLexicon.is_personals('手机'))
        print(lexicon.IrrelevantLexicon.is_irrelevant_word('note3'))

        print(lexicon.FixedSentimentLexicon.get_polar('不好'))
        print(lexicon.FixedSentimentLexicon.get_polar('不错'))

        print(lexicon.DegreeLexicon.get_head('稍'))


if __name__ == '__main__':
    unittest.main()
