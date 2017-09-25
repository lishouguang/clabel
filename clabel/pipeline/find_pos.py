# coding: utf-8

import os
import re
from collections import Counter

from clabel.config import RESOURCE_DIR
from common import utils
from nlp.lexicon import degreeLexicon
from nlp.lexicon import irrelevantLexicon
from nlp.parser import default_parser as parser


def find_adj(corpus_file, dest_file, max_lines=200000, freq_threshold=10):
    """
    规则：在【很/太/非常】后面的词通常是形容词
    根据上述规则，对语料文本进行分词，提取出【很/太/非常】后面的词，并统计词频，词频较高的确定为形容词
    """
    counter = Counter()

    i = 0
    for line in utils.iter_file(corpus_file):
        i += 1

        if i % 100 == 0:
            print(i)

        if i > max_lines:
            break

        txt = ' '.join(parser.segment(line))

        groups = re.findall('[太很(非常)]\s(\S+)', txt)
        if groups:
            word = groups[0]

            # 过滤掉单字，单字词性往往不固定，不好确定
            # 过滤掉标点符号
            if len(word) < 2:
                continue

            # 过滤掉纯数字
            if re.match('\d+', word):
                continue

            # 过滤掉无关词
            if degreeLexicon.is_degree(word) or irrelevantLexicon.is_irrelevant_word(word):
                continue

            counter.update([word])

    lines1 = [x for x, c in counter.most_common() if c > freq_threshold]
    lines2 = ['{} {}'.format(x, c) for x, c in counter.most_common() if c > freq_threshold]
    lines3 = ['{} pos {}'.format(x, c) for x, c in counter.most_common() if c > freq_threshold]

    basename = os.path.join(os.path.dirname(dest_file), os.path.splitext(os.path.basename(dest_file))[0])
    utils.write_file(dest_file, lines1)
    utils.write_file(basename + '.2.txt', lines2)
    utils.write_file(basename + '.3.txt', lines3)

    return lines1


def run():
    corpus_file = os.path.join(RESOURCE_DIR, 'mobile', 'std.txt')
    adj_file = os.path.join(RESOURCE_DIR, 'tmp', 'adj.txt')
    find_adj(corpus_file, adj_file, freq_threshold=0)


if __name__ == '__main__':
    run()
