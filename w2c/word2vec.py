# coding: utf-8

import os
import re
import logging
import itertools
import multiprocessing

from gensim.models.word2vec import Word2Vec

from common import utils

from w2c.config import DEFAULT_MODEL_FILE
from w2c.config import WORD_POS_SEPARATOR

logger = logging.getLogger(__file__)


class MySentences(object):

    def __init__(self, source):
        self.__source = source

    def __iter__(self):
        for line in utils.iter_file(self.__source):
            yield [tp[0] for tp in re.findall(r'(\S+)%s(\S+)' % WORD_POS_SEPARATOR, line)
                   if tp[1] != 'PU']


def train(sentences, model_file):
    """
    :rtype: Word2Vec
    """
    workers = multiprocessing.cpu_count()
    window = 3
    model = Word2Vec(workers=workers, window=window, iter=100)

    sentences1, sentences2 = itertools.tee(sentences)

    # 构建词表
    logger.info('build vocab...')
    model.build_vocab(sentences1)

    # 训练
    logger.info('train...')
    model.train(sentences2, total_examples=model.corpus_count, epochs=model.iter)

    # 保存
    logger.info('save...')
    model.save(model_file)

    return model


def get(model_file=DEFAULT_MODEL_FILE):
    """
    :rtype: Word2Vec
    """
    model = Word2Vec.load(model_file)
    if isinstance(model, Word2Vec):
        return model
    return None
