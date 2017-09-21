# coding: utf-8


import re
from pypinyin import lazy_pinyin
from pypinyin.utils import simple_seg
from pypinyin.constants import RE_HANS


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
