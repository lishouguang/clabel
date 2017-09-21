# coding: utf-8

import os
import re
import jpype
import codecs

from abc import ABC
from abc import abstractmethod

from clabel.config import RESOURCE_DIR
from clabel.config import LM_MODEL_DIR
from clabel.nlp.pinyin import tag_pinyin

from clabel.helper.utils import iter_file


class LM(ABC):
    """
    Language Model
    基于BerkeleyLM实现
    """

    def __init__(self, model_file):
        JLM = jpype.JClass('com.meizu.bi.nlp.lm.LM')
        self._lm = JLM()
        self._lm.loadModel(model_file)

    @staticmethod
    def preprocess(txt):
        """
        对待计算概率的句子进行预处理，只提取出汉字、英文、数字
        :param txt:
        :return:
        """
        SYMBOL_ENG = '<eng>'
        SYMBOL_NUM = '<num>'
        SYMBOL_ENG_NUM = '<engnum>'

        tokens = re.findall(r'[a-zA-Z0-9\u4e00-\u9fa5]', txt)

        tps = tag_pinyin(''.join(tokens))

        hanzis = []
        pnyins = []
        for tp in tps:
            hanzi = tp[0]
            pnyin = tp[1]

            if re.match(r'^[a-zA-Z]+$', hanzi):
                hanzi = SYMBOL_ENG

            if re.match(r'^[0-9]+$', hanzi):
                hanzi = SYMBOL_NUM

            if re.match(r'^[a-zA-Z0-9]+$', hanzi):
                hanzi = SYMBOL_ENG_NUM

            hanzis.append(hanzi)
            pnyins.append(pnyin if pnyin else hanzi)

        return hanzis, pnyins

    @abstractmethod
    def predict_prob(self, txt):
        pass


class HanziLM(LM):

    def predict_prob(self, txt):
        hanzis, _ = LM.preprocess(txt)
        return self._lm.getProb(' '.join(hanzis))


class PinyinLM(LM):

    def predict_prob(self, txt):
        _, pnyins = LM.preprocess(txt)
        return self._lm.getProb(' '.join(pnyins))


def build_lm_train_data(raw_data_file, hanzi_data_file, pnyin_data_file):
    """
    构建Language Model训练语料
    :param raw_data_file:
    :param hanzi_data_file:
    :param pnyin_data_file:
    """
    SYMBOL_ENG = '<eng>'
    SYMBOL_NUM = '<num>'
    SYMBOL_ENG_NUM = '<engnum>'

    with codecs.open(hanzi_data_file, mode='w', encoding='utf-8') as hf,\
            codecs.open(pnyin_data_file, mode='w', encoding='utf-8') as pf:

        j = 0
        for i, line in enumerate(iter_file(raw_data_file)):
            # if i % 10000 == 0:
            #     print(i)

            if j > 24713125:
                break

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
                #     hf.write('{}\n'.format(' '.join(words)))

                if pnyins:
                    j += 1
                    if j % 10000 == 0:
                        print(j)

                    pf.write('{}\n'.format(' '.join(pnyins)))


def run_test():
    lm = LM(os.path.join(LM_MODEL_DIR, 'hanzi.arpa'))

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