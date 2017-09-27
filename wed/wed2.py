# coding: utf-8

import re

from nlp.pinyin import tag_pinyin
from p2h.pinyin2hanzi import p2h


def correct(txt):
    # TODO 只能纠错中文，并且是发音的错误
    # [，。？！?, ]

    corrects = []

    for sent in re.split(r'([，。？！?,])', txt):
        if re.match(r'[，。？！?,]', sent):
            corrects.append(sent)

        else:
            tps = tag_pinyin(sent)
            pinyins = ''.join([tp[1] for tp in tps])
            try:
                cc = p2h(pinyins)
                corrects.append(cc)
            except Exception as e:
                print('error:', sent)
                corrects.append(sent)

    return ''.join(corrects)


