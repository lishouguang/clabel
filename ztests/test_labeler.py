# coding: utf-8

import os
import unittest

from collections import Counter

from clabel.config import RESOURCE_DIR
from clabel.labeler import LabelExtractor
from clabel.labeler import LexiconExtractor
from common import utils, clean
from nlp.parser import default_parser as parser


class MyTestCase(unittest.TestCase):
    def test_something(self):
        self.assertEqual(True, False)

    def test_LexiconExtractor(self):
        self.assertTrue(True)

        pinglun_file = os.path.join(RESOURCE_DIR, 'tmp', 'sbracelet', 'sbracelet.txt')
        workspace = os.path.join(RESOURCE_DIR, 'tmp', 'sbracelet')
        O_seeds = {'不错', '漂亮', '流畅', '方便', '很好', '好', '一般', '差'}

        lexicon_extractor = LexiconExtractor(workspace=workspace)
        lexicon_extractor.run(pinglun_file, O_seeds)

    def test_labelExtractor(self):
        self.assertTrue(True)

        feature_file = os.path.join(RESOURCE_DIR, 'tmp', 'sbracelet', '_result', 'features.revised')
        opinion_file = os.path.join(RESOURCE_DIR, 'tmp', 'sbracelet', '_result', 'opinions.revised')

        label_extractor = LabelExtractor(feature_file, opinion_file, sentence_prob_threshold=-10)

        txt = '之前买的另外一个手环质量就不行'
        labels = label_extractor.extract_from_txt(txt)
        print(' '.join([str(label) for label in labels]))

    def test_labelExtractor_batch(self):
        self.assertTrue(True)

        feature_file = os.path.join(RESOURCE_DIR, 'tmp', 'sbracelet', '_result', 'features.revised')
        opinion_file = os.path.join(RESOURCE_DIR, 'tmp', 'sbracelet', '_result', 'opinions.revised')

        label_extractor = LabelExtractor(feature_file, opinion_file, sentence_prob_threshold=-10)

        '''
        labels = label_extractor.extract_from_txt(txt)
        for label in labels:
            print(label)
        '''

        counter = Counter()
        results = []
        comment_file = os.path.join(RESOURCE_DIR, 'tmp', 'sbracelet', 'sbracelet.txt')
        for i, line in enumerate(utils.iter_file(comment_file)):

            print(i)

            if i > 100:
                break

            # 句法解析
            txts = clean.clean_txt2(line)
            relations = []
            for txt in txts:
                sentences = label_extractor.preprocess(txt)
                for sentence in sentences:
                    sent = parser.parse2sents(sentence)[0]
                    relation = ' '.join([str(r) for r in sent.relations])
                    relations.append(relation)

            # 提取标签
            labels = label_extractor.extract_from_txt(line)
            for label in labels:
                fo = label.feature + label.opinion
                counter.update([fo])

            # print(line, '->', labels)
            results.append(line)
            results.append('->')
            results += relations
            results.append('->')
            for label in labels:
                results.append(str(label))
            results.append('')

        utils.write_file(os.path.join(RESOURCE_DIR, 'tmp', 'sbracelet', 'labels.result.txt'), results)

        for fo, c in counter.most_common():
            print(fo, c)

    def test_label_eval(self):
        self.assertTrue(True)

        import re
        import os

        from nlp.config import RESOURCE_DIR
        from common.utils import iter_file

        total = 0
        extract = 0
        right = 0
        for line in iter_file(os.path.join(RESOURCE_DIR, 'tmp', 'labels.result.txt')):
            if not line:
                continue

            xx = re.findall(r'\[(\d) (\d) (\d)\]', line)
            if xx:
                print(xx)
                nums = xx[0]
                total += int(nums[0])
                extract += int(nums[1])
                right += int(nums[2])

        print('total: {}, extract: {}, right: {}'.format(total, extract, right))
        print('准确率:{}, 召回率:{}'.format(1.0 * right / extract, 1.0 * right / total))


if __name__ == '__main__':
    unittest.main()
