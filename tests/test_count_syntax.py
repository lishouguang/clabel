# coding: utf-8

import os
import re
import unittest
from collections import Counter
from collections import defaultdict

from clabel.config import RESOURCE_DIR

from clabel.nlp.parser import default_hanlp_parser as parser
from clabel.helper import utils


class MyTestCase(unittest.TestCase):
    def test_something(self):
        self.assertEqual(True, False)

    def test_load_mobile_words(self):
        self.assertTrue(True)

        sentiments = load_sentiment_words(os.path.join(RESOURCE_DIR, 'mobile', '1正面评价词_a+.txt'))
        sentiments |= load_sentiment_words(os.path.join(RESOURCE_DIR, 'mobile', '1负面评价词_a-.txt'))

        features = load_feature_word(os.path.join(RESOURCE_DIR, 'mobile', 'mobile.ontology'))

        print(sentiments)
        print(features)
        print('sentiment words size: {}, feature words size: {}'.format(len(sentiments), len(features)))

        utils.write_file(os.path.join(RESOURCE_DIR, 'mobile', 'mobile.words'), sentiments | features)

    def test_count_syntax(self):
        self.assertTrue(True)

        sentiments = load_sentiment_words(os.path.join(RESOURCE_DIR, 'mobile', '1正面评价词_a+.txt'))
        sentiments |= load_sentiment_words(os.path.join(RESOURCE_DIR, 'mobile', '1负面评价词_a-.txt'))
        features = load_feature_word(os.path.join(RESOURCE_DIR, 'mobile', 'mobile.ontology'))

        corpus_file = os.path.join(RESOURCE_DIR, 'mobile', 'std.txt')

        ff_counter = Counter()
        oo_counter = Counter()
        fo_counter = Counter()

        ff_samples = defaultdict(set)
        oo_samples = defaultdict(set)
        fo_samples = defaultdict(set)

        i = 0
        for line in utils.iter_file(corpus_file):
            i += 1

            if i % 100 == 0:
                print(i)

            if i > 200000:
                break

            for sent in parser.parse2sents(line):
                for relation in sent.relations:
                    token1 = relation.token1.word
                    token2 = relation.token2.word

                    if token1 in features and token2 in features:
                        ff_counter.update([relation.format])
                        ff_samples[relation.format].add(str(relation))

                    if token1 in sentiments and token2 in sentiments:
                        oo_counter.update([relation.format])
                        oo_samples[relation.format].add(str(relation))

                    if token1 in sentiments and token2 in features:
                        fo_counter.update([relation.format])
                        fo_samples[relation.format].add(str(relation))

                    if token1 in features and token2 in sentiments:
                        fo_counter.update([relation.format])
                        fo_samples[relation.format].add(str(relation))

        utils.save_obj(ff_counter, os.path.join(RESOURCE_DIR, 'mobile', 'count', 'ff.counter'))
        utils.save_obj(oo_counter, os.path.join(RESOURCE_DIR, 'mobile', 'count', 'oo.counter'))
        utils.save_obj(fo_counter, os.path.join(RESOURCE_DIR, 'mobile', 'count', 'fo.counter'))

        utils.save_obj(ff_samples, os.path.join(RESOURCE_DIR, 'mobile', 'count', 'ff.dict'))
        utils.save_obj(oo_samples, os.path.join(RESOURCE_DIR, 'mobile', 'count', 'oo.dict'))
        utils.save_obj(fo_samples, os.path.join(RESOURCE_DIR, 'mobile', 'count', 'fo.dict'))

    def test_show_count(self):
        self.assertTrue(True)

        ff_counter = utils.read_obj(os.path.join(RESOURCE_DIR, 'mobile', 'count', 'ff.counter'))
        oo_counter = utils.read_obj(os.path.join(RESOURCE_DIR, 'mobile', 'count', 'oo.counter'))
        fo_counter = utils.read_obj(os.path.join(RESOURCE_DIR, 'mobile', 'count', 'fo.counter'))

        ff_dict = utils.read_obj(os.path.join(RESOURCE_DIR, 'mobile', 'count', 'ff.dict'))
        oo_dict = utils.read_obj(os.path.join(RESOURCE_DIR, 'mobile', 'count', 'oo.dict'))
        fo_dict = utils.read_obj(os.path.join(RESOURCE_DIR, 'mobile', 'count', 'fo.dict'))

        print('-' * 10 + 'ff' + '-' * 10)
        for r, c in ff_counter.most_common(20):
            print(r, c)

        print('-' * 10 + 'oo' + '-' * 10)
        for r, c in oo_counter.most_common(20):
            print(r, c)

        print('-' * 10 + 'fo' + '-' * 10)
        for r, c in fo_counter.most_common(20):
            print(r, c)

        for relation in ff_dict:
            utils.write_file(os.path.join(RESOURCE_DIR, 'mobile', 'count', 'samples', 'ff_{}.txt'.format(relation)),
                             ff_dict[relation])

        for relation in oo_dict:
            utils.write_file(os.path.join(RESOURCE_DIR, 'mobile', 'count', 'samples', 'oo_{}.txt'.format(relation)),
                             oo_dict[relation])

        for relation in fo_dict:
            utils.write_file(os.path.join(RESOURCE_DIR, 'mobile', 'count', 'samples', 'fo_{}.txt'.format(relation)),
                             fo_dict[relation])

    def test_x1(self):
        self.assertTrue(True)

        lines = []
        for i, line in enumerate(utils.iter_file(os.path.join(RESOURCE_DIR, 'mobile', 'std.txt'))):
            if i < 50000:
                lines.append(line)

        utils.write_file(os.path.join(RESOURCE_DIR, 'mobile', 'std.5w.txt'), lines)


def load_sentiment_words(file_path):
    words = set()

    for line in utils.iter_file(file_path):
        line = line.strip()
        if not line or line.startswith('----'):
            continue

        for word in line.split():
            word = word.strip()
            if not word:
                continue

            word = re.sub(r'\(\d+\)', '', word)
            words.add(word)

    return words


def load_feature_word(file_path):
    words = set()

    for line in utils.iter_file(file_path):
        line = line.strip()
        if not line:
            continue

        groups = re.findall(r'^(\S+) \S+ \S+ \S+ \[([^\[\]]*)\].*$', line)[0]
        words.add(groups[0])
        for word in groups[1].split():
            if word:
                words.add(word)

    return words


if __name__ == '__main__':
    unittest.main()
