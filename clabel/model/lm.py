# coding: utf-8

import os
import re
import jpype
import codecs

from clabel.config import RESOURCE_DIR
from clabel.config import LM_MODEL_DIR
from clabel.nlp.pinyin import tag_pinyin

from clabel.helper.utils import iter_file


class LM(object):
    """
    Language Model
    基于BerkeleyLM实现
    """

    def __init__(self, model_file):
        JLM = jpype.JClass('com.meizu.bi.nlp.lm.LM')
        self._lm = JLM()
        self._lm.loadModel(model_file)

    def predict_prob(self, txt):

        SYMBOL_ENG = '<eng>'
        SYMBOL_NUM = '<num>'
        SYMBOL_ENG_NUM = '<engnum>'

        txt = re.sub(r'[，。？！?,]', '', txt)

        tokens = tag_pinyin(txt)

        words = []
        for tp in tokens:
            word = tp[0]

            if re.match(r'^[a-zA-Z]+$', word):
                word = SYMBOL_ENG

            if re.match(r'^[0-9]+$', word):
                word = SYMBOL_NUM

            if re.match(r'^[a-zA-Z0-9]+$', word):
                word = SYMBOL_ENG_NUM

            words.append(word)

        return self._lm.getProb(' '.join(words))


def build_lm_train_data(raw_data_file, train_data_file):
    """
    构建Language Model训练语料
    :param raw_data_file:
    :param train_data_file:
    """
    SYMBOL_ENG = '<eng>'
    SYMBOL_NUM = '<num>'
    SYMBOL_ENG_NUM = '<engnum>'

    with codecs.open(train_data_file, mode='w', encoding='utf-8') as f:

        for i, line in enumerate(iter_file(raw_data_file)):
            if i % 10000 == 0:
                print(i)

            for sent in re.split(r'[，。？！?,]', line):

                tokens = tag_pinyin(sent)

                words = []
                pnyins = []
                for tp in tokens:
                    word = tp[0]
                    pnyin = tp[1]

                    if re.match(r'^[a-zA-Z]+$', word):
                        word = SYMBOL_ENG

                    if re.match(r'^[0-9]+$', word):
                        word = SYMBOL_NUM

                    if re.match(r'^[a-zA-Z0-9]+$', word):
                        word = SYMBOL_ENG_NUM

                    words.append(word)

                    pnyin = pnyin if pnyin else word
                    pnyins.append(pnyin)

                # if words:
                #     f.write('{}\n'.format(' '.join(words)))

                if pnyins:
                    f.write('{}\n'.format(' '.join(words)))


def run_test():
    lm = LM(os.path.join(LM_MODEL_DIR, 'zh.arpa'))

    from clabel.helper.utils import iter_file
    from clabel.helper.utils import write_file

    probs = []
    for line in iter_file(os.path.join(RESOURCE_DIR, 'tmp', 'comment.test.txt')):
        for sent in re.split(r'[，。？！?,]', line):
            words = re.findall(r'[a-zA-Z0-9\u4e00-\u9fa5]', sent)
            sent = ''.join(words)
            if sent:
                prob = lm.predict_prob(sent)
                probs.append((sent, prob))

    sort_probs = sorted(probs, key=lambda tp: tp[1])

    write_file(os.path.join(RESOURCE_DIR, 'tmp', 'result.txt'), ['{} {}'.format(p, s) for s, p in sort_probs])


if __name__ == '__main__':
    # run_test()
    build_lm_train_data(os.path.join(RESOURCE_DIR, 'mobile', 'std.txt'), os.path.join(RESOURCE_DIR, 'tmp', 'std.pinyin.txt'))
