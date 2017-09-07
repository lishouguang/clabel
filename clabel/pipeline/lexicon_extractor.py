# coding: utf-8

import os
import logging

from fastavro import reader as avro_reader

from clabel.helper import utils
from clabel.config import RESOURCE_DIR
from clabel.config import LEXICON_FEATURE_RAW
from clabel.config import LEXICON_FEATURE_REVISED

from . import clean
from . import sentence_parser
from . import double_propagation
from . import cluster
from clabel.model import word2vec as w2c

logger = logging.getLogger(__file__)


def extract(pinglun_file, O_seeds):
    """
    提取特征词/评价词
    :param pinglun_file: 评论文本
    :param O_seeds: 种子评价词
    :return:
    """
    logger.info('pipeline run...')

    base_name = os.path.basename(pinglun_file)

    clean_file = os.path.join(RESOURCE_DIR, 'clean', '%s.clean' % base_name)
    clean.clean_file(pinglun_file, clean_file)

    relation_file = os.path.join(RESOURCE_DIR, 'relation', '%s.avro' % base_name)
    sentence_parser.parse(clean_file, relation_file)

    S = get_sentences_relations(relation_file)

    F, O = double_propagation.extract(O_seeds, S)

    # utils.save_obj(F, os.path.join(RESOURCE_DIR, 'dp', 'dp.F.pruned'))
    # utils.save_obj(O, os.path.join(RESOURCE_DIR, 'dp', 'dp.O.pruned'))
    #
    # F = utils.read_obj(os.path.join(RESOURCE_DIR, 'dp', 'dp.F.pruned'))
    # O = utils.read_obj(os.path.join(RESOURCE_DIR, 'dp', 'dp.O.pruned'))

    # relation_file = os.path.join(RESOURCE_DIR, 'relation', '%s.avro' % base_name)
    # T = get_sentences_tokens(relation_file)
    # model = w2c.train(T)
    model = w2c.get()

    cf = cluster.create(F, model, preference=-30)

    write_feature_clusters(cf, LEXICON_FEATURE_RAW)

    logger.info('pipeline over.')

    return cf, O


def write_feature_clusters(cf, df):
    features = ['%s %s' % (cls, ' '.join(cf[cls])) for cls in cf]
    utils.write_file(df, features)


def get_sentences_relations(avro_file):
    """
    将评论文本进行句法分析，取得依赖关系
    :return: [[(format, token1, token2), (format, token1, token2), ...], ...]
    """
    i = 0

    with open(avro_file, 'rb') as df:
        for pinglun in avro_reader(df):
            # txt = pinglun['txt']
            for sent in pinglun['sents']:
                i += 1
                # if i < 1000:
                yield sent['relations']

    '''
    R = []
    source_dir = os.path.join(RESOURCE_DIR, 'parsed')
    i = 0
    for d in os.listdir(source_dir):
        i += 1
        print i

        R += utils.read_obj(os.path.join(source_dir, d))
        if len(R) >= 50000:
            break

    utils.save_obj(R, os.path.join(RESOURCE_DIR, 'dp', 'dp.R'))
    '''
    # R = utils.read_obj(os.path.join(RESOURCE_DIR, 'dp', 'dp.R'))
    # R = [sentence for _, parsed in R for sentence in parsed['sentences']]
    # return R


def get_sentences_tokens(avro_file):
    """
    将评论文本进行句法分析，取得分词
    :return: [[token1, token2, token3, ...], ...]
    """

    i = 0
    with open(avro_file, 'rb') as df:
        for pinglun in avro_reader(df):
            # txt = pinglun['txt']
            for sent in pinglun['sents']:
                i += 1
                # if i < 1000:
                yield [token['word'] for token in sent['tokens']]


class FormattedFeature(object):

    __instance = None

    def __init__(self, f):
        lines = utils.read_file(f)

        self._clusters = {}

        for line in lines:
            if line.startswith('='):
                continue

            features = [f for f in line.split(' ') if f.strip() != '']
            self._clusters[features[0]] = set(features)

        self.__features = set()
        for head in self._clusters:
            for feature in self._clusters[head]:
                self.__features.add(feature)

    def get_head(self, feature):
        for head in self._clusters:
            if feature in self._clusters[head]:
                return head
        return None

    def get_heads(self):
        return self._clusters.keys()

    def is_feature(self, f):
        return f in self.__features

    @staticmethod
    def get_instance():
        """
        :rtype: FormattedFeature
        """
        if FormattedFeature.__instance is None:
            FormattedFeature.__instance = FormattedFeature(LEXICON_FEATURE_REVISED)

        return FormattedFeature.__instance
