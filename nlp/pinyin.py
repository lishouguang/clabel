# coding: utf-8

import os
import re

from collections import defaultdict, Counter

from nlp.config import APP_RESOURCE_DIR

from pypinyin import lazy_pinyin
from pypinyin.utils import simple_seg
from pypinyin.constants import RE_HANS

from common.utils import iter_file, save_obj, read_obj


def tag_pinyin(txt):
    newparts = []

    for part in simple_seg(txt):
        if RE_HANS.match(part):
            pys = lazy_pinyin(part)
            newparts += [_ for _ in zip(part, pys)]
        else:
            for p in re.split(r'([，。？！?,])', part):
                if p:
                    newparts.append((p, None))

    return newparts


class HomoModel(object):

    model_file = os.path.join(APP_RESOURCE_DIR, 'lexicon', 'homo', 'homo.pkl')

    def __init__(self, vocab_file):
        self._pinyin2chars = defaultdict(set)
        self._counter = Counter()
        self._char2pinyin = dict()

        i = 0
        for line in iter_file(vocab_file):
            i += 1
            if i % 10000 == 0:
                print(i)

            if i > 1000000:
                break

            for c, p in tag_pinyin(line):
                self._pinyin2chars[p].add(c)
                self._char2pinyin[c] = p

                self._counter.update([c])

    def pinyin2chars(self, pinyin):
        chars = [(c, self._counter.get(c)) for c in self._pinyin2chars.get(pinyin, [])]
        sorted_chars = sorted(chars, key=lambda tp: tp[1], reverse=True)
        return [c for c, _ in sorted_chars]

    def char2pinyin(self, char):
        return self._char2pinyin.get(char)

    @property
    def dictx(self):
        return self._pinyin2chars

    def save(self):
        save_obj(self, HomoModel.model_file)

    @staticmethod
    def load():
        """
        :return: HomoModel
        :rtype HomoModel
        """
        return read_obj(HomoModel.model_file)


if __name__ == '__main__':
    from nlp.config import RESOURCE_DIR
    from nlp.config import APP_RESOURCE_DIR
    model = HomoModel(os.path.join(RESOURCE_DIR, 'mobile', 'std.txt'))
    model.save()
