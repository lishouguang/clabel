# coding: utf-8

import re
import os
import logging
import itertools
import multiprocessing

from clabel.config import RESOURCE_DIR
from clabel.config import NLP_POS_SEPARATOR

from clabel.helper import utils

from gensim.models.word2vec import Word2Vec
from gensim.models.word2vec import LineSentence

logger = logging.getLogger(__file__)


class MySentences(object):

    def __init__(self, source):
        self.__source = source

    def __iter__(self):
        for line in utils.iter_file(self.__source):
            yield [tp[0] for tp in re.findall(ur'(\S+)%s(\S+)' % NLP_POS_SEPARATOR, line.decode('utf-8'))
                   if tp[1] != 'PU']


def train(sentences, model_file):
    """
    :rtype: Word2Vec
    """
    workers = multiprocessing.cpu_count()
    window = 3
    model = Word2Vec(workers=workers, window=window)

    sentences1, sentences2 = itertools.tee(sentences)

    # 构建词表
    logger.info('build vocab...')
    model.build_vocab(sentences1)

    # 训练
    logger.info('train...')
    model.train(sentences2)

    # 保存
    logger.info('save...')
    model.save(model_file)

    return model


def get(model_file):
    """
    :rtype: Word2Vec
    """
    model = Word2Vec.load(model_file)
    if isinstance(model, Word2Vec):
        return model
    return None
